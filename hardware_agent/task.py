#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

import os
import re
import threading
import uuid
import copy
from typing import Any, Dict, List, Optional, Type

from pydantic import UUID4, BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError
from hardware_agent.hardware_general_agent import HardwareAgent
import networkx as nx
# importing matplotlib.pyplot
import matplotlib.pyplot as plt
from collections import deque

DefaultTaskPromptTemplate = """
{ProblemDescription}

[Previous Task Implementation]
{PreviousTaskOutput}

[Current Task]
{Task}

[Rules]:
- Only focus on the [Current Task].
- Don't change or modify the content in [Previous Task Implementation].
"""

# Task class for task flow
class Task:
    """Class that represents a task to be executed.

    Each task must have a description, an expected output and an agent responsible for execution.

    Attributes:
        agent: Hardware agent responsible for task execution. Represents entity performing task.
        async_execution: Boolean flag indicating asynchronous task execution.
        callback: Function/object executed post task completion for additional actions.
        context: List of Task instances providing task context or input data.
        description: Descriptive text detailing task's purpose and execution.
        expected_output: Clear definition of expected task outcome. # not used now
        output_file: File path for storing task output.
        output_json: Pydantic model for structuring JSON output.
        childs: tasks being executed next.
        parents: tasks before executing this task.
    """
    def __init__(self, 
                 id: str, 
                 prompt_dict: Dict[str, Any], 
                 agent: HardwareAgent, 
                 description: str,
                 expected_output: str = "",
                 output_parser: Any=None,
                 thread: threading.Thread=None,
                 async_execution: bool=False,
                 human_input: bool=False,
                 ):
        self.id = id
        self.prompt_dict = prompt_dict
        self.agent = agent
        self.output_parser = output_parser
        self.description = description
        self.thread = thread
        self.async_execution = async_execution
        self.parents = []
        self.childs = []
        self.human_input = human_input
        self.expected_output = expected_output
        self.output = None
        self.callback = None

    def add_child(self, child_task):
        self.childs.append(child_task)

    def add_parent(self, parent_task):
        self.parents.append(parent_task)

    def get_parents(self):
        return self.parents

    def get_output(self):
        return self.output

    def get_task_id(self):
        return self.id

    def _pseudo_execute_check(self, agent: None=None, content: Optional[str] = None) -> str:
        """
        execute the task in a pseudo way for checking the task flow
        """
        # type: ignore # Incompatible types in assignment (expression has type "list[Never]", variable has type "str | None")
        context = []
        for task in (self.parents):
            if task.async_execution:
                task.thread.join()  # type: ignore # Item "None" of "Thread | None" has no attribute "join"
            if task and task.output:
                # type: ignore # Item "str" of "str | None" has no attribute "append"
                context.append(task.output)
        # print("context = ", context)
        if len(context) == 0:
            parent_task_content = "N/A"
        else:
            # type: ignore # Argument 1 to "join" of "str" has incompatible type "str | None"; expected "Iterable[str]"
            parent_task_content = "\n".join(context)

        # make the prompt dict
        if 'PreviousTaskOutput' in self.prompt_dict:
            self.prompt_dict['PreviousTaskOutput'] = parent_task_content

        prompt_str = self.prompt()
        print("[pseudo execute prompt]:\n", prompt_str, "\n")
        self.output = "[Info]: Pseudo Execution Finish task " + str(self.id)
        return "[Info]: Pseudo Execution Finish task " + str(self.id)

    def execute(self,
                agent: HardwareAgent | None=None,
                content: Optional[str] = None) -> str:
        """
        execute the task
        agent: agent to execute the task
        content: previous task output
        """
        agent = agent or self.agent # assign agent
        if not agent:
            raise Exception(
                f"The task '{self.description}' has no agent assigned, therefore it can't be executed directly and should be executed in a Crew using a specific process that support that, like hierarchical."
            )

        # resync the llm gateway
        agent.revalidate_llm_config()
        # type: ignore # Incompatible types in assignment (expression has type "list[Never]", variable has type "str | None")
        context = []
        for task in (self.parents):
            if task.async_execution:
                task.thread.join()  # type: ignore # Item "None" of "Thread | None" has no attribute "join"
            if task and task.output:
                # type: ignore # Item "str" of "str | None" has no attribute "append"
                context.append(task.output)

        if len(context) == 0:
            parent_task_content="N/A"
        else:
            # type: ignore # Argument 1 to "join" of "str" has incompatible type "str | None"; expected "Iterable[str]"
            parent_task_content = "\n".join(context)

        # make the prompt dict
        if 'PreviousTaskOutput' in self.prompt_dict:
            self.prompt_dict['PreviousTaskOutput'] = parent_task_content

        prompt_str = self.prompt()
        if self.async_execution:
            self.thread = threading.Thread(
                target=self._execute, args=(agent, prompt_str)
            )
            self.thread.start()
        else:
            result = self._execute(
                agent=agent,
                prompt_str=prompt_str,
            )
            return result
        return "[Info]: Async execution. Wait until threads finished"

    def _execute(self, agent, prompt_str):
        ### agent.initiate_chat
        # deal with the output of the task
        # print("executing chat")
        chat_results = agent.initiate_chat(message=prompt_str)

        # hook up to task util: code_block_parser
        if self.output_parser:
            # result = self.output_parser(chat_results)
            # Remove the leading and tailing spaces
            result = self.output_parser(chat_results).strip()

        # Mark: Not used now
        # exported_output = self._export_output(result)

        self.output = result

        if self.callback:
            self.callback(self.output)

        return result

    def prompt(self) -> str:
        """
        generate the prompt for the task
        """

        if 'prompt_template' in self.prompt_dict:
            prompt_template = self.prompt_dict['prompt_template']
        else:
            prompt_template = DefaultTaskPromptTemplate

        prompt_key_dict = {}
        for key, content in self.prompt_dict.items():
            if key == 'prompt_template':
                continue
            if key in prompt_template:
                prompt_key_dict[key] = content

        prompt_str = prompt_template.format(**prompt_key_dict)
        return prompt_str

    def _export_output(self, result: str) -> Any:
        exported_result = result

        if self.output_pydantic or self.output_json:
            model = self.output_pydantic or self.output_json

            # try to convert task_output directly to pydantic/json
            try:
                # type: ignore # Item "None" of "type[BaseModel] | None" has no attribute "model_validate_json"
                exported_result = model.model_validate_json(result)
                if self.output_json:
                    # type: ignore # "str" has no attribute "model_dump"
                    return exported_result.model_dump()
                return exported_result
            except Exception:
                # sometimes the response contains valid JSON in the middle of text
                match = re.search(r"({.*})", result, re.DOTALL)
                if match:
                    try:
                        # type: ignore # Item "None" of "type[BaseModel] | None" has no attribute "model_validate_json"
                        exported_result = model.model_validate_json(
                            match.group(0))
                        if self.output_json:
                            # type: ignore # "str" has no attribute "model_dump"
                            return exported_result.model_dump()
                        return exported_result
                    except Exception:
                        pass

        # regular output
        if self.output_file:
            content = (
                # type: ignore # "str" has no attribute "json"
                exported_result if not self.output_pydantic else exported_result.json()
            )
        self._save_file(content)
        return exported_result

    def _save_file(self, result: Any) -> None:
        # type: ignore # Value of type variable "AnyOrLiteralStr" of "dirname" cannot be "str | None"
        directory = os.path.dirname(self.output_file)

        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # type: ignore # Argument 1 to "open" has incompatible type "str | None"; expected "int | str | bytes | PathLike[str] | PathLike[bytes]"
        with open(self.output_file, "w", encoding='utf-8') as file:
            file.write(result)
        return None

    def print_task(self, verbose=True):
        task_description = f"Task(description={self.description}, expected_output={self.expected_output})"
        if verbose:
            task_description += "\n[Child Tasks]:\n"
            for task in self.childs:
                task_description += repr(task)
            task_description += "\n"
        return task_description

    def __repr__(self, verbose=True):
        return f"Task(description={self.description}, expected_output={self.expected_output})"


