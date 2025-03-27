#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

from vcdvcd import VCDVCD, binary_string_to_hex, StreamParserCallbacks
import math
import io, re
import pandas as pd
from typing import List
import subprocess, os
from hardware_agent.examples.VerilogCoder.debug_graph_analyzer import DebugGraph

class CustomCallback(StreamParserCallbacks):
    def __init__(self, printIds={}, lines=20, offset=0):
        self._printIdx = printIds
        self._references_to_widths = {}
        self.lines = 20
        self.counter = 0
        self.offset = offset

    def enddefinitions(
            self,
            vcd,
            signals,
            cur_sig_vals
    ):
        vcd.io = io.StringIO()
        self._printIdx = self._printIdx if self._printIdx else {i: i.split('.')[-1] for i in vcd.signals}

        if signals:
            self._print_dumps_refs = signals
        else:
            self._print_dumps_refs = sorted(vcd.data[i].references[0] for i in cur_sig_vals.keys())

        for i, ref in enumerate(self._print_dumps_refs, 1):
            if i == 0:
                i = 1
            identifier_code = vcd.references_to_ids[ref]
            size = int(vcd.data[identifier_code].size)
            width = max(((size // 4)), int(math.floor(math.log10(i))) + 1)
            self._references_to_widths[ref] = width

        to_print = '// {0:<16}'.format('time')
        for ref in vcd.signals:
            string = '{0:>{1}s}'.format(self._printIdx[ref], self._references_to_widths.get(ref, 1))
            to_print += '{0:<16}'.format(string)

        print(to_print, file=vcd.io)

    def time(
            self,
            vcd,
            time,
            cur_sig_vals
    ):
        self.counter += 1

        if self.counter > self.offset + self.lines or self.counter < self.offset:
            return

        if (vcd.signal_changed):
            ss = []
            ss.append('// {0:<16}'.format(str(time) + 'ns'))
            for ref in self._printIdx:
                identifier_code = vcd.references_to_ids[ref]
                value = cur_sig_vals[identifier_code]
                string = '{0:>{1}s}'.format(
                    binary_string_to_hex(value),
                    self._references_to_widths.get(ref, 1))
                ss.append('{0:<16}'.format(string))
            print(''.join(ss), file=vcd.io)

# extract raw name from dut and ref
def get_raw_signal_name(name: str) -> str:
    if "_dut" in name:
        match = re.search("_dut", name)
        return name[:match.start()]
    elif "_ref" in name:
        match = re.search("_ref", name)
        return name[:match.start()]
    elif "_tb" in name:
        match = re.search("_tb", name)
        return name[:match.start()]
    else:
        return name

def tabular_via_callback(vcd_path, offset: int, mismatch_columns: List[str], window_size: int = 10, ori_mismatch_columns: list[str]=[]):
    vcd = VCDVCD(vcd_path, callbacks=CustomCallback(offset=offset, lines=window_size), store_tvs=False, only_sigs=False)
    tabular_text = vcd.io.getvalue()
    return tabular_text


def tabular_via_dataframe(vcd_path, offset: int, mismatch_columns: List[str], window_size: int = 5,
                          ori_mismatch_columns: list[str]=[]):
    # print('generated tabular columns = ', mismatch_columns, ' offset =', offset)
    #     from scipy.sparse import csc_matrix
    import numpy as np

    def insert_field_before_bracket(string, field):
        index = string.find('[')  # Find the index of '['
        if index != -1:  # If '[' is found
            string = string[:index] + field + string[index:]  # Insert '_ref'/_dut before '['
        else:
            string += field
        return string

    vcd = VCDVCD(vcd_path)
    n_row = vcd.endtime + 1
    n_col = len(vcd.signals)
    # fill in the waveform to the np array
    matrix = np.full((n_row, n_col), np.nan, dtype=float)
    for e, ref in enumerate(vcd.signals):
        symbol = vcd.references_to_ids[ref]
        for ts, signal in vcd.data[symbol].tv:
            try:
                matrix[ts, e] = int(signal) if signal.isdigit() else -999
            except:
                matrix[ts, e] = -999

    # Deal with the signal names including the module inside.
    # only select the signal with <signal>_ref and <signal>_dut
    transformed_signals = []
    tb_signals = []
    for signal in vcd.signals:
        signal_fields = signal.split('.')
        # print(signal_fields)
        # clk to be dropped
        if signal_fields[-1] == 'clk':
            transformed_signals.append(signal_fields[-1])
            continue
        if len(signal_fields) == 2 and signal_fields[0] == 'tb':
            transformed_signals.append(signal_fields[-1])
            # transformed_signals.append(insert_field_before_bracket(signal_fields[-1], "_tb"))
            tb_signals.append(signal_fields[-1])
        # good1 is the reference design; top_module1 is the generated design
        elif signal_fields[-2] == "top_module1":
            transformed_signals.append(insert_field_before_bracket(signal_fields[-1], "_dut"))
        # should not pull out reference waveform since the internal signal is not correct
        elif signal_fields[-2] == "good1" and signal_fields[-1] in ori_mismatch_columns:
            transformed_signals.append(insert_field_before_bracket(signal_fields[-1], "_ref"))
        else:
            transformed_signals.append(signal_fields[-2] + "_" + signal_fields[-1])
    assert(len(transformed_signals) == n_col)

    df = pd.DataFrame(matrix, columns=[i.split(".")[-1] for i in transformed_signals]).dropna(subset='clk')
    df = df.fillna(method='ffill')
    df = df.loc[:, ~df.columns.duplicated()]

    # Mark: get original output mismatch columns to make sure there is difference in the last offset line
    ori_mismatch_columns_dut = [i for i in df.columns if any( (j == get_raw_signal_name(i) and ("_dut" in i)) for j in ori_mismatch_columns)]
    ori_mismatch_columns_ref = [i for i in df.columns if any((j == get_raw_signal_name(i) and ("_ref" in i)) for j in ori_mismatch_columns)]
    ori_mismatch_columns_dut = sorted(ori_mismatch_columns_dut)
    ori_mismatch_columns_ref = sorted(ori_mismatch_columns_ref)
    # only select the <signal>_ref/<signal>_dut
    """
    mismatch_columns_tmp = []
    for i in df.columns:
        for j in mismatch_columns:
            raw_signal = get_raw_signal_name(i)
            if raw_signal in input_ports and "_tb" in input_ports:
                mismatch_columns_tmp.append(i)
            elif (j in i) and ("_dut" in i or "_ref" in i) and raw_signal not in input_ports:
                mismatch_columns_tmp.append(i)
    """
    mismatch_columns = [i for i in df.columns if any( (j in i and ("_dut" in i or "_ref" in i)) for j in mismatch_columns)]
    # print(mismatch_columns_tmp)
    # mismatch_columns = mismatch_columns_tmp
    first_row = df.loc[0: 1][mismatch_columns]
    # tail_rows = df.loc[1: offset + 1][mismatch_columns]
    # Whether to drop duplicates?
    tail_rows = df.loc[1: offset + 1][mismatch_columns].drop_duplicates(keep='first')
    # Mark: Keep 4 clock cycles
    if offset + window_size > df.shape[0]:
        future_rows = df.loc[offset + 1:][mismatch_columns]
    else:
        future_rows = df.loc[offset + 1: offset + window_size][mismatch_columns]
    # print('future row = ', future_rows.shape)
    # tail_rows = df.loc[1: offset + 1][mismatch_columns]
    # df = pd.concat([first_row, tail_rows, future_rows])[-window_size:]
    if offset > window_size:
        df = pd.concat([first_row, tail_rows])[-window_size:]
    else:
        df = pd.concat([first_row, tail_rows])
    df = df.astype(int).astype(str).applymap(lambda x: binary_string_to_hex(x) if x != -999 else 'x')

    # Mark: Add to modify the offset if needed
    print(ori_mismatch_columns_ref, ori_mismatch_columns_dut, ori_mismatch_columns)
    different_at_last = False
    for i in range(len(ori_mismatch_columns_dut)):
        s_dut = ori_mismatch_columns_dut[i]
        for s_ref in ori_mismatch_columns_ref:
            if get_raw_signal_name(s_ref) != get_raw_signal_name(s_dut):
                continue
            # print('check the last line: ', df[s_ref].iloc[-1], df[s_dut].iloc[-1])
            if df[s_ref].iloc[-1] != df[s_dut].iloc[-1]:
                # print("Find difference at the last line")
                different_at_last = True
                break
    if not different_at_last:
        df = df.drop(df.index[-1])

    # df = df.astype(int).astype(str)
    df = df.sort_index(axis=1) # sort the signal
    df.index.names = ['time(ns)']
    # Mark: compose final string, check the out_byte [7:0]
    binary_string_mismatch = {}
    for ms in mismatch_columns:
        if ms not in ori_mismatch_columns_dut and ms not in ori_mismatch_columns_ref:
           continue
        if bool(re.search('\[\d+:0\]', ms)):
            # matched_res = re.search('\[\d+:0\]', ms); change to binary
            try:
                ms_binary = ''.join(bin(int(c, 16))[2:].zfill(4) for c in df.iloc[-1][ms])
                binary_string_mismatch[ms] = ms_binary
            except:
                binary_string_mismatch[ms] = str(df.iloc[-1][ms])
                print("Failed to transform to binary ", ms, " target line: ", df.iloc[-1][ms])
        else:
            binary_string_mismatch[ms] = str(df.iloc[-1][ms])
    binary_string_mismatch = dict(sorted(binary_string_mismatch.items()))
    waveform = "### First mismatched signals time(ns) Trace ###\n" + df.to_string(header=True, index=True) + \
               "\n### First mismatched signals time(ns) End ###\n"
    #            df.loc[offset + 1:].to_string(header=True, index=True)
    if len(binary_string_mismatch) != 0:
        waveform += "The values of mismatched signals at the first mismatched signal time above:\n"
        for ms, bin_signal in binary_string_mismatch.items():
            waveform += ms + ": " + bin_signal + "\n"

    # Reference the future waveforms
    if df.shape[0] < window_size:
        print('data frame shape = ', df.shape[0], " ", window_size)
        df = pd.concat([first_row, tail_rows, future_rows])
        if df.shape[0] > window_size + 2:
            df = df[-(window_size + 2):]
        df = df.astype(int).astype(str).applymap(lambda x: binary_string_to_hex(x) if x != -999 else 'x')
        df = df.sort_index(axis=1)  # sort the signal
        df.index.names = ['time(ns)']
        waveform += "\n### Mismatched signals time(ns) Trace After the First Mismatch ###\n" + df.to_string(header=True, index=True) + \
               "\n### Mismatched signals time(ns) Trace After the First Mismatch End ###\n"
    return waveform

def parse_mismatch(test_output: str):
    mismatch = {}
    prefix = "First mismatch occurred at time"
    for line in test_output.split('\n'):
        if prefix in line:
            # signal name
            st = line.find("Output '")
            ed = line.find("' ")
            signal_name = line[st + 8:ed]

            # timestep
            st = line.find(prefix)
            mismatch_timestep = int(line[st + len(prefix):-1].strip())

            mismatch[signal_name] = mismatch_timestep

    first_mismatch_timestep = min(mismatch.values())
    return list(mismatch.keys()), first_mismatch_timestep


def get_tabular(method: str, vcd_path: str, mismatch_columns: list[str], offset:int, window_size: int=20,
                ori_mismatch_columns: list[str]=[]):
    with open(vcd_path, 'r') as f:
        waveform = f.read()
        f.close()
    # print('waveform = ', waveform)
    tmp_vcd_path = os.path.dirname(os.path.abspath(vcd_path)) + '/tmp.vcd'
    # print('tmp_vcd_path = ', tmp_vcd_path)

    with open(tmp_vcd_path, "w") as f:
        f.write(waveform)
        f.seek(0)

        gen_func = {
            'callback': tabular_via_callback,
            'dataframe': tabular_via_dataframe,
        }.get(method)
        if gen_func is None:
            raise Exception(f"get tabular do not support {method} method.")

        return gen_func(tmp_vcd_path, offset, mismatch_columns, window_size, ori_mismatch_columns)


# From Yun-Da; Probably will not use it
class WaveformTabular():

    def _run(self, vcd_path: str, test_output: str):

        def parse_mismatch(test_output: str):
            mismatch = {}
            prefix = "First mismatch occurred at time"
            for line in test_output.split('\n'):
                if prefix in line:
                    # signal name
                    st = line.find("Output '")
                    ed = line.find("' ")
                    signal_name = line[st + 8:ed]

                    # timestep
                    st = line.find(prefix)
                    mismatch_timestep = int(line[st + len(prefix):-1].strip())

                    mismatch[signal_name] = mismatch_timestep

            first_mismatch_timestep = min(mismatch.values())
            return list(mismatch.keys()), first_mismatch_timestep

        def get_tabular(method: str, vcd_path: str):
            with open(vcd_path, 'r') as f:
                waveform = f.read()
                f.close()
            # print('waveform = ', waveform)
            tmp_vcd_path = os.path.dirname(os.path.abspath(vcd_path)) + '/tmp.vcd'
            # print('tmp_vcd_path = ', tmp_vcd_path)

            with open(tmp_vcd_path, "w") as f:
                f.write(waveform)
                f.seek(0)

                mismatch_columns, offset = parse_mismatch(test_output)
                mismatch_columns.extend(["counter", "state", "done", "in", "data", "byte_r", ])
                window_size = 20

                gen_func = {
                    'callback': tabular_via_callback,
                    'dataframe': tabular_via_dataframe,
                }.get(method)
                if gen_func is None:
                    raise Exception(f"get tabular do not support {method} method.")

                return gen_func(tmp_vcd_path, offset, mismatch_columns, window_size)

        tabular = get_tabular('dataframe', vcd_path)
        return tabular

if __name__ == '__main__':
    vcd_waveanalyze = WaveformTabular()
    cmds = "vvp /home/scratch.chiatungh_nvresearch/hardware-agent-marco/verilog_tool_tmp/test.vvp".split(' ')
    print(" ".join(cmds))
    try:
        test_output = subprocess.check_output(cmds, stderr=subprocess.STDOUT)
        test_output = test_output.decode("utf-8")
        print(test_output)
    except subprocess.CalledProcessError as e:
        print('Exception')
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    debug_wave = vcd_waveanalyze._run(vcd_path="./wave.vcd",
                                      test_output=test_output)
    if isinstance(debug_wave, str):
        print(debug_wave)

