#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

from __future__ import print_function
import sys
import os
from optparse import OptionParser

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyverilog
from pyverilog.vparser.parser import parse
from io import StringIO
import networkx as nx
# importing matplotlib.pyplot
import matplotlib.pyplot as plt
import re

# create graph from ast str
# directed graph from networkX
def create_graph_from_ast(ast, display=False, display_signal_only=False):
    graph = nx.DiGraph()
    ast.toplogic_tree_traverse(network_G=graph, rvalue=False, lvalue=False)
    if not display and not display_signal_only:
        return graph
    # Print out nodes with attributes
    nodes_to_display = []
    edges_to_display = []
    print("Nodes:")
    for node, attrs in graph.nodes(data=True):
        if display_signal_only and (not re.match("^Assign", node) and not re.match("^Always", node) and not re.match("^Module", node)):
            nodes_to_display.append(node)
        print(f"Node {node}: {attrs}")

    # Print out edges with attributes
    print("\nEdges:")
    for src, dst, attrs in graph.edges(data=True):
        if display_signal_only and src in nodes_to_display and dst in nodes_to_display:
            edges_to_display.append((src, dst))
        print(f"Edge {src} to {dst}: {attrs}")

    # displaying graphs
    plt.figure(figsize=(18, 16))  # Set the figure size
    pos = nx.spring_layout(graph, k=1.0)
    if display_signal_only:
        subgraph = graph.subgraph(nodes_to_display)
        # subgraph.add_edges_from(edges_to_display)
    else:
        subgraph = graph

    nx.draw_networkx(subgraph, pos, with_labels=True)  # Draw the graph without labels

    # Add node labels
    # node_labels = nx.get_node_attributes(graph, 'label')
    # nx.draw_networkx_labels(graph, pos, labels=node_labels)

    # edge labels
    edge_labels = nx.get_edge_attributes(subgraph, 'lines')
    nx.draw_networkx_edge_labels(
        subgraph, pos,
        edge_labels=edge_labels,
        font_color='blue'
    )
    # plt.axis('off')
    plt.show()
    return graph

def get_ast_structure_str(ast):
    normal_stdout = sys.stdout
    # put the string output to a string buffer
    result = StringIO()
    sys.stdout = result

    # traverse the ast
    ast.show(buf=sys.stdout)

    # Redirect std output to the normal mode
    sys.stdout = normal_stdout

    # Get the result out
    ast_str = result.getvalue()
    # print('ast str = ', ast_str, '\n ast end')
    return ast_str

def generate_top_logic_graph(filelist: list[str]):
    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    ast, directives = parse(filelist,
                            preprocess_include=[],
                            preprocess_define=[])

    # ast_str = get_ast_structure_str(ast)
    return create_graph_from_ast(ast, display=False, display_signal_only=False)

def main():
    INFO = "Verilog code parser"
    VERSION = pyverilog.__version__
    USAGE = "Usage: python example_parser.py file ..."

    def showVersion():
        print(INFO)
        print(VERSION)
        print(USAGE)
        sys.exit()

    optparser = OptionParser()
    optparser.add_option("-v", "--version", action="store_true", dest="showversion",
                         default=False, help="Show the version")
    optparser.add_option("-I", "--include", dest="include", action="append",
                         default=[], help="Include path")
    optparser.add_option("-D", dest="define", action="append",
                         default=[], help="Macro Definition")
    (options, args) = optparser.parse_args()

    filelist = args
    # print(filelist)
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()

    ast, directives = parse(filelist,
                            preprocess_include=options.include,
                            preprocess_define=options.define)

    # ast_str = get_ast_structure_str(ast)
    create_graph_from_ast(ast, display_signal_only=True, display=True)
    ast.show(attrnames=True)



if __name__ == '__main__':
    main()
