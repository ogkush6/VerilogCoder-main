#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

import os
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union, Annotated
from hardware_agent.tools_utility import get_tools_descriptions, create_tool_tbl
from autogen.coding import DockerCommandLineCodeExecutor, LocalCommandLineCodeExecutor

def get_plan_graph_retrieval_agent_config(config_list: Dict[str, Any], opensource_model=False):
    if opensource_model:
        assistance_agent = "OS_AssistantAgent"
    else:
        assistance_agent = "AssistantAgent"
    # For more than 3 agents
    group_chat_configs = {'group_chat' : {'speaker_selection_method': "round_robin",
                                                  'messages': [],
                                                  'max_round': 100},
                          'chat_manager': {'is_termination_msg': lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                                           'llm_config': {"config_list": config_list, "cache_seed": None}},
                          }

    agent_configs = [
        {'type': 'UserProxyAgent',
         'tools': ['retrieve_additional_plan_information_tool'],
         'base_agent_config': {'name': 'user',
                               'description': 'User proxy who ask questions.',
                               'human_input_mode': "NEVER",
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                               'max_consecutive_auto_reply': 20,
                               'code_execution_config': {"use_docker": False},
                               }
         },
        {'type': assistance_agent,
         'tools': ['retrieve_additional_plan_information_tool'],
         'base_agent_config': {'name': 'verilog_engineer',
                               'llm_config': {"config_list": config_list, "cache_seed": None, "temperature": 0,  "top_p": 1},
                               'description': "verilog engineer extract the signal and signal transition into the json format.",
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                               'max_consecutive_auto_reply': 20,
                               # the default system message of the AssistantAgent is overwritten here
                               'system_message': "You are a verilog RTL designer. You retrieve the required information for current plan in the knowledge graph."
                                                 "When you think the required information of the current plan is enough, Reply TERMINATE in the response.",
                               }
         }
    ]
    return agent_configs, group_chat_configs

def get_verilog_completion_agent_config(config_list: Dict[str, Any], opensource_model=False):
    if opensource_model:
        assistance_agent = "OS_AssistantAgent"
    else:
        assistance_agent = "AssistantAgent"
    os.makedirs("coding", exist_ok=True)
    # Use docker executor for running code in a container if you have docker installed.
    # code_executor = DockerCommandLineCodeExecutor(work_dir="coding")
    code_executor = LocalCommandLineCodeExecutor(work_dir="coding")
    # For more than 3 agents
    verilog_writer_group_chat_configs = {'group_chat': {'speaker_selection_method': "round_robin",
                                                        'messages': [],
                                                        'max_round': 100},
                                         'chat_manager': {
                                             'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                                            "").rstrip().endswith(
                                                 "TERMINATE"),
                                             'llm_config': {"config_list": config_list, "cache_seed": None}},
                                         }

    verilog_writer_group_agent_configs = [
        {'type': 'UserProxyAgent',
         'tools': ['verilog_syntax_check_tool'],
         'base_agent_config': {'name': 'user',
                               'description': 'User proxy who ask questions.',
                               'human_input_mode': "NEVER",
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                              "").rstrip().endswith(
                                   "TERMINATE"),
                               'max_consecutive_auto_reply': 20,
                               # 'code_execution_config': False,
                               'code_execution_config': {"executor": code_executor},
                               }
         },
        {'type': assistance_agent,
         # 'tools': [ 'verilog_syntax_check_tool'],
         'transform_message': {'method': ['HistoryLimit'],
                               'args': [{'max_messages': 3}]},
         'base_agent_config': {'name': 'verilog_engineer',
                               'llm_config': {"config_list": config_list, "cache_seed": None, "temperature": 0.1,
                                              "top_p": 1},
                               'description': "Verilog engineer who write the verilog code and complete the task.",
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                              "").rstrip().endswith(
                                   "TERMINATE"),
                               'max_consecutive_auto_reply': 20,
                               # the default system message of the AssistantAgent is overwritten here
                               'system_message': "You are a verilog RTL designer. You write and complete the verilog code "
                                                 "given the module description and the task. You need to follow the "
                                                 "verilog_verification_assistant's suggestion to modify the code. "
                                                 "You need to return the latest verilog code with ```verilog and ``` bracket."
                               }
         },
        {'type': assistance_agent,
         'tools': ['verilog_syntax_check_tool'],
         'transform_message': {'method': ['HistoryLimit'],
                               'args': [{'max_messages': 3}]},
         'base_agent_config': {'name': 'verilog_verification_assistant',
                               'llm_config': {"config_list": config_list, "cache_seed": None, "temperature": 0,
                                              "top_p": 1},
                               'description': "Assistant who verify the written verilog code and the task definition.",
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                              "").rstrip().endswith(
                                   "TERMINATE"),
                               'max_consecutive_auto_reply': 20,
                               # the default system message of the AssistantAgent is overwritten here
                               'system_message': "You are a verilog verification assistance. You verify the subtasks and written verilog code from verilog_engineer."
                                                 " Identify the mismatches of the module description, sub task and written verilog code. Suggest "
                                                 "verilog_engineer a plan to modify code with bulletins. You can not suggest modification of the Module input and output ports. "
                                                 "If The provided Verilog code correctly implements the subtask requirement, "
                                                 "you need to always return the correct verilog code with ```verilog and ``` bracket "
                                                 "firstly and Reply TERMINATE outside the ```verilog and ``` bracket. Don't only reply TERMINATE.",
                               }
         }
    ]
    return verilog_writer_group_agent_configs, verilog_writer_group_chat_configs

