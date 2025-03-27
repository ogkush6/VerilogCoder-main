#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

import json
import re
import matplotlib.pyplot as plt
import os

# Unsolved problem set
unsolved_fsm_tasks = ['review2015_fsmonehot', '2014_q3fsm', 'm2014_q6', 'fsm_serial', '2013_q2bfsm', 'fsm_hdlc',
                     'fsm_serialdata', 'kmap2', 'ece241_2013_q4', 'ece241_2013_q3', 'ece241_2014_q4', 'ece241_2013_q2']
unsolved_tasks = ['kmap3', 'dff8', 'm2014_q4d', 'bugs_mux2', 'lfsr32', 'lfsr5', '2012_q2b', 'm2014_q6c', 'mt2015_muxdiff',
                  'rule110', '2014_q3c', 'count_clock', 'circuit8', 'circuit10', 'review2015_fsm', 'gshare', 'lemmings4',
                  'review2015_fancytimer', 'edgedetect2']


def list_files_in_directory(directory):
    try:
        # List all files in the given directory
        files = os.listdir(directory)

        # Filter out directories, only keep files
        files = [f for f in files if os.path.isfile(os.path.join(directory, f))]

        return files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def modify_test_dumpvar_all(test_str: str):
    lines = test_str.splitlines()
    for l in range(len(lines)):
        match = re.search("dumpvar", lines[l])
        if match:
    #        print('ori: ', lines[l])
            end_index = match.end()
            lines[l] = lines[l][:end_index + 1] + "();\n"
    #         print(lines[l])
    content = '\n'.join(lines)
    return content

# verilog_eval jsonl
def load_verilog_eval_jsonl(description_file: str, jsonl_file:str, task_ids: set[str]=set(), verbose_level: int=0):
    '''
    description_file: description of the problem. Used for the prompt
    jsonl_file: humaneval jsonl file. VerilogEval_Machine.jsonl, VerilogEval_Human.jsonl
    task_ids: A list of task_ids to select
    verbose_level: control the print information
    '''
    all_task_ids = []
    task_map = {}
    with open(description_file, 'r') as f:
        jsonl_content = f.read()
    descriptions = [json.loads(jline) for jline in jsonl_content.splitlines()]

    with open(jsonl_file, 'r') as f:
        jsonl_content = f.read()
    result = [json.loads(jline) for jline in jsonl_content.splitlines()]
    data_tbl = []
    for content in result:
        if content['task_id'] not in task_ids and len(task_ids) > 0:
            continue
        dumpall_var_test = modify_test_dumpvar_all(content['test'])
        # replace top_module to TopModule
        content['prompt'] = content['prompt'].replace("top_module", "TopModule")
        dumpall_var_test = dumpall_var_test.replace("top_module ", "TopModule ")

        data_tbl.append({'task_id': content['task_id'],
                         'ref': content['prompt'] + "\n" + content['canonical_solution'],
                         'prompt': content['prompt'],
                         'test': dumpall_var_test})

        task_id = content['task_id']
        if task_id not in task_map:
            task_map[task_id] = len(data_tbl) - 1
            all_task_ids.append(task_id)
        if verbose_level > 2:
            for key in content:
                print(key, ":\n", content[key])
    # Deal with the description
    for content in descriptions:
        if content['task_id'] not in task_ids:
            continue
        task_id = content['task_id']
        assert(task_id in task_map)
        # replace top_module to TopModule
        content['detail_description'] = content['detail_description'].replace("top_module ", "TopModule ")

        data_tbl[task_map[task_id]]['prompt'] = content["detail_description"] + "\n[Module Definition]:\n" + \
                                                data_tbl[task_map[task_id]]['prompt']

    # verbose level
    # print("loaded {} example:".format(len(data_tbl)))
    # for task in data_tbl:
    #    print(task['task_id'])
    #    for key in task:
    #         print(key, ":", task[key])
    #    # print(task['test'])
    print('num tasks = ', len(all_task_ids))
    return data_tbl

# verilog_eval 2
def load_verilog_eval2_cases(file_dir: str, task_ids: set[str]=set(), verbose_level: int=0):
    '''
    file_dir: verilog_eval2 problem prompt dir
    task_ids: A list of task_ids to select
    verbose_level: control the print information
    '''

    files = list_files_in_directory(file_dir)
    if len(files) == 0:
        print("Error! There is no files in for loading verilog cases under ", file_dir)
        exit(1)

    task_map = {}
    data_tbl = []
    for file in files:
        file_name_fields = file.split('.')
        # file_type = file_name_fields[-1]
        problem_fields = file_name_fields[0].split('_')
        task_id = '_'.join(problem_fields[1:-1])
        content_type = problem_fields[-1]
        if task_id not in task_ids:
            continue
        print('reading ', file_dir, file)
        with open(file_dir + "/" + file, 'r') as f:
            text = f.read()
        f.close()
        if task_id not in task_map:
            data_tbl.append({'task_id': task_id})
            task_map[task_id] = len(data_tbl) - 1
        data_tbl[task_map[task_id]][content_type] = text

    # combine the ref to test for running iverilog
    for task in data_tbl:
        task['test'] = task['test'] + "\n" + task['ref']
        # for key in task:
        #     print(key, ":", task[key])
    # for key in data_tbl[0]:
        # print(key)
    # print(list(all_task_id))
    return data_tbl

