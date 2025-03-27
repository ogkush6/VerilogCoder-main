#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

import os
from copy import deepcopy
from langchain import PromptTemplate
from tqdm import tqdm
from typing import List, Dict, Any, Optional
from langchain.pydantic_v1 import Field, BaseModel
import os
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_structured_output_chain,
)
from langchain_community.graphs.graph_document import (
    Node as BaseNode,
    Relationship as BaseRelationship,
    GraphDocument,
)

# from langchain_openai import ChatOpenAI
from pydantic import Field, BaseModel
from langchain.prompts import ChatPromptTemplate
# Query the knowledge graph in a RAG application
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union, Annotated
from autogen import config_list_from_json
from autogen.oai.client import ModelClient, OpenAIWrapper
import networkx as nx
import json
from collections import deque
import copy


VERILOG_KG_QUERY_PROMPT_TEMPLATE="""
You are a top-tier Verilog expert with experience in retrieving related information from a built verilog knowledge graph. 

[Plan Node Description]: 
{NodeQuery}

Let's think step by step. 
1. Find the plan node match above description.
2. Do BFS search for {k} level.
3. Output the node names from the BFS result.
   ``` Output format
   <node name A>, <node type A>, <description A>
   <node name B>, <node type B>, <description B>
   ...
   ```

The output should not include other Plan Type Nodes.
Make sure to use the valid commands. "EXCEPT" and "WHERE" is not a valid command.
"""

class Property(BaseModel):
  """A single property consisting of key and value"""
  key: str = Field(..., description="key")
  value: str = Field(..., description="value")

class Node(BaseNode):
    properties: Optional[List[Property]] = Field(
        None, description="List of node properties")

    def get_node_property(self, property_key: str):
        for property in self.properties:
            if property.key == property_key:
                return property.value
        return ""

class Relationship(BaseRelationship):
    properties: Optional[List[Property]] = Field(
        None, description="List of relationship properties"
    )

class KnowledgeGraph(BaseModel):
    """Generate a knowledge graph with entities and relationships."""
    nodes: List[Node] = Field(
        ..., description="List of nodes in the knowledge graph")
    rels: List[Relationship] = Field(
        ..., description="List of relationships in the knowledge graph"
    )

def format_property_key(s: str) -> str:
    words = s.split()
    if not words:
        return s
    first_word = words[0].lower()
    capitalized_words = [word.capitalize() for word in words[1:]]
    return "".join([first_word] + capitalized_words)

def props_to_dict(props) -> dict:
    """Convert properties to a dictionary."""
    properties = {}
    if not props:
      return properties
    for p in props:
        properties[format_property_key(p.key)] = p.value
    return properties

def map_to_base_node(node: Node) -> BaseNode:
    """Map the KnowledgeGraph Node to the base Node."""
    properties = props_to_dict(node.properties) if node.properties else {}
    # Add name property for better Cypher statement generation
    properties["name"] = node.id.title()
    return BaseNode(
        id=node.id.title(), type=node.type.capitalize(), properties=properties
    )


def map_to_base_relationship(rel: Relationship) -> BaseRelationship:
    """Map the KnowledgeGraph Relationship to the base Relationship."""
    source = map_to_base_node(rel.source)
    target = map_to_base_node(rel.target)
    properties = props_to_dict(rel.properties) if rel.properties else {}
    return BaseRelationship(
        source=source, target=target, type=rel.type, properties=properties
    )


