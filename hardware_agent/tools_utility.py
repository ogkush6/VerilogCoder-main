#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

# utilities for tools descriptions
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union

def create_tool_tbl(tool_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    tool_table_map = {}
    for tool in tool_configs:
        tool_table_map[tool['name']] = tool
    return tool_table_map

def get_tools_descriptions(tools: List[str], tool_table_map: Dict[str, Any]) -> (str, str):
    tool_strings = []
    for name in tools:
        description = tool_table_map[name]['description']
        tool_strings.append(f"{name}: \n{description}")

    formatted_tools = "\n".join(tool_strings)
    tool_names = ", ".join([tool for tool in tools])
    return tool_names, formatted_tools
