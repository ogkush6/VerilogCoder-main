#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

from hardware_agent.examples.VerilogCoder.verilogcoder import VerilogCoder
from autogen import config_list_from_json
from hardware_agent.examples.VerilogCoder.verilog_examples_manager import VerilogCaseManager
import argparse
import os

"""
example command: python hardware_agent/examples/VerilogCoder/run_verilog_coder.py --generate_plan_dir 
hardware_agent/examples/VerilogCoder/verilog-eval-v2/plans/ --generate_verilog_dir hardware_agent/examples/VerilogCoder/verilog-eval-v2/plan_output/ 
--verilog_example_dir hardware_agent/examples/VerilogCoder/verilog-eval-v2/dataset_dumpall/
"""

parser = argparse.ArgumentParser(description='VerilogCoder: Autonomous Autonomous Verilog Coding Agents with Graph-based '
                                             'Planning and Abstract Syntax Tree (AST)-based Waveform Tracing Tool',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--generate_plan_dir', help="Plan directory for generated plans", default="./generated_verilog_plans/")
parser.add_argument('--generate_verilog_dir', help="Verilog directory for generated functional correct Verilog module",
                    default="./generate_verilog_dir/")
parser.add_argument('--verilog_tmp_dir', help="Temp directory for agent", default="./verilog_tool_tmp/")
parser.add_argument('--verilog_example_dir', help="Verilog question set dir", default="./verilog_eval_v2/")
args = parser.parse_args()
print(args)

# create the tmp directory for plan graph
tmp_dir = "./tmp/"
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)
    print(f"Created directory: {tmp_dir}")
else:
    print(f"Directory already exists: {tmp_dir}")

# Load verilog problem sets
# Add questions
# user_task_ids = {'vector4', 'zero'}
user_task_ids = {'zero'}
case_manager = VerilogCaseManager(file_path=args.verilog_example_dir, task_ids=user_task_ids)

# llm configurations
gpt4_config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

# llama3 settings: Used for comparison
llm_configs = {"task_planner_llm": gpt4_config_list,
               "kg_llm": gpt4_config_list,
               "graph_retrieval_llm": gpt4_config_list,
               "verilog_writing_llm": gpt4_config_list,
               "verilog_debug_llm": gpt4_config_list}

print("[Info]: VerilogCoder llm configs = ", llm_configs)

llm_types = {}
for key in llm_configs.keys():
    if "llama3" in llm_configs[key][0]["model"]:
        llm_types[key] = "llama3"
    else:
        llm_types[key] = "gpt"
print("[Info]: VerilogCoder llm types = ", llm_types)

coding_agent = VerilogCoder( task_planner_llm_config=llm_configs["task_planner_llm"],
                             kg_llm_config=llm_configs["kg_llm"],
                             graph_retrieval_llm_config=llm_configs["graph_retrieval_llm"],
                             verilog_writing_llm_config=llm_configs["verilog_writing_llm"],
                             debug_llm_config=llm_configs["verilog_debug_llm"],
                             llm_types=llm_types,
                             generate_plan_dir=args.generate_plan_dir,
                             generate_verilog_dir=args.generate_verilog_dir,
                             verilog_tmp_dir=args.verilog_tmp_dir)

pass_tasks = []
failed_tasks = []
for _ in range(case_manager.total_tasks()):
    cur_task_id = case_manager.get_cur_task_id()
    # if os.path.exists(args.generate_plan_dir + "/" + cur_task_id + "_plan.json"):
    #    plan_filename = args.generate_plan_dir + "/" + cur_task_id + "_plan.json"
    #    have_plans = True
    # else:
    plan_filename = ""
    have_plans = False
    success = coding_agent.write_Verilog_module(cur_task_id=cur_task_id,
                                                spec=case_manager.get_cur_prompt(),
                                                golden_test_bench=case_manager.get_cur_task_test(),
                                                plan_filename=plan_filename,
                                                have_plans = have_plans)
    if success:
        pass_tasks.append(cur_task_id)
    else:
        failed_tasks.append(cur_task_id)
    # Next verilog case
    case_manager.next()

print('passed tasks: ', len(pass_tasks), '\n', pass_tasks, '\n')
print('failed tasks: ', len(failed_tasks), '\n', failed_tasks, '\n')
print('success rate: ', len(pass_tasks) / case_manager.total_tasks())