def get_verilog_waveform_debug_agent_config(config_list: Dict[str, Any],opensource_model=False):
    if opensource_model:
        assistance_agent = "OS_AssistantAgent"
    else:
        assistance_agent = "AssistantAgent"
    os.makedirs("coding", exist_ok=True)
    # Use docker executor for running code in a container if you have docker installed.
    # code_executor = DockerCommandLineCodeExecutor(work_dir="coding")
    code_executor = LocalCommandLineCodeExecutor(work_dir="coding")
    # For more than 3 agents
    solving_group_chat_configs = {'group_chat': {'speaker_selection_method': "round_robin",
                                                 'messages': [],
                                                 'max_round': 40},
                                  'chat_manager': {
                                      'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                                     "").rstrip().endswith(
                                          "TERMINATE"),
                                      'llm_config': {"config_list": config_list, "cache_seed": None}},
                                  }

    # agent configs
    solving_agent_configs = [
        {'type': 'UserProxyAgent',
         'tools': ['verilog_simulation_tool', 'waveform_trace_tool'],
         'base_agent_config': {'name': 'user',
                               'description': 'User proxy who ask questions and execute the tools with the provided input from Assistant.',
                               'human_input_mode': "NEVER",
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                              "").rstrip().endswith(
                                   "TERMINATE"),
                               'max_consecutive_auto_reply': 40,
                               'code_execution_config': {"executor": code_executor},
                               }
         },
        {'type': assistance_agent,
         'tools': ['verilog_simulation_tool', 'waveform_trace_tool'],
         # 'transform_message': {'method': ['LLMSummary'],
         #                      'args': [{'llm_config': {"config_list": config_list, "cache_seed": None},
         #                                'max_token': 800}]},
         'transform_message': {'method': ['HistoryLimit'],
                               'args': [{'max_messages': 3}]},
         'base_agent_config': {'name': 'verilog_engineer',
                               'description': 'Assistant who write the verilog code to resolve the task.',
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                              "").rstrip().endswith(
                                   "TERMINATE"),
                               'max_consecutive_auto_reply': 40,
                               'system_message': "You are a Verilog RTL designer that only writes verilog top_module using correct "
                                                 "Verilog syntax based on the plan. Use the provided tools to solve the task. Reply TERMINATE when the Function Check Success.",
                               # 'llm_config': {"config_list": config_list, "cache_seed": None, "temperature": 0.1, "top_p": 1},
                               'llm_config': {
                                   "temperature": 0.2,
                                   "top_p": 1,
                                   "timeout": 600,
                                   # "cache_seed": 42,
                                   "config_list": config_list,
                               },
                               },
         },
    ]
    return solving_agent_configs, solving_group_chat_configs

