#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

# read the data
import os
from hardware_agent.examples.VerilogCoder.load_verilog_cases import load_verilog_eval_jsonl, load_verilog_eval2_cases

class VerilogCaseManager:

    def __init__(self, file_path:str, task_ids: set[str], description_file_path: str = ""):

        self.file_path = file_path
        # task = {'task_id': str, 'reference': str, 'test': test bench}
        if os.path.isfile(file_path):
            assert(description_file_path != "")
            self.verilog_cases = load_verilog_eval_jsonl(description_file=description_file_path,
                                                         jsonl_file=file_path,
                                                         task_ids=task_ids)
        elif os.path.isdir(file_path):
            self.verilog_cases = load_verilog_eval2_cases(file_dir=file_path, task_ids=task_ids)
        self.cur_task = 0

    def get_cur_task_test(self):
        '''
        return the test of current test
        '''
        print('[VerilogCaseManager] current testbench of task id= ', self.verilog_cases[self.cur_task]['task_id'])
        return self.verilog_cases[self.cur_task]['test']

    def get_cur_task_ref(self):
        '''
        return the test of current test
        '''
        print('[VerilogCaseManager] get current ref module of task id= ', self.verilog_cases[self.cur_task]['task_id'])
        return self.verilog_cases[self.cur_task]['ref']

    def get_cur_prompt(self):
        '''
        return the prompt of current case
        '''
        return self.verilog_cases[self.cur_task]['prompt']

    def get_cur_task_id(self):
        '''
        return the test of current test
        '''
        print('current test is ', self.verilog_cases[self.cur_task]['task_id'])
        return self.verilog_cases[self.cur_task]['task_id']

    def next(self):
        if self.cur_task < len(self.verilog_cases):
            self.cur_task += 1
        else:
            print("Warning: this is the last task")

    def total_tasks(self):
        return len(self.verilog_cases)
