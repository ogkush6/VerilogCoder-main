#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

# LLM prompt and config management
"""
only support llama3 and gpt model prompts
"""

def get_plan_retrieve_prompt(llm_type):

    prompt = {}
    if llm_type == 'llama3':
        from hardware_agent.examples.VerilogCoder.OS_prompt_templates import \
            VERILOG_PLAN_RETRIEVE_PROMPT_TEMPLATE
        from hardware_agent.examples.VerilogCoder.Tool_examples import ToolExamplePrefix, ToolExampleEnd, \
            RetrievalToolExamples

        prompt["template"] = VERILOG_PLAN_RETRIEVE_PROMPT_TEMPLATE
        prompt["tool_examples"] = ToolExamplePrefix + RetrievalToolExamples + ToolExampleEnd
        return prompt
    else:
        # default is using self.llm_type=='gpt' prompt
        from hardware_agent.examples.VerilogCoder.prompt_templates import \
            VERILOG_PLAN_RETRIEVE_PROMPT_TEMPLATE
        prompt["template"] = VERILOG_PLAN_RETRIEVE_PROMPT_TEMPLATE
        return prompt

def get_verilog_completion_prompt(llm_type):
    prompt = {}
    if llm_type == 'llama3':
        from hardware_agent.examples.VerilogCoder.OS_prompt_templates import Verilog_Subtask_Template_Prompt
        from hardware_agent.examples.VerilogCoder.Tool_examples import ToolExamplePrefix, ToolExampleEnd, \
            SyntaxCheckerToolExamples

        prompt["template"] = Verilog_Subtask_Template_Prompt
        prompt["tool_examples"] = ToolExamplePrefix + SyntaxCheckerToolExamples + ToolExampleEnd
        return prompt
    else:
        # default is using self.llm_type=='gpt' prompt
        from hardware_agent.examples.VerilogCoder.prompt_templates import \
            Verilog_Subtask_Template_Prompt
        prompt["template"] = Verilog_Subtask_Template_Prompt
        return prompt

def get_verilog_debug_prompt(llm_type):
    prompt = {}
    if llm_type == 'llama3':
        from hardware_agent.examples.VerilogCoder.OS_prompt_templates import Verilog_Subtask_Prompt
        from hardware_agent.examples.VerilogCoder.Tool_examples import ToolExamplePrefix, ToolExampleEnd, \
            SimulatorToolExamples, WaveformTraceToolExamples

        prompt["template"] = Verilog_Subtask_Prompt
        prompt["tool_examples"] = ToolExamplePrefix + SimulatorToolExamples + WaveformTraceToolExamples +\
                                      ToolExampleEnd
        return prompt
    else:
        # default is using self.llm_type=='gpt' prompt
        from hardware_agent.examples.VerilogCoder.prompt_templates import \
            Verilog_Subtask_Prompt
        prompt["template"] = Verilog_Subtask_Prompt
        return prompt

def get_plan_graph_retrieval_agent_config(llm_type, llm_config):
    if llm_type == 'llama3':
        from hardware_agent.examples.VerilogCoder.verilog_agent_config_llama3 import get_plan_graph_retrieval_agent_config
        return get_plan_graph_retrieval_agent_config(config_list=llm_config)

    else:
        # default is using self.llm_type=='gpt' prompt
        from hardware_agent.examples.VerilogCoder.verilog_agent_configs import get_plan_graph_retrieval_agent_config
        return get_plan_graph_retrieval_agent_config(config_list=llm_config)

def get_verilog_completion_agent_config(llm_type, llm_config):
    if llm_type == 'llama3':
        from hardware_agent.examples.VerilogCoder.verilog_agent_config_llama3 import get_verilog_completion_agent_config
        return get_verilog_completion_agent_config(config_list=llm_config)

    else:
        # default is using self.llm_type=='gpt' prompt
        from hardware_agent.examples.VerilogCoder.verilog_agent_configs import get_verilog_completion_agent_config
        return get_verilog_completion_agent_config(config_list=llm_config)

def get_verilog_debug_agent_config(llm_type, llm_config):
    if llm_type == 'llama3':
        from hardware_agent.examples.VerilogCoder.verilog_agent_config_llama3 import get_verilog_waveform_debug_agent_config
        return get_verilog_waveform_debug_agent_config(config_list=llm_config)

    else:
        # default is using self.llm_type=='gpt' prompt
        from hardware_agent.examples.VerilogCoder.verilog_agent_configs import get_verilog_waveform_debug_agent_config
        return get_verilog_waveform_debug_agent_config(config_list=llm_config)
