#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

import re
from autogen.agentchat.chat import ChatResult

def extract_verilog_code_blocks(text):
    """
    Extracts code blocks enclosed between triple backticks (```) from the given text.

    Args:
        text (str): The input text containing code blocks.

    Returns:
        list: A list of code blocks found in the text.
    """
    # Regular expression to match code blocks enclosed in triple backticks
    pattern = re.compile(r'```verilog(.*?)```', re.DOTALL)

    # Find all matches of the pattern in the text
    code_blocks = pattern.findall(text)

    return code_blocks


def verilog_output_parse(response: ChatResult) -> str:

    result = None
    for k in reversed(range(len(response.chat_history))):
        chat = response.chat_history[k]
        content = extract_verilog_code_blocks(chat['content'])
        if len(content) > 0:
            result = content[-1]
            return result
    return response.summary

def validate_correct_parse(response: ChatResult) -> str:

    print("Validating correct parse")
    for k in reversed(range(len(response.chat_history))):
        chat = response.chat_history[k]
        if "[Compiled Success]" in chat['content'] and "[Function Check Success]" in chat['content']:
            return "Pass"
    return "Failed"