# debug agent without waveform tool
def get_verilog_debug_agent_config(config_list: Dict[str, Any], opensource_model=False):
    if opensource_model:
        assistance_agent = "OS_AssistantAgent"
    else:
        assistance_agent = "AssistantAgent"
    os.makedirs("coding", exist_ok=True)
    # Use docker executor for running code in a container if you have docker installed.
    # code_executor = DockerCommandLineCodeExecutor(work_dir="coding")
    code_executor = LocalCommandLineCodeExecutor(work_dir="coding")
    # For more than 3 agents
    solving_group_chat_configs = {'group_chat': {'speaker_selection_method': "round_robin",
                                                 'messages': [],
                                                 'max_round': 40},
                                  'chat_manager': {
                                      'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                                     "").rstrip().endswith(
                                          "TERMINATE"),
                                      'llm_config': {"config_list": config_list, "cache_seed": None}},
                                  }

    # agent configs
    solving_agent_configs = [
        {'type': 'UserProxyAgent',
         'tools': ['verilog_simulation_tool'],
         'base_agent_config': {'name': 'user',
                               'description': 'User proxy who ask questions and execute the tools with the provided input from Assistant.',
                               'human_input_mode': "NEVER",
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                              "").rstrip().endswith(
                                   "TERMINATE"),
                               'max_consecutive_auto_reply': 40,
                               'code_execution_config': {"executor": code_executor},
                               }
         },
        {'type': assistance_agent,
         'tools': ['verilog_simulation_tool'],
         # 'transform_message': {'method': ['LLMSummary'],
         #                      'args': [{'llm_config': {"config_list": config_list, "cache_seed": None},
         #                                'max_token': 800}]},
         'transform_message': {'method': ['HistoryLimit'],
                               'args': [{'max_messages': 3}]},
         'base_agent_config': {'name': 'verilog_engineer',
                               'description': 'Assistant who write the verilog code to resolve the task.',
                               'is_termination_msg': lambda x: x.get("content", "") and x.get("content",
                                                                                              "").rstrip().endswith(
                                   "TERMINATE"),
                               'max_consecutive_auto_reply': 40,
                               'system_message': "You are a Verilog RTL designer that only writes verilog top_module using correct "
                                                 "Verilog syntax based on the plan. Use the provided tools to solve the task. Reply TERMINATE when the Function Check Success.",
                               # 'llm_config': {"config_list": config_list, "cache_seed": None, "temperature": 0.1, "top_p": 1},
                               'llm_config': {
                                   "temperature": 0.2,
                                   "top_p": 1,
                                   "timeout": 600,
                                   # "cache_seed": 42,
                                   "config_list": config_list,
                               },
                               },
         }
    ]
    return solving_agent_configs, solving_group_chat_configs

def tool_usage_prompt(tool_configs, agent_config):
    tool_tbl = create_tool_tbl(tool_configs)
    # can specify for each agent if needed
    for agent in agent_config:
        if 'tools' not in agent:
            continue
        tool_names, formatted_tools = get_tools_descriptions(agent['tools'], tool_tbl)
        if agent['type'] != "UserProxyAgent":
            agent['base_agent_config'][
                'system_message'] += "\nUse the tools you have been provided with to verify the generated verilog code. \nHere are " \
                                     "provided tools:\n" + formatted_tools
            print(agent['base_agent_config']['name'], "->", agent['base_agent_config']['system_message'])
    return agent_config