def get_taskids(files: list[str], task_ids: set[str], is_completed: bool=False):
    for file in files:
        file_name_fields = file.split('.')
        # file_type = file_name_fields[-1]
        problem_fields = file_name_fields[0].split('_')
        if is_completed:
            task_id = '_'.join(problem_fields[0:-1])
        else:
            task_id = '_'.join(problem_fields[1:-1])
        if task_id == '':
            print("Empty task ", file)
            continue
        if task_id not in task_ids:
            task_ids.add(task_id)
    return task_ids

# check completed verilogs function
def check_completed_verilog_case(data_set_file_dir: str, completed_file_dir: str):

    files = list_files_in_directory(data_set_file_dir)
    completed_files = list_files_in_directory(completed_file_dir)
    if len(files) == 0:
        print("Error! There is no files in for loading verilog cases under ", file_dir)
        exit(1)
    user_task_ids = []

    complicated_task_ids = {"dff8", "edgedetect2", "m2014_q4d", "kmap2", "bugs_mux2", "ece241_2013_q2", "ece241_2014_q4",
                     "lfsr32",
                     "lfsr5", "2012_q2b", "ece241_2014_q3", "m2014_q6c", "mt2015_muxdiff", "2012_q1g", "m2014_q3",
                     "rule110",
                     "kmap3", "mt2015_q4", "2014_q3fsm", "2014_q3c", "m2014_q6", "fsm_serial", "2013_q2bfsm",
                     "fsm_hdlc",
                     "count_clock", "circuit8", "fsm_serialdata", "circuit10", "review2015_fsm", "gshare", "lemmings4",
                     "review2015_fancytimer"}
    all_task_ids = set()
    completed_task_ids = set()
    all_task_ids = get_taskids(files, all_task_ids)
    completed_task_ids = get_taskids(completed_files, completed_task_ids, is_completed=True)
    print("number of all task ids = ", len(all_task_ids))
    print("number of completed task ids = ", len(completed_task_ids))
    incomplete_easy_task_ids = []
    incomplete_hard_task_ids = []
    incomplete_task_ids = []
    for task_id in all_task_ids:
        if task_id in completed_task_ids or task_id in user_task_ids:
            continue
        incomplete_task_ids.append(task_id)
        if task_id not in complicated_task_ids:
            incomplete_easy_task_ids.append(task_id)
        else:
            incomplete_hard_task_ids.append(task_id)

    print("incompleted easy task ids: ", incomplete_easy_task_ids)
    print("\nincompleted hard task ids: ", incomplete_hard_task_ids)

    incomplete_task_ids = sorted(incomplete_task_ids)
    print("\nincompleted task ids: ", incomplete_task_ids)
    return incomplete_task_ids

def get_union_incompleted_cases(data_set_file_dir: str, completed_file_dirs: list[str]):
    Union_incomplete_task_ids = []
    for completed_file_dir in completed_file_dirs:
        incomplete_task_ids = check_completed_verilog_case(data_set_file_dir=data_set_file_dir, completed_file_dir=completed_file_dir)
        for task_id in incomplete_task_ids:
            if task_id not in Union_incomplete_task_ids:
                Union_incomplete_task_ids.append(task_id)
    print("Union incompleted ids:")
    for task_id in Union_incomplete_task_ids:
        print(task_id)

if __name__ == '__main__':
    # completed_file_dirs = ["hardware_agent/examples/verilog_testcases/verilog-eval-v2/plan_output_nowaveform_tool/",
    #                       "hardware_agent/examples/verilog_testcases/verilog-eval-v2/plan_output/",
    #                       "hardware_agent/examples/verilog_testcases/verilog-eval-v2/plan_output_internal_planner/",
    #                       "hardware_agent/examples/verilog_testcases/verilog-eval-v2/plan_output_internal_planner_nowaveform_tool/"]
    #get_union_incompleted_cases(data_set_file_dir="hardware_agent/examples/verilog_testcases/verilog-eval-v2/dataset_dumpall/",
    #                            completed_file_dirs=completed_file_dirs)
    check_completed_verilog_case(data_set_file_dir="hardware_agent/examples/verilog_testcases/verilog-eval-v2/dataset_dumpall/",
                                 completed_file_dir="hardware_agent/examples/verilog_testcases/verilog-eval-v2/plan_output/")
    load_verilog_eval2_cases(file_dir="hardware_agent/examples/verilog_testcases/verilog-eval-v2/dataset_dumpall/",
                             task_ids=set(['vector0']))
    print("Machine eval original:")
    load_verilog_eval_jsonl(description_file="hardware_agent/examples/verilog_testcases/VerilogDescription_Machine.jsonl",
                            jsonl_file="hardware_agent/examples/verilog_testcases/VerilogEval_Machine.jsonl",
                            task_ids=set([]))