class KnowledgeGraphToolKits:

    def __init__(self,
                 llm_config: Optional[Union[Dict, Literal[False]]] = None,
                 workdir: str="./tmp/"):

        # networkx knowledge graph
        self.networkx_graph = nx.DiGraph()
        self.networkx_graph_desp_to_nodeID_tbl_map = {}

        # SET THIS TO TRUE, TO DELETE THE CURRENT GRAPH
        self.create_new_graph = True
        # Use OpenAI Wrapper
        self._validate_llm_config(llm_config)
        self._llm_config = llm_config
        self.workdir = workdir

    def _validate_llm_config(self, llm_config):
        assert llm_config in (None, False) or isinstance(
            llm_config, dict
        ), "llm_config must be a dict or False or None."
        if llm_config is None:
            llm_config = self.DEFAULT_CONFIG
        self.llm_config = self.DEFAULT_CONFIG if llm_config is None else llm_config
        # TODO: more complete validity check
        if self.llm_config in [{}, {"config_list": []}, {"config_list": [{"model": ""}]}]:
            raise ValueError(
                "When using OpenAI or Azure OpenAI endpoints, specify a non-empty 'model' either in 'llm_config' or in each config of 'config_list'."
            )
        self.client = None if self.llm_config is False else OpenAIWrapper(**self.llm_config)

    def resync_client(self):
        self._validate_llm_config(self._llm_config)

    def ask_client(self, prompt: str) -> str:
        # print("prompt = ", prompt)
        messages = [{"content": prompt, "role": "user"}]
        response = self.client.create(messages=messages)
        extracted_response = self.client.extract_text_or_completion_object(response)[0]
        if extracted_response is None:
            print("Object is none. Prompt is ", prompt)
        else:
            extracted_response = extracted_response.replace("\"", "")
        # print(extracted_response)
        return extracted_response

    # Use simple knowledge graph
    def build_knowledge_graph(self,
                              plans: List[str],
                              signal_nodes_extract: Dict[str, List[str]],
                              display_neo4j_graph: bool=False):
        plan_nodes = []
        signal_nodes = []
        signal_transitions = []
        signal_examples = []
        print("[Determine KG Build Graph Info]: Creating Plan Nodes...")
        NodeIDPromptTemplate = """You are a top-tier Verilog expert with experience in extracting the Node ID to represent a Node in knowledge graph from a descriptions.
        **Nodes** represent signal name, state name, state transition, plan, and signal example.
        **Node IDs**: Never utilize integers as node IDs. Node IDs should be concise, have signal name, human-readable identifiers and be able to represent the description. The Node IDs should not exceed 60 texts.
        
        [Target Description]
        {Description}
        
        Return the extracted Node ID only.
        """
        # decide the nodes
        for plan in plans:
            prompt = NodeIDPromptTemplate.format(Description="Plan: " + plan)
            node_id = self.ask_client(prompt)
            plan_nodes.append(Node(id=node_id, type='Plan', properties=[Property(key='description', value=plan)]))

        print("[Determine KG Build Graph Info]: Creating Signal Nodes...")
        for signal in signal_nodes_extract['signal']:
            prompt = NodeIDPromptTemplate.format(Description="Signal Name: " + signal)
            node_id = self.ask_client(prompt)
            signal_nodes.append(Node(id=node_id, type='Signal', properties=[Property(key='description', value=signal)]))

        print("[Determine KG Build Graph Info]: Creating State Transition Nodes...")
        for state_transition_description in signal_nodes_extract['state_transitions_description']:
            prompt = NodeIDPromptTemplate.format(Description="StateTransition: " + state_transition_description)
            node_id = self.ask_client(prompt)
            signal_transitions.append(Node(id=node_id, type='StateTransition', properties=[Property(key='description',
                                                                                                    value=state_transition_description)]))
        print("[Determine KG Build Graph Info]: Creating Signal Example Nodes...")
        for signal_example in signal_nodes_extract['signal_examples']:
            prompt = NodeIDPromptTemplate.format(Description="SignalExample: " + signal_example)
            node_id = self.ask_client(prompt)
            signal_examples.append(Node(id=node_id, type='SignalExample', properties=[Property(key='description', value=signal_example)]))
        print("[Determine KG Build Graph Info]: Creating Nodes done...")

        # determine the relations
        RelationPromptTemplate = """You are a top-tier Verilog expert with experience in determining the relationships of two node descriptions.
        
        [Description Node 1]
        {Description1}
        
        [Description Node 2]
        {Description2}
        
        [Instruct]: Determine the relationships of the above two node description.
        {RelationType}
        
        Reply "<Determined Relationship>" in the response only.
        """
        PlanRelType="""
        "IMPLEMENTS" relationship: If the description node 2 occurs in description node 1.  
        "NORELATION" relationship: there are no relationship of these two nodes base on their description.
        """
        SignalRelType="""
        "EXAMPLES" relationship: A SignalExample type node description is describing an example of the Signal type node.
        "STATETRANSITION" relationship: the description of Signal type node is the current state or next-state in the StateTransition description.
        "NORELATION" relationship: there are no relationship of these two node base on their description.
        """
        print("[Determine KG Build Graph Info]: Creating Rels...")
        rels = []
        for i in range(len(plan_nodes)):

            description1 = "node id: " + plan_nodes[i].id + "\nnode type: " + plan_nodes[i].type + "\ndescription: " + \
                           plan_nodes[i].get_node_property(property_key="description")
            for j in range (len(signal_nodes)):
                # resync the client
                self.resync_client()
                print('plan node idx: ', i, ' signal node idx: ', j)
                description2 = "node id: " + signal_nodes[j].id + "\nnode type: " + signal_nodes[j].type + "\ndescription: " + \
                           signal_nodes[j].get_node_property(property_key="description")

                prompt = RelationPromptTemplate.format(Description1=description1, Description2=description2,
                                                       RelationType=PlanRelType)
                extracted_response = self.ask_client(prompt)
                # print("response = ", extracted_response)
                if "NORELATION" in extracted_response:
                    continue
                # create relation
                rels.append(Relationship(source=plan_nodes[i], target=signal_nodes[j], type=extracted_response, properties=[]))

        for i in range(len(signal_nodes)):
            description1 = "node id: " + signal_nodes[i].id + "\nnode type: " + signal_nodes[i].type  + "\ndescription: " + \
                           signal_nodes[i].get_node_property(property_key="description")
            for j in range(len(signal_transitions)):
                # resync the client
                self.resync_client()
                print('signal node idx: ', i, ' and ', j)
                description2 = "node id: " + signal_transitions[j].id + "\nnode type: " + signal_transitions[j].type + "\ndescription: " + \
                               signal_transitions[j].get_node_property(property_key="description")
                prompt = RelationPromptTemplate.format(Description1=description1, Description2=description2,
                                                       RelationType=SignalRelType)
                extracted_response = self.ask_client(prompt)
                # print("response = ", extracted_response)
                if "NORELATION" in extracted_response:
                    continue
                # create relation
                rels.append(Relationship(source=signal_nodes[i], target=signal_transitions[j], type=extracted_response, properties=[]))

        for i in range(len(signal_nodes)):
            description1 = "node id: " + signal_nodes[i].id + "\nnode type: " + signal_nodes[i].type + "\ndescription: " + \
                           signal_nodes[i].get_node_property(property_key="description")
            for j in range(len(signal_examples)):
                # resync the client
                self.resync_client()
                print('signal node idx: ', i, ' and ', j)
                description2 = "node id: " + signal_examples[j].id + "\nnode type: " + signal_examples[j].type + "\ndescription: " + \
                               signal_examples[j].get_node_property(property_key="description")
                prompt = RelationPromptTemplate.format(Description1=description1, Description2=description2,
                                                       RelationType=SignalRelType)
                extracted_response = self.ask_client(prompt)
                # print("response = ", extracted_response)
                if "NORELATION" in extracted_response:
                    continue
                # create relation
                rels.append(Relationship(source=signal_nodes[i], target=signal_examples[j], type=extracted_response,
                                         properties=[]))

        nodes = [*plan_nodes, *signal_nodes, *signal_transitions, *signal_examples]

        print("[Determine KG Build Graph Info]: Creating Rels Done...")

        # build the networkx graph
        for node in nodes:
            self.networkx_graph.add_node(node.id, type=node.type, description=node.get_node_property(property_key="description"))
            self.networkx_graph_desp_to_nodeID_tbl_map[node.get_node_property(property_key="description")] = node.id

        # build the edges
        for rel in rels:
            self.networkx_graph.add_edge(rel.source.id, rel.target.id, type=rel.type)

        graph_data = nx.node_link_data(self.networkx_graph)
        with open( self.workdir + '/networkx_kg.json', 'w') as f:
            json.dump(graph_data, f)

    
    def create_knowledge_graph(self,
                               TEXT: str,
                               plans: List[str]=[],
                               signal_nodes_extract: Dict[str, List[str]]={'signal': [],
                                                                           'state_transitions_description': [],
                                                                           'signal_examples': []},
                               chunk_size: int=4096,
                               chunk_overlap: int=24,
                               determined_nodes: bool=False ):

        if self.create_new_graph:
            # networkx knowledge graph
            self.networkx_graph = nx.DiGraph()
            self.networkx_graph_desp_to_nodeID_tbl_map = {}

        self.build_knowledge_graph(plans=plans, signal_nodes_extract=signal_nodes_extract)
        return

    def build_desp_to_nodeID_map(self):
        for node_id in self.networkx_graph.nodes():
            node_description = self.networkx_graph.nodes[node_id]['description']
            if node_description not in self.networkx_graph_desp_to_nodeID_tbl_map:
                self.networkx_graph_desp_to_nodeID_tbl_map[node_description] = node_id
        print(self.networkx_graph_desp_to_nodeID_tbl_map)

    def networkx_bfs_knowledge_graph_query(self, query: str, bfs_level: int=1):

        # check graph
        # print("nodes = ", self.networkx_graph.number_of_nodes(), " edges = ", self.networkx_graph.number_of_edges())
        if (self.networkx_graph.number_of_nodes() == 0 and self.networkx_graph.number_of_edges() == 0):
            print("[Warning] NetworkX graph is empty!")
            if os.path.exists(self.workdir + '/networkx_kg.json'):
                print("[Warning] loading graph from ", self.workdir, "/networkx_kg.json.")
                with open(self.workdir + '/networkx_kg.json', 'r') as f:
                    graph_data_loaded = json.load(f)
                self.networkx_graph = nx.node_link_graph(graph_data_loaded)
                print("nodes = ", self.networkx_graph.number_of_nodes(),
                      " edges = ", self.networkx_graph.number_of_edges())
                self.build_desp_to_nodeID_map()

        match_node_id = ""
        if query in self.networkx_graph_desp_to_nodeID_tbl_map:
            match_node_id = self.networkx_graph_desp_to_nodeID_tbl_map[query]
        # assert(match_node_id!= "") # If not match to any nodes, need similarity search! Todo work now.
        if match_node_id == "":
            return "[Error] Can not find the description node. Make sure to extract all the content inside ``` and ``` block including comma, or period."
        # execute in BFS ways
        # queue
        q = deque()
        tmp_q = deque()
        q.append((match_node_id, match_node_id))

        frontier_level = 0

        result = "[Retrieved neighbor information of the knowledge graph using BFS "+str(bfs_level) + " level]:\n"
        retrieved_description = set()
        while len(q) > 0 and frontier_level <= bfs_level:
            # all the tasks in q can be executed parallely
            (parent_node_id, cur_node_id) = q.popleft()
            if parent_node_id != cur_node_id and self.networkx_graph.nodes[cur_node_id]['description'] not in retrieved_description:
                result += self.networkx_graph.nodes[cur_node_id]['description'] + " (Type:" + self.networkx_graph.nodes[cur_node_id]['type'] + ")\n"
                retrieved_description.add(self.networkx_graph.nodes[cur_node_id]['description'])
            for child_node in self.networkx_graph.successors(cur_node_id):
                tmp_q.append((cur_node_id, child_node))
            if len(q) == 0 and len(tmp_q) > 0:
                frontier_level += 1
                if frontier_level == bfs_level:
                    result += "\n[The " + str(bfs_level+1) +"-th BFS level of Neighbor information of the knowledge graph]:\n"
                # move to next frontier
                q = copy.deepcopy(tmp_q)
                tmp_q.clear()
                assert (len(q) > 0 and len(tmp_q) == 0)
        if len(retrieved_description) == 0:
            return "Can not find any Neighbor information in the knowledge graph. You can TERMINATE and continue to next tasks."
        return result


