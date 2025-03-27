#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

import os
from autogen.agentchat.contrib.capabilities import teachability
from autogen.cache import Cache
from autogen.coding import DockerCommandLineCodeExecutor, LocalCommandLineCodeExecutor
from autogen import GroupChat, GroupChatManager, AssistantAgent, ConversableAgent, UserProxyAgent, config_list_from_json, register_function
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union
from autogen.agentchat.contrib.capabilities import transform_messages, transforms
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.phi_image_agent import PhiVConversableAgent
from autogen.agentchat.os_conversable_agent import OS_ConversableAgent
from autogen.agentchat.os_assistant_agent import OS_AssistantAgent

# Normally user don't need to change the termination msg
def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

class HardwareAgent:
    # Hardware agent has planner, react assistant, RAG assistant, and memory controlling unit
    # agent config
    """
    agent_configs = [
    {'type': 'UserProxyAgent',
     'tools': [],
     'is_termination_msg': lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
     'base_agent_config': { 'name': 'user',
                 'description': 'User proxy who ask questions and execute the tools with the provided input from Assistant.',
                 'args': ...
                 }
     },
     {'type': 'AssistantAgent',
     'tools': [],
     'teachable': {'args': {'reset_db': True, ...}},
     'is_termination_msg': lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
     'transform_message': { 'method': ['LLMSummary', 'HistoryLimit', 'TokenLimit'], 'args': [{'max_messages': 3, 'min_tokens': 10}, {}]},
     'base_agent_config': {'name': 'assistant',
                           'description': 'Assistant who reasons the problem and uses the provided tools to resolve the task.',
                            args...,
                          }
     }
      # reference https://microsoft.github.io/autogen/docs/notebooks/agentchat_groupchat_RAG/
      Only support for rag_chat in the start; Can only use one of UserProxyAgent or RetrieveUserProxyAgent.
      {'type': 'RetrieveUserProxyAgent',
      'tools': [],
      'is_termination_msg': lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
     'teachable': {'args': {'reset_db': True, ...}},
     'transform_message': { 'method': ['LLMSummary', 'HistoryLimit', 'TokenLimit'], 'args': [{'max_messages': 3, 'min_tokens': 10}, {}]},
     ''base_agent_config': { 'name': 'Retrieval Assistant',
                             'retrieve_config': {'taks': ...},
                             'description': 'Assistant who reasons the problem and uses the provided tools to resolve the task.',
                             'args': ...,
                            }
      }
    ]
    tool_configs = [{'function_call': function,
                    'executor': 'execute agent name',
                    'caller': 'caller agent name',
                    'name': '<name>',
                    'description: '<description>',
                    'tool_examples': 'examples for prompt'
                    }, ...],
    ###
    Reference of Assistant Agent
    # ReACT LLM
    AssistantAgent(
        name="Assistant",
        system_message="Only use the tools you have been provided with. Reply TERMINATE when the task is done.",
        llm_config={"config_list": config_list, "cache_seed": None},
        description="Assistant who reasons the problem and uses the provided tools to resolve the task.",
    )
    ###
    Reference to register a function
    register_function(
        timing_metric_calculation_tool,
        caller=assistant,
        executor=user_proxy,
        name="timing_metric_calculation_tool",
        description="Use this tool to calculate the change of one of WNS, TNS, or FEP\" timing metric of designs.\n"
                    "Input the metric name and the metric value vectors for calculating the change of a pair of settings in string format.",
    )
    llm_config = {"config_list": config_list, "timeout": 60, "temperature": 0.8, "seed": 1234}
    """
    # Define the supported agent class list
    AGENTCLASSLIST = {'UserProxyAgent': UserProxyAgent,
                      'AssistantAgent': AssistantAgent,
                      'ConversableAgent': ConversableAgent,
                      'RetrieveUserProxyAgent': RetrieveUserProxyAgent,
                      'RetrieveAssistantAgent': RetrieveAssistantAgent,
                      'PhiVConversableAgent': PhiVConversableAgent, # Added image LLM support
                      'OS_AssistantAgent': OS_AssistantAgent,
                      'OS_ConversableAgent': OS_ConversableAgent
                      }
    TRANSFORMMESSAGELIST = { 'LLMSummary': transform_messages.LLMTransformMessages,
                             'HistoryLimit': transforms.MessageHistoryLimiter,
                             'TokenLimit': transforms.MessageTokenLimiter
                           }

    def __init__(self,
                 agent_configs: List[Dict[str, Any]],
                 tool_configs: List[Dict[str, Any]],
                 group_chat_kwargs: Optional[Dict[str, Any]]={'group_chat': {'speaker_selection_method': "auto",
                                                                             'messages': [],
                                                                             'max_round': 15},
                                                              'chat_manager': {'llm_config':
                                                                                   {"config_list": None,
                                                                                    "cache_seed": None}}}):

        # Todo: need to check number of proxy agent
        self.num_proxy_agent = 0
        self.num_assistant_agent = 0
        self.num_rag_proxy_agent = 0
        self.agents = {}
        self.proxy_agent = None
        # Memories
        self.teachable_database = []
        self.transform_messages_handlers = []

        for agent_config in agent_configs:

            if agent_config['type'] not in self.AGENTCLASSLIST:
                print('[Error] The agent type ', agent_config['type'], ' is not supported!')
                continue

            # create agent
            if agent_config['type'] == 'UserProxyAgent':
                self.proxy_agent = self.AGENTCLASSLIST['UserProxyAgent'](
                    # is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                    **agent_config['base_agent_config']
                )
                self.num_proxy_agent += 1
                self.agents[agent_config['base_agent_config']['name']] = self.proxy_agent
            elif agent_config['type'] == 'RetrieveUserProxyAgent':
                assert(self.proxy_agent is None)
                self.proxy_agent = self.AGENTCLASSLIST['RetrieveUserProxyAgent'](
                    # is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                    **agent_config['base_agent_config']
                )
                self.num_rag_proxy_agent += 1
                self.agents[agent_config['base_agent_config']['name']] = self.proxy_agent
            else:
                # Should include llm_configs
                self.agents[agent_config['base_agent_config']['name']] = self.AGENTCLASSLIST[agent_config['type']](
                    # is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                    **agent_config['base_agent_config']
                )
                self.num_assistant_agent += 1
            # short term memory
            if 'transform_message' in agent_config:
                self._add_transform_messages(transform_message_config_list=agent_config['transform_message'],
                                             agent=self.agents[agent_config['base_agent_config']['name']],
                                             agent_name=agent_config['base_agent_config']['name'])
            # long term memory capability
            if 'teachable' in agent_config:
                self._add_teachability(teachable_config=agent_config['teachable']['args'],
                                       agent=self.agents[agent_config['base_agent_config']['name']],
                                       agent_name=agent_config['base_agent_config']['name'])
        # end initializing the agent
        self.manager = None
        if self.num_assistant_agent + self.num_proxy_agent + self.num_rag_proxy_agent > 2:
            agents_list = []
            for agent_name in self.agents:
                agents_list.append(self.agents[agent_name])
            """
            speaker_selection_method argument:
            https://microsoft.github.io/autogen/docs/reference/agentchat/groupchat/
            "auto": the next speaker is selected automatically by LLM.
            "manual": the next speaker is selected manually by user input.
            "random": the next speaker is selected randomly.
            "round_robin": the next speaker is selected in a round robin fashion, i.e., iterating in the same order as provided in agents.
            a customized speaker selection function (Callable): the function will be called to select the next speaker. The function should take the last speaker and the group chat as input and return one of the following:
            """
            groupchat = GroupChat(agents=agents_list, **group_chat_kwargs['group_chat'])
            #     messages=[], max_round=15,
            #    speaker_selection_method=group_speaker_selection_method
            # )
            self.manager = GroupChatManager(groupchat=groupchat, **group_chat_kwargs['chat_manager'])

        # register tools
        for tool in tool_configs:
            print('register tool ', tool['name'], tool['function_call'], ' caller: ', self.agents[tool['caller']],
                  ' executer: ', self.agents[tool['executor']])
            register_function(tool['function_call'],
                              caller=self.agents[tool['caller']],
                              executor=self.agents[tool['executor']],
                              name=tool['name'],
                              description=tool['description'])
        print(f"Hardware Agent Initialized %d proxy, %d rag proxy, %d assistants"%(self.num_proxy_agent,
                                                                                   self.num_rag_proxy_agent,
                                                                                   self.num_assistant_agent))

    def _add_transform_messages(self,
                                transform_message_config_list: Dict[str, List[Any]],
                                agent: Union[UserProxyAgent, AssistantAgent, RetrieveUserProxyAgent] = None,
                                agent_name: str = ""):
        # Not support LLMSummary with other types of method
        if 'LLMSummary' in transform_message_config_list['method']:
               assert(len(transform_message_config_list['method']) == 1)
        if 'LLMSummary' in transform_message_config_list['method']:
            """
            condensed_config_list = config_list_from_json(env_or_file="chat_summary_llm_config.txt")
            context_handling = transform_messages.LLMTransformMessages(
                    llm_config={"config_list": config_list, "cache_seed": None}, max_token=1500)
            """
            self.transform_messages_handlers.append({'agent': agent_name,
                                        'config': transform_message_config_list,
                                        'obj': self.TRANSFORMMESSAGELIST['LLMSummary'](**transform_message_config_list['args'][0])})
        else:
            """
            context_handling = transform_messages.TransformMessages(
               transforms=[
                    transforms.MessageHistoryLimiter(max_messages=10),
                    transforms.MessageTokenLimiter(max_tokens=1000, max_tokens_per_message=50, min_tokens=500),
               ]
            )
            """
            transforms_list = []
            for t in range (len(transform_message_config_list['method'])):
                transforms_list.append(self.TRANSFORMMESSAGELIST[transform_message_config_list['method'][t]](**transform_message_config_list['args'][t]))
            self.transform_messages_handlers.append({'agent': agent_name,
                                                     'config': transform_message_config_list,
                                                     'obj': transform_messages.TransformMessages(transforms=transforms_list)})
        self.transform_messages_handlers[-1]['obj'].add_to_agent(agent)
        return

    def _add_teachability(self,
                          teachable_config: Dict[str, Any] = {'verbosity': 1, 'reset_db': True, 'path_to_db': "./tmp/"},
                          agent: Union[UserProxyAgent, AssistantAgent, RetrieveUserProxyAgent]= None,
                          agent_name: str=""):
        self.teachable_database.append({'agent': agent_name,
                                        'config': teachable_config,
                                        'obj': teachability.Teachability(**teachable_config)})
        self.teachable_database[-1]['obj'].add_to_agent(agent)
        return

    def reset_agents(self):
        for agent_name in self.agents:
            self.agents[agent_name].reset()

    # revalidate the llm for gateway chat
    def revalidate_llm_config(self):
        for agent_name in self.agents:
            if type(self.agents[agent_name]) == UserProxyAgent or \
                    type(self.agents[agent_name]) == RetrieveUserProxyAgent:
                continue
            self.agents[agent_name].revalidate_llm_config()

    # Mark: start the chat to proxy
    # Need to input the pure text question after using prompt formatting
    def initiate_chat(self, use_cache: bool=False, cache_seed: int=43, **kwargs) -> str:

        if self.manager is None:
            # one assistant + one proxy
            assistant = None
            for agent_name in self.agents:
                if type(self.agents[agent_name]) == UserProxyAgent or \
                        type(self.agents[agent_name]) == RetrieveUserProxyAgent:
                    continue
                assistant = self.agents[agent_name]
            assert(assistant is not None)
            # Cache LLM responses. To get different responses, change the cache_seed value.
            with Cache.disk(cache_seed=cache_seed) as cache:
                if use_cache:
                    kwargs['cache'] = cache
                    print('[Info]: use cache seed ', cache_seed, ' for chat')
                # Regular ReACT reasoning
                if type(self.proxy_agent) == UserProxyAgent:
                    return self.proxy_agent.initiate_chat(assistant, **kwargs)
                # RAG proxy
                elif type(self.proxy_agent) == RetrieveUserProxyAgent:
                    return self.proxy_agent.initiate_chat(assistant, message=self.proxy_agent.message_generator, **kwargs)
        elif self.manager is not None:
            # Group chat
            with Cache.disk(cache_seed=cache_seed) as cache:
                if use_cache:
                    kwargs['cache'] = cache
                    print('[Info]: use cache seed ', cache_seed, ' for chat')
                # Regular ReACT reasoning
                if type(self.proxy_agent) == UserProxyAgent:
                    return self.proxy_agent.initiate_chat(self.manager, **kwargs)
                # RAG proxy
                elif type(self.proxy_agent) == RetrieveUserProxyAgent:
                    return self.proxy_agent.initiate_chat(self.manager, message=self.proxy_agent.message_generator, **kwargs)
        return "[Error]: Didn't complete chat! please check the agent config"

# Todo: RAG as a function call
class HardwareAgentWithRAGCall(HardwareAgent):
    # Call the RAG through function call during chats
    """
     # reference https://microsoft.github.io/autogen/docs/notebooks/agentchat_groupchat_RAG/
     {'type': 'RetrieveUserProxyAgent',
     'teachable': {'enable': True/False, 'args': {'reset_db': True, ...}},
     'MessageTransform': { 'method': ['LLMSummary', 'LastN', 'MaxToken'], 'args': {'max_messages': 3, 'min_tokens': 10}},
     ''base_agent_config': { 'name': 'Retrieval Assistant',
                             'retrieve_config': {'taks': ...},
                             'descriptions': 'Assistant who reasons the problem and uses the provided tools to resolve the task.',
                             'args': ...,
                            }
      }
    """
    def __init__(self):
        pass