class BaseTaskFlowManager:
    """class that manages the task flows and execute the tasks

    Attributes:
        task_list: A list of tasks with task relations

    Example:
        task fields:
        id: str; task name
        parent_tasks: list[str]; parent task name
        content: str; task instruction
        source: str; task additional information
        agent: Hardware Agent to execute the task
        output_parser: function; output parser function
        prompt_dict: prompt template; Prompt for the current task
    """

    def __init__(self, task_list: List[Dict[str, Any]]=[]):
        self.task_list = task_list
        self.task_head = []
        self.task_graph = nx.DiGraph()

    # Create the DAG task graph
    def create_DAG_task_graph(self, input_task_list: List[Dict[str, Any]]=[], display_graph: bool=False):

        if len(input_task_list) == 0:
            cur_task_list = self.task_list
            print("[BaseTaskFlowManager Info]: create DAG task graph from initialized self.task_list")
        else:
            cur_task_list = input_task_list
            print("[BaseTaskFlowManager Info]: create/incrementally update DAG task graph from input_task_list")

        # create all the nodes
        for task_info in cur_task_list:
            if task_info['id'] not in self.task_graph:
                # Create a task
                """
                Need to have the following attributes to create the task
                1. prompt_dict = {'prompt_template': <template>, 'prompt_keys': prompt_values}
                2. agent = Assigned hardware agent
                3. output_parser = parser function for the output
                """
                self.task_graph.add_node(task_info['id'], task=Task(id=task_info['id'],
                                                                    prompt_dict=task_info['prompt_dict'],
                                                                    agent=task_info['agent'],
                                                                    output_parser=task_info['output_parser'],
                                                                    description=task_info['content'] + task_info['source']))

        # create the edges
        for task_info in cur_task_list:
            if 'parent_tasks' in task_info and len(task_info['parent_tasks']) > 0:
                parent_task_ids = task_info['parent_tasks']
                for pid in parent_task_ids:
                    # Mark: avoid self loop
                    assert(pid != task_info['id'] and pid in self.task_graph)
                    self.task_graph.add_edge(pid, task_info['id'])
                    # add parent and child tasks
                    self.task_graph.nodes[task_info['id']]['task'].add_parent(self.task_graph.nodes[pid]['task'])
                    self.task_graph.nodes[pid]['task'].add_child(self.task_graph.nodes[task_info['id']]['task'])
            else:
                self.task_head.append(task_info['id'])
        # Mark: Should not have multiple heads
        print("Head task are :", self.task_head)
        assert(len(self.task_head) == 1)

        # display the task flow
        if display_graph:
            # displaying graphs
            plt.figure(figsize=(18, 16))  # Set the figure size
            pos = nx.spring_layout(self.task_graph, k=1.0)
            nx.draw_networkx(self.task_graph, pos, with_labels=True)  # Draw the graph without labels
            plt.show()
        return

    # Check sequential task flow
    # 1 -> 2 -> 3 -> ... -> N
    def check_sequential_task_flow(self):

        if len(self.task_head) != 1:
            return False
        cur_task_id = self.task_head[-1]

        while (cur_task_id != -1):
            number_of_childs = len(list(self.task_graph.successors(cur_task_id)))
            print (list(self.task_graph.successors(cur_task_id)))
            if number_of_childs > 1:
                return False
            if number_of_childs == 0:
                cur_task_id = -1
            else:
                cur_task_id = list(self.task_graph.successors(cur_task_id))[-1]
        return True

    def check_dependency(self, executed_tasks: List[Any], test_task: Task):
        """
        executed_tasks: List of task ids
        test_task: tested current Task obj
        """
        parent_tasks = test_task.get_parents()
        for p_task in parent_tasks:
            if p_task.get_task_id() not in executed_tasks:
                # need to wait until all the parent task finished
                return False
        return True

    # Execute the task flow from the head
    def execute_task_flows(self, pseudo: bool=False):

        # execute in BFS ways
        # queue
        q = deque()
        tmp_q = deque()
        task_executed_results = []
        executed_tasks = set()
        for p_task_id in self.task_head:
            q.append(p_task_id)

        while len(q) > 0:
            # all the tasks in q can be executed parallely
            current_task_id = q.popleft()
            current_task = self.task_graph.nodes[current_task_id]['task']
            print("\n[TaskManager]: Executing ", current_task.print_task(verbose=False), "\n")
            assert(isinstance(current_task, Task))
            if pseudo:
                current_task._pseudo_execute_check()
            else:
                current_task.execute()
            task_executed_results.append({'task_id': current_task_id, 'task_output' : current_task.get_output()})
            executed_tasks.add(current_task_id)
            for child_task_id in self.task_graph.successors(current_task_id):
                if not self.check_dependency(executed_tasks, self.task_graph.nodes[child_task_id]['task']):
                    # dependency check failed; wait until all the parent task finished
                    continue
                tmp_q.append(child_task_id)
            if len(q) == 0 and len(tmp_q) > 0:
                # move to next frontier
                q = copy.deepcopy(tmp_q)
                tmp_q.clear()
                assert(len(q) > 0 and len(tmp_q) == 0)
        return task_executed_results

    # Add task dynamically to support tree of thoughts
    def add_task_DAG_task_graph(self, input_task_list: List[Dict[str, Any]]=[], display_graph: bool=False):

        if len(input_task_list) == 0:
            print("[BaseTaskFlowManager Error]: add task without any tasks in the list")
            exit(1)
        self.create_DAG_task_graph(input_task_list,  display_graph)
        # combining the task list
        self.task_list.extend(input_task_list)

    # atomic execution access
    def get_task_head(self):
        """
        Get the head of the task flow based on topological sort
        return the list of task id of task head
        """
        return self.task_head
