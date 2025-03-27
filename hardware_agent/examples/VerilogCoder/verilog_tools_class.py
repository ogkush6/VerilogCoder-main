#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union, Annotated
import subprocess
import os
import re
import shutil
from hardware_agent.examples.VerilogCoder.vcd_waveform_analyzer import parse_mismatch, get_tabular
from hardware_agent.examples.VerilogCoder.debug_graph_analyzer import DebugGraph
import sys
from io import StringIO

# utilities
def check_functionality(vvp_output:str):
    lines = vvp_output.splitlines()
    mismatches = None
    for line in lines:
        if re.match("^Mismatches:", line):
            print(line)
            mismatches = int(line.split()[1])
            break
        elif re.match("^Hint: Total mismatched samples is ", line):
            print(line)
            mismatches = int(line.split()[5])
            break

    print('mismatches = ', mismatches)
    assert(mismatches is not None)
    if mismatches > 0:
        return False
    else:
        return True

def logic_checker_tool(logic_term: Annotated[str, "boolean logic"],
                       boolean_variables: Annotated[str, "boolean variables in the logic_term with space between two values"],
                       boolean_values: Annotated[str, "boolean values (0 or 1) of the boolean_variables with space between two values"]):
    vars = boolean_variables.split(' ')
    vals = boolean_values.split(' ')
    if len(vars) != len(vals):
        return "[Error]: Wrong input format! boolean variables and boolean values not match! Every boolean variable need to have a boolean value!"
    for var in vars:
        if var not in logic_term:
            return "[Error]: " + var + " is not in the logic_term: " + logic_term + "!"
    # write to a python code
    code = ""
    for i in range (len(vars)):
        code += vars[i] + "=" + vals[i] + "\n"
    result = code + "logic_term = " + logic_term + "="
    code += "print(" + logic_term + ")"
    # print(code)
    # safty check
    if 'rm' in code or 'os' in code:
        return "[Error] Only input the boolean logic, boolean variables, and boolean values!"
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    exec(code)
    sys.stdout = old_stdout

    result += str(redirected_output.getvalue())
    return "[Boolean evaluation result]\n" + result

# Verilog check function without the testbench
def sequential_flipflop_latch_identify_tool(sequential_signal_name: Annotated[str, "The sequential signal name."],
                                            time_sequence: Annotated[str, "A sequence of the time with space between two time points."],
                                            clock_waveform: Annotated[str, "A sequence of clock waveform that more than 3 clock "
                                                                           "cycles with space between two time points."],
                                            sequential_signal_waveform: Annotated[str, "A sequence of sequential signal "
                                                                                       "waveform corresponding to the clock_waveform "
                                                                                       "with space between two time points."]) -> str:

        # clock waveform check
        time_sequence = time_sequence.split()
        clock_waveform = clock_waveform.split()
        sequential_signal_waveform = sequential_signal_waveform.split()
        if len(clock_waveform) < 6 or len(sequential_signal_waveform) < 6 or len(time_sequence) < 6:
            return "[Input sequence length error]: You must input the sequence at least with 3 clock cycles!."
        if len(clock_waveform) > 20 or len(sequential_signal_waveform) > 20 or len(time_sequence) > 20:
            return "[Input sequence length error]: The input sequence length is larger than 20. Input at most 20 time points in the sequence."
        # print("clock waveform = ", clock_waveform)
        # print("sequential waveform = ", sequential_signal_waveform)
        if len(clock_waveform) != len(sequential_signal_waveform):
            return "[Input sequence length error]: The clock waveform sequence length (length=" + str(len(clock_waveform)) + ") is different than the " \
                   "sequential element waveform length (length= " + str(len(sequential_signal_waveform)) + "). The signal sequence must match to the clock sequence time points."
        checked_length = min(len(sequential_signal_waveform), len(clock_waveform))

        # check edge trigger and d latch
        posedge_transition = False
        negedge_transition = False
        active_high_transition = False
        active_low_transition = False

        for t in range(checked_length - 1):
            if sequential_signal_waveform[t] == sequential_signal_waveform[t+1]:
                continue
            # print("clock t:", clock_waveform[t], " clock t+1:", clock_waveform[t+1])
            # print("signal t:", sequential_signal_waveform[t], " signal t+1:", sequential_signal_waveform[t + 1], "\n")
            if clock_waveform[t] == "0" and clock_waveform[t+1] == "1":
                posedge_transition = True
            if clock_waveform[t] == "1" and clock_waveform[t+1] == "0":
                negedge_transition = True
            if clock_waveform[t] == "1" and clock_waveform[t+1] == "1":
                active_high_transition = True
            if clock_waveform[t] == "0" and clock_waveform[t+1] == "0":
                active_low_transition = True
        # print("posedge=",posedge_transition,"\nnegedge=",negedge_transition,
        #  "\nactive high=", active_high_transition, "\nactive low=", active_low_transition)
        # identify element
        if posedge_transition and not negedge_transition and not active_high_transition and not active_low_transition:
            return "[Info]" + sequential_signal_name + " is a posedge triggered flip-flop.\n"
        if negedge_transition and not posedge_transition and not active_high_transition and not active_low_transition:
            return "[Info]" + sequential_signal_name + " is a negedge triggered flip-flop.\n"
        if active_high_transition and not active_low_transition and not negedge_transition:
            return "[Info]" + sequential_signal_name + " is a active high (clock is 1) latch.\n"
        if active_low_transition and not active_high_transition and not posedge_transition:
            return "[Info]" + sequential_signal_name + " is a active low (clock is 0) latch.\n"

        return "[Information]: Can not determine the " + sequential_signal_name \
               + " is flip-flop, latch, or combinational logic.\nYou can do the following:\n" \
                 "1. Input a longer sequence to sequential_flipflop_latch_identify_tool again\n" \
                 "2. The " + sequential_signal_name + " is not a sequential logic."

