#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

import copy
import re
from collections import deque
from hardware_agent.examples.VerilogCoder.pyverilog.examples.example_top_logic_graph import generate_top_logic_graph

# use class
class DebugGraph:

    def __init__(self, verilog_filelist: list[str]):
        self.filelist = verilog_filelist
        self.graph = generate_top_logic_graph(verilog_filelist)
        # print(list(self.graph.nodes(data=True)))

    def get_k_control_signals(self, target_signals: list[str], k:int, signal_only: bool=False) -> list[str]:

        control_signals = {}
        signal_level_tracer = []
        # queue
        q = deque()
        tmp_q = deque()

        for signal in target_signals:
            # store (predecessors, controlled signal)
            q.append((signal, signal))
            control_signals[signal] = self.graph.nodes[signal]['lines']

        # BFS
        for l in range (k + 1):
            # traverse l layers
            tmp_q.clear()
            level_signal_control_rels = []
            while len(q) > 0:
                cur_signal = q.popleft()
                level_signal_control_rels.append(cur_signal[0] + "->" + cur_signal[1])
                if cur_signal[0] not in control_signals:
                    if self.graph.has_edge(cur_signal[0], cur_signal[1]):
                        # must be the control signals through the edge
                        control_signals[cur_signal[0]] = self.graph[cur_signal[0]][cur_signal[1]]['lines']
                    else:
                        print("[Error] Edge not found! - ", cur_signal)
                # find the predecessors
                controls = self.graph.predecessors(cur_signal[0])
                for c in controls:
                    if c in control_signals:
                        continue
                    # exclude the parameter
                    if 'type' in self.graph.nodes[c] and self.graph.nodes[c]['type'] in ["Parameter", "Localparam"]:
                        continue
                    if signal_only and (re.match('^Always', c) or re.match('^Assign', c) or re.match('^Module', c) or re.match('^IntConst', c)):
                        continue
                    # store (predecessors, controlled signal)
                    tmp_q.append((c, cur_signal[0]))
            # swap the q
            assert(len(q) == 0)
            print(tmp_q)
            q = copy.deepcopy(tmp_q)
            # record the signal relations
            signal_level_tracer.append(level_signal_control_rels)

        return control_signals, signal_level_tracer

if __name__ == '__main__':
    debug_graph_tracer = DebugGraph(["/home/scratch.chiatungh_nvresearch/hardware-agent-marco/hardware_agent/examples/verilog_testcases/fsm_serialdata.v"])
    print(debug_graph_tracer.get_k_control_signals(['out_byte', 'done'], k=3, signal_only=True))