# Verilog Toolkits for path variables
class VerilogToolKits:

    def __init__(self, workdir: str="./verilog_tool_tmp/"):
        self.test_bench = ""
        # working dir
        self.workdir = workdir
        self.verilog_file_path =  self.workdir + "/test.sv"
        self.test_vpp_file_path = self.workdir + "/test.vpp"
        self.wave_vcd_file_path = self.workdir + "/wave.vcd"
        self.completed_verilog_file_path = self.workdir + "/test.v"
        # temp data
        self.cur_graph_verilog = "" # used to update the AST graph_tracer
        self.completed_verilog = ""
        self.spec = "" # store the spec
        self.graph_tracer = None

    def get_work_paths(self):
        return {'workdir': self.workdir,
                'verilog': self.completed_verilog_file_path,
                'test_sv': self.verilog_file_path,
                'wave': self.wave_vcd_file_path}

    def reset(self):
        self.test_bench = ""
        self.spec = ""
        self.cur_graph_verilog = ""
        self.completed_verilog = ""
        self.graph_tracer = None

    def load_test_bench(self, task_id: str, spec: str, test_bench:str, write_file: bool=False):
        self.spec = spec
        self.test_bench = test_bench
        assert(self.test_bench != "")
        if not write_file:
            return
        test_bench_filename = task_id + ".sv"
        with open(self.workdir + "/" + test_bench_filename, 'w') as f:
            f.write(self.test_bench)
        f.close()

    def write_verilog_file(self, task_id: str, num: int=0, output_dir: str=None):
        generated_module = task_id + "_" + str(num) + ".v"
        if output_dir is None:
            output_dir = self.workdir
        with open(output_dir + "./" + generated_module, 'w') as f:
            f.write(self.completed_verilog)
        f.close()

        generated_test_file = task_id + "_" + str(num) + ".sv"
        with open(output_dir + "./" + generated_test_file, 'w') as f:
            f.write(self.test_bench + "\n" + self.completed_verilog)
        f.close()
        return generated_module, generated_test_file

    # call by agent
    def recall_spec_and_generated_verilog_code_tool(self):
        if self.spec == "":
            return "Error: no case for solving now!\nThought: I should load the case for agent to solve firstly!"
        if self.completed_verilog == "":
            return "Error: no generated verilog code!\nThought: I should generate the verilog module code first!"
        observation_str = "[Module Spec]:\n" + self.spec + "\n\n[Current Implemented Verilog Module]:\n" \
                          + self.completed_verilog
        hint = "Instruct: Let's think step by step. Identify the difference of [Module Spec] and [Current Implemented Verilog Module]" \
               "Then, make a plan to modify the implemented verilog module to meet Module Spec."

        return observation_str + "\n\n" + hint

    # syntax check tool
    def verilog_syntax_check_tool(self, completed_verilog: Annotated[str, "The completed verilog module code implementation"]) -> str:
        print('running syntax check ', self.workdir)
        # initialize the pathes
        assert(self.test_bench != "")
        
        if "endmodule" not in completed_verilog:
            example_verilog_code = completed_verilog + " endmodule"
            return "[Error] the module is not completed! You need to write the Verilog module code with `module` in the beginning and `endmodule` in the end!\nBelow is the example:\n```verilog\n" + example_verilog_code + "\n```"
        
        num_tb_lines = len(self.test_bench.splitlines())
        completed_verilog = completed_verilog.strip()
        verilog_file = self.test_bench + "\n" + completed_verilog
        self.completed_verilog = completed_verilog  # record the latest verilog result

        with open(self.verilog_file_path, 'w') as f:
            f.write(verilog_file)
        f.close()

        # Mark: write out to construct the control graph
        with open(self.completed_verilog_file_path, 'w') as f:
            f.write(completed_verilog)
        f.close()

        cmds = (
                    "iverilog -Wall -Winfloop -Wno-timescale -g2012 -s tb -o " + self.test_vpp_file_path + " " + self.verilog_file_path).split(
            ' ')

        print(" ".join(cmds))
        try:
            outputs = subprocess.check_output(cmds, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # print('Exception return with error (code {}): {})'.format(e.returncode, e.output))
            outputs = e.output

        outputs = outputs.decode("utf-8").splitlines()
        print(outputs)
        # Compile failed
        if len(outputs) != 0:
            # compile error parameters
            error_line_window = 5
            compiled_error = {}
            error_msg = ""

            for content in outputs:
                if not re.search('sv\:[\d+]', content):
                    error_msg += content + "\n"
                    continue
                tmp = content.split(':')
                m_error_line = int(tmp[1]) - 1
                # if m_error_line < num_tb_lines:
                # skip
                # m_error_line = 0
                # compiled_error[m_error_line] = " ".join(str(x) for x in tmp[2:])
                if m_error_line > num_tb_lines:
                    # m_error_line = m_error_line - num_tb_lines
                    compiled_error[m_error_line] = " ".join(str(x) for x in tmp[2:])
                else:
                    error_msg += content + "\n"
            print('compiled error = ', compiled_error)
            # comment the wrong lines
            # commented_module = completed_verilog.splitlines()
            commented_module = verilog_file.splitlines()
            module_error_msg = ""
            error_cnt = 0
            for m_error_line in compiled_error:
                error_cnt += 1
                commented_module[m_error_line] = commented_module[m_error_line] + " ## Error line: " + compiled_error[
                    m_error_line] + " ## "

                # Deal with previous k lines
                pre_lines = m_error_line - error_line_window
                if pre_lines < 0:
                    pre_lines = 0
                module_error_msg += "## Compiled Error Section " + str(error_cnt) + " Begin ##\n\n"
                for l in range(pre_lines, m_error_line + 1):
                    module_error_msg += commented_module[l] + "\n"
                # module_error_msg += commented_module[m_error_line] + "\n"
                # Deal with after k lines
                pre_lines = m_error_line + error_line_window
                if pre_lines > len(commented_module) - 1:
                    pre_lines = len(commented_module) - 1
                for l in range(m_error_line + 1, pre_lines):
                    module_error_msg += commented_module[l] + "\n"
                module_error_msg += "\n## Compiled Error Section " + str(error_cnt) + " End ##\n\n"

            # commented_module = '\n'.join(str(x) for x in commented_module)  + "\n\n" +  error_msg
            module_error_msg += error_msg
            # print("commented_module = ", commented_module)
            return "[Compiled Failed Report]\n" + module_error_msg

        return "[Compiled Success Verilog Module]:\n```verilog\n" + self.completed_verilog + "\n```"


    # call by agent
    def verilog_simulation_tool(self, completed_verilog: Annotated[str, "The completed verilog module code implementation"]) -> str:
        print('running simulation tool in ', self.workdir)
        # initialize the pathes
        assert(self.test_bench != "")
        
        if "endmodule" not in completed_verilog:
            example_verilog_code = completed_verilog + " endmodule"
            return "[Error] the module is not completed! You need to write the Verilog module code with `module` in the beginning and `endmodule` in the end!\nBelow is the example:\n```verilog\n" + example_verilog_code + "\n```"
        
        num_tb_lines = len(self.test_bench.splitlines())
        completed_verilog = completed_verilog.strip()
        verilog_file = self.test_bench + "\n" + completed_verilog
        self.completed_verilog = completed_verilog  # record the latest verilog result

        with open(self.verilog_file_path, 'w') as f:
            f.write(verilog_file)
        f.close()

        # Mark: write out to construct the control graph
        with open(self.completed_verilog_file_path, 'w') as f:
            f.write(completed_verilog)
        f.close()

        cmds = (
                    "iverilog -Wall -Winfloop -Wno-timescale -g2012 -s tb -o " + self.test_vpp_file_path + " " + self.verilog_file_path).split(
            ' ')

        print(" ".join(cmds))
        try:
            outputs = subprocess.check_output(cmds, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # print('Exception return with error (code {}): {})'.format(e.returncode, e.output))
            outputs = e.output

        outputs = outputs.decode("utf-8").splitlines()
        print(outputs)
        # Compile failed
        if len(outputs) != 0:
            # compile error parameters
            error_line_window = 5
            compiled_error = {}
            error_msg = ""

            for content in outputs:
                if not re.search('sv\:[\d+]', content):
                    error_msg += content + "\n"
                    continue
                tmp = content.split(':')
                m_error_line = int(tmp[1])
                # if m_error_line < num_tb_lines:
                # skip
                # m_error_line = 0
                # compiled_error[m_error_line] = " ".join(str(x) for x in tmp[2:])
                if m_error_line > num_tb_lines:
                    # m_error_line = m_error_line - num_tb_lines
                    compiled_error[m_error_line] = " ".join(str(x) for x in tmp[2:])
                else:
                    error_msg += content + "\n"
            print('compiled error = ', compiled_error)
            # comment the wrong lines
            # commented_module = completed_verilog.splitlines()
            commented_module = verilog_file.splitlines()
            module_error_msg = ""
            error_cnt = 0
            for m_error_line in compiled_error:
                error_cnt += 1
                commented_module[m_error_line] = commented_module[m_error_line] + " ## Error line: " + compiled_error[
                    m_error_line] + " ## "

                # Deal with previous k lines
                pre_lines = m_error_line - error_line_window
                if pre_lines < 0:
                    pre_lines = 0
                module_error_msg += "## Compiled Error Section " + str(error_cnt) + " Begin ##\n\n"
                for l in range(pre_lines, m_error_line + 1):
                    module_error_msg += commented_module[l] + "\n"
                # module_error_msg += commented_module[m_error_line] + "\n"
                # Deal with after k lines
                pre_lines = m_error_line + error_line_window
                if pre_lines > len(commented_module) - 1:
                    pre_lines = len(commented_module) - 1
                for l in range(m_error_line + 1, pre_lines):
                    module_error_msg += commented_module[l] + "\n"
                module_error_msg += "\n## Compiled Error Section " + str(error_cnt) + " End ##\n\n"

            # commented_module = '\n'.join(str(x) for x in commented_module)  + "\n\n" +  error_msg
            module_error_msg += error_msg
            # print("commented_module = ", commented_module)
            return "[Compiled Failed Report]\n" + module_error_msg

        # simulation
        if os.path.exists(self.wave_vcd_file_path):
            os.remove(self.wave_vcd_file_path)
        cmds = ("vvp " + self.test_vpp_file_path).split(' ')
        print(" ".join(cmds))
        outputs = subprocess.check_output(cmds, stderr=subprocess.DEVNULL).decode("utf-8")

        if os.path.exists(os.getcwd() + "/wave.vcd"):
            shutil.move(os.getcwd() + "/wave.vcd", self.wave_vcd_file_path)

        if check_functionality(outputs):
            return "[Compiled Success]\n[Function Check Success]\n" + outputs
        else:
            return "[Compiled Success]\n[Function Check Failed]\n==Tool Output==\n" + outputs + \
                   "==Tool Output End==\n\nThought: input above tool output into waveform_trace_tool as `function_check_output` to debug the failed signals starts with trace_level=2!"

    def get_input_ports(self, module_content: str):

        module_content = module_content.splitlines()
        input_ports = []
        for line in module_content:
            line = line.strip()
            if 'input' not in line:
                continue
            line = line.replace(",", " ")
            contents = line.split()
            for i in range(len(contents)):
                cur_text = contents[i]
                i += 1
                if cur_text == "//":
                    break
                if cur_text == 'input':
                    while contents[i] == 'logic' or not re.match(r'^[a-zA-Z]', contents[i]):
                        i += 1
                    input_ports.append(contents[i])
        return input_ports

    def waveform_trace_tool(self, function_check_output: Annotated[str, "The output string of function "
                                                              "check from verilog_simulation_tool."],
        trace_level: Annotated[int, "The number of level for wrong signal waveform tracing. "
                                                    "It should be larger than 1."]) -> str:
        if not os.path.exists(self.wave_vcd_file_path):
            return "[Error] wave.vcd is not found! Please complete the verilog code and run the verilog_simulation_tool " \
                   "first!"
        if not os.path.exists(self.completed_verilog_file_path):
            return "[Error] test.v is not found! Please complete the verilog code and run the verilog_simulation_tool " \
                   "first!"
        # 1. construct debug tracer
        if self.cur_graph_verilog != self.completed_verilog:
            # if the verilog file are not the same; reconstruct the graph
            print("Creating new AST tree graph...")
            self.graph_tracer = DebugGraph([self.completed_verilog_file_path])

        print("Get mismatched signal...")
        # 2. get mismatched signal first
        if check_functionality(function_check_output):
            print("No mismatched signals")
            return "[Waveform Tracer]: No mismatched signals!"
        mismatch_columns, offset = parse_mismatch(test_output=function_check_output)

        # 3. trace more signals
        print("Trace graph signal...")
        traced_signals_map, signal_level_tracer = self.graph_tracer.get_k_control_signals(target_signals=mismatch_columns,
                                                                                          k=trace_level,
                                                                                          signal_only=True)

        traced_signal_str = "[Signal Traces] Backtrace control signal relations.\n"
        for bt in range(len(signal_level_tracer) - 1, -1, -1):
            if bt == len(signal_level_tracer) - 1:
                for signal_rel in signal_level_tracer[bt]:
                    traced_signal_str += signal_rel + "\n"

            header_space = "-" * (len(signal_level_tracer) - 1 - bt)
            for signal_rel in signal_level_tracer[bt]:
                traced_signal_str += header_space + signal_rel
                if bt == 0:
                    traced_signal_str += " (*last output port level)"
                traced_signal_str += "\n"
        traced_signal_str += "\n"

        # get the waveform tbl str
        all_traced_signals = [str(k) for k in traced_signals_map.keys()]

        # add the input ports to trace
        input_ports = self.get_input_ports(self.completed_verilog)
        # print("input = ", input_ports)
        for input in input_ports:
            mismatch_columns.append(input)
            if input in all_traced_signals:
                continue
            all_traced_signals.append(input)

        # print("all traced signals = ", all_traced_signals)
        print("Get table waveform...")
        waveform_table_str = get_tabular(method='dataframe', vcd_path=self.wave_vcd_file_path,
                                         mismatch_columns=all_traced_signals,
                                         offset=offset,
                                         ori_mismatch_columns=mismatch_columns)

        waveform_table_str = "[Siganl Waveform]: <signal>_tb is the given testbench signal and can not be changed! <signal>_ref is the golden, and <signal>_dut is the generated verilog file waveform. Check " \
                             "the mismatched signal waveform and its traced signals. The clock cycle (clk) is 10ns and toggles every 5ns. \n'-' means unknown during simulation. " \
                             "If the '-' is the reason of mismatched signal, please check the reset and assignment block.\n" + \
                             "[Testbench Input Port Signal to Module]: " + ', '.join(input_ports) + \
                             "\n[Traced Signals]: " + ', '.join(all_traced_signals) + "\n[Table Waveform in hexadecimal format]\n" + waveform_table_str
        # 4: get the corresponding verilog code snippets, Todo: Make it another function
        logic_trace_windows = 6
        full_module = True

        with open(self.completed_verilog_file_path, 'r') as f:
            verilog_lines = f.readlines()
        f.close()
        if full_module:
            logic_str = "[Verilog of DUT]:\n```verilog\n" + ''.join(verilog_lines) + "\n```\n"
        else:
            logic_str = "[Generated Verilog Logic Trace]\nMismatched dut Signals:"
            for wrong_signal in mismatch_columns:
                logic_str += " " + wrong_signal
            logic_str += "\nLogics assignments of the Mismatched DUT Signals: ["
            for ms in mismatch_columns:
                logic_str += ms + " "
            logic_str += "]\n"

            verilog_line_record = set()
            for k, v in traced_signals_map.items():
                # print(k, v)
                if k in mismatch_columns:
                    line_str = "functional error signal <" + k + "> from lines " + str(v[0]) + " to " + str(v[1])
                else:
                    line_str = "control signal of functional error signals from lines " + str(v[0]) + " to " + str(v[1])
                if "lines " + str(v[0]) + " to " + str(v[1]) in verilog_line_record:
                    continue

                logic_str += line_str + ":\n"
                verilog_line_record.add("lines " + str(v[0]) + " to " + str(v[1]))
                min_line = v[0] - logic_trace_windows if v[0] - logic_trace_windows >= 0 else 0
                max_line = v[1] + logic_trace_windows if v[1] + logic_trace_windows < len(verilog_lines) else len(
                    verilog_lines)
                for line in range(min_line, max_line):
                    logic_str += verilog_lines[line - 1]
                logic_str += "\n"
        # Todo: clock cycle might not be needed; Need to automate it
        # HINT = "\n\n[Hint] Firstly, identify the time of mismatched signals with the consideration of the clk, which toggles every 5ns. " \
        #       "Then, explain the related signals and their transistions in the waveform table. " \
        #       "If the information is not enough for correct the functional error, " \
        #       "try to trace more relevant signals using trace_level >"
        HINT = "\n\n[Note] You can not change the [testbench input signal]: (" + ', '.join(input_ports) + ")! Modify the module implementation considering the input signals."\
               "\n[Hint] Firstly, identify the time of mismatched signals, and only focus on the mistmatched signals in the waveform firstly." \
               "Then, explain the related signals and their transitions in the waveform table. Don't correct signals without mismatch in the table waveforms." \
               "If the information is not enough for correct the functional error, " \
               "try to trace more relevant signals using trace_level >" + str(trace_level) + " for waveform_trace_tool."

        # less than 5ns
        if offset <= 5:
            HINT += "\n\n[Debug report]: The mismatch happened at the beginning. Check and set the correct initial value for mismatched signal.\n" \
                    + "### Example of initialize the signal to 0 ###\n\n" + "logic [3:0] a;\ninitial\n  a=4'b0000;\n\n" + "### End example ###"

        return (    logic_str + waveform_table_str + HINT +
                    "\n\nThought: If you know how to correct the functional error, start to correct the "
                    "code and run verilog_simulation_tool again.")

if __name__ == '__main__':
    # print(logic_checker_tool(logic_term="(A & B & ~C)",
    #                         boolean_variables="A B C",
    #                         boolean_values="1 1 0"))
    # print(sequential_flipflop_latch_identify_tool(sequential_signal_name="p",
    #                                        clock_waveform="0 0 0 0 0 1 1 1 1 1 1 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0 1 1 1 1 1 0 0 0 0",
    #                                        sequential_signal_waveform="x x x x x 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 1 1 1 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0"))
    # exit(1)
    # define the tools # Test Prob149
    verilog_tools = VerilogToolKits()
    paths = verilog_tools.get_work_paths()
    with open("/home/scratch.chiatungh_nvresearch/hardware-agent-marco/verilog_tool_tmp1/dff8.sv", 'r') as f:
        test_benchmark = f.read()
    f.close()
    verilog_tools.load_test_bench(task_id="fsm2", spec="", test_bench=test_benchmark)
    # print(verilog_simulation_tool(completed_verilog=completed_verilog_syntax_error))
    # output = verilog_simulation_tool(completed_verilog=completed_verilog_function_error)
    with open("/home/scratch.chiatungh_nvresearch/hardware-agent-marco/verilog_tool_tmp1/dff8_0.v", 'r') as f:
        completed_verilog_code = f.read()
    f.close()
    output = verilog_tools.verilog_simulation_tool(completed_verilog=completed_verilog_code)
    print(output)
    print(verilog_tools.waveform_trace_tool(function_check_output=output, trace_level=2))
