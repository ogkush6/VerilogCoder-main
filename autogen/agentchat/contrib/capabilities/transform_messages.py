import copy
import re
import ast
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union

from autogen import ConversableAgent

from ....formatting_utils import colored
from .transforms import MessageTransform, _count_tokens
from ....oai.client import ModelClient, OpenAIWrapper

class TransformMessages:
    """Agent capability for transforming messages before reply generation.

    This capability allows you to apply a series of message transformations to
    a ConversableAgent's incoming messages before they are processed for response
    generation. This is useful for tasks such as:

    - Limiting the number of messages considered for context.
    - Truncating messages to meet token limits.
    - Filtering sensitive information.
    - Customizing message formatting.

    To use `TransformMessages`:

    1. Create message transformations (e.g., `MessageHistoryLimiter`, `MessageTokenLimiter`).
    2. Instantiate `TransformMessages` with a list of these transformations.
    3. Add the `TransformMessages` instance to your `ConversableAgent` using `add_to_agent`.

    NOTE: Order of message transformations is important. You could get different results based on
        the order of transformations.

    Example:
        ```python
        from agentchat import ConversableAgent
        from agentchat.contrib.capabilities import TransformMessages, MessageHistoryLimiter, MessageTokenLimiter

        max_messages = MessageHistoryLimiter(max_messages=2)
        truncate_messages = MessageTokenLimiter(max_tokens=500)
        transform_messages = TransformMessages(transforms=[max_messages, truncate_messages])

        agent = ConversableAgent(...)
        transform_messages.add_to_agent(agent)
        ```
    """
    def __init__(self, *, transforms: List[MessageTransform] = [], verbose: bool = True):
        """
        Args:
            transforms: A list of message transformations to apply.
            verbose: Whether to print logs of each transformation or not.
        """
        self._transforms = transforms
        self._verbose = verbose

    def add_to_agent(self, agent: ConversableAgent):
        """Adds the message transformations capability to the specified ConversableAgent.

        This function performs the following modifications to the agent:

        1. Registers a hook that automatically transforms all messages before they are processed for
            response generation.
        """
        agent.register_hook(hookable_method="process_all_messages_before_reply", hook=self._transform_messages)

    def _transform_messages(self, messages: List[Dict]) -> List[Dict]:
        post_transform_messages = copy.deepcopy(messages)
        # system_message = None
        # Mark: Always remember the initial query. Otherwise, agent don't know what to do next.
        # Bug fix
        system_message = copy.deepcopy(messages[0])
        # if messages[0]["role"] == "system":
        #    system_message = copy.deepcopy(messages[0])
        #    post_transform_messages.pop(0)

        for transform in self._transforms:
            # deepcopy in case pre_transform_messages will later be used for logs printing
            pre_transform_messages = (
                copy.deepcopy(post_transform_messages) if self._verbose else post_transform_messages
            )
            post_transform_messages = transform.apply_transform(pre_transform_messages)

            if self._verbose:
                logs_str, had_effect = transform.get_logs(pre_transform_messages, post_transform_messages)
                if had_effect:
                    print(colored(logs_str, "yellow"))

        if system_message:
            post_transform_messages.insert(0, system_message)
        # print("post_transform_messages = ", post_transform_messages)
        return post_transform_messages

# Mark: Added to summarize the chat messages
class LLMTransformMessages(TransformMessages):
    """Agent capability for transforming messages before reply generation using LLM to summarize.

        This capability allows you to apply LLM summary for message transformations to
        a ConversableAgent's incoming messages before they are processed for response
        generation.

        To use `LLMTransformMessages`:

        1. Create message LLMTransformMessages.
        2. Instantiate `LLMTransformMessages` with a list of these transformations.
        3. Add the `LLMTransformMessages` instance to your `ConversableAgent` using `add_to_agent`.

        Example:
            ```python
            from agentchat import ConversableAgent
            from agentchat.contrib.capabilities import LLMTransformMessages, TransformMessages, MessageTokenLimiter

            truncate_messages = MessageTokenLimiter(max_tokens=500)
            transform_messages = LLMTransformMessages(transforms=[truncate_messages])

            agent = ConversableAgent(...)
            transform_messages.add_to_agent(agent)
            ```
    """
    DEFAULT_CONFIG = False  # False or dict, the default config for llm inference

    DEFAULT_SUMMARY_PROMPT = """Below is the internal chat messages of an LLM agent. Each thought is an item in dict (json) format.
The thoughts may be memories, actions taken by the agent, or outputs from those actions. Please return a new, smaller list of json, which summarizes the chat messages. You can summarize individual thoughts, and you can condense related thoughts together with a description of their content.
The maximum tokens of all the summarized messages should be less than {TokenLimit} tokens.

Here are the chat history.
{ChatHistory}
    
Make the summaries as pithy and informative as possible. Be specific about what happened and what was learned. 
The summary will be used as keywords for searching for the original memory. Be sure to preserve any key words or important information.    
Your response must be in list of json format which contains the summarized chat messages. Each entry in the array must have an `role` key, and an `content` key. Make sure to return less list of dict (json) chat hostory.

Please follow the following rules:
1. If the `role` is `tool`, use `assistant` as `role` key. Otherwise, you can use the for original `role` key.
2. Don't "..." except for fields or keys in json file.  
"""
    DEFAULT_SUMMARY_CONTENT_PROMPT = """Summarize the takeaway from the content with less tokens. Do not add any introductory phrases.Here is the content.
{Content}

Make the summaries as pithy and informative as possible. Be specific about what happened and what was learned. 
The summary will be used as keywords for searching for the original memory. Be sure to preserve any key words or important information.
"""

    llm_config: Union[Dict, Literal[False]]
    def __init__(self, *, transforms: List[MessageTransform] = [],
                 llm_config: Optional[Union[Dict, Literal[False]]] = None,
                 max_token: int = 2500,
                 verbose: bool = True):
        """
        Args:
            transforms: A list of message transformations to apply.
            verbose: Whether to print logs of each transformation or not.
            llm_config (dict or False or None): llm inference configuration.
                Please refer to [OpenAIWrapper.create](/docs/reference/oai/client#create)
                for available options.
                When using OpenAI or Azure OpenAI endpoints, please specify a non-empty 'model' either in `llm_config` or in each config of 'config_list' in `llm_config`.
                To disable llm-based auto reply, set to False.
                When set to None, will use self.DEFAULT_CONFIG, which defaults to False.
        """
        super().__init__(transforms=transforms, verbose=verbose)
        self._validate_llm_config(llm_config)
        self._max_tokens = max_token

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


    def _summarize_messages(self, messages: List[Dict]) -> List[Dict]:

        prompt = LLMTransformMessages.DEFAULT_SUMMARY_PROMPT.format(TokenLimit=self._max_tokens,
                                                                    ChatHistory=messages)
        summary_messages = [{"content": prompt, "role": "user"}]
        response = self.client.create(messages=summary_messages)
        extracted_response = self.client.extract_text_or_completion_object(response)[0]
        try:
            final_response = ast.literal_eval(extracted_response)
        except:
            # llama open source model fix; Author: Jatin Nainani
            try:
                start = extracted_response.find('[')
                end = extracted_response.rfind(']') + 1
                list_of_dicts_str = extracted_response[start:end]
                final_response = ast.literal_eval(list_of_dicts_str)
            except:
                print("Summarize convert to list of dict failed!", extracted_response)
                return messages

        return final_response

    def _get_processed_messages_tokens(self, messages) -> int:
        processed_messages_tokens = 0
        for id in range (1, len(messages)):
            msg = messages[id]
            # Some messages may not have content.
            if not isinstance(msg.get("content"), (str, list)):
                continue
            msg_tokens = _count_tokens(msg["content"])
            # prepend the message to the list to preserve order
            processed_messages_tokens += msg_tokens
        return processed_messages_tokens

    # Mark: Todo: might need to further refactor the code
    def _append_summary_seq_msgs(self, summary_seq_msgs: List[Any],
                                 post_transform_messages: List[Any]):
        if len(summary_seq_msgs) > 0:
            # append to the post transform messages
            post_transform_messages.extend(self._summarize_messages(summary_seq_msgs))
            # reset the summary messages
            summary_seq_msgs.clear()
            return True
        return False

    def _transform_messages(self, messages: List[Dict]) -> List[Dict]:
        post_transform_messages = []
        system_message = copy.deepcopy(messages[0])

        # count the tokens: if not exceeding the max token, no need to condense memory
        processed_messages_tokens = self._get_processed_messages_tokens(messages)
        prompt_tokens = _count_tokens(messages[0]["content"])
        print('prompt token = ', prompt_tokens, 'processed token count = ', processed_messages_tokens)
        if processed_messages_tokens < self._max_tokens or \
                re.match('[F|f][I|i][N|n][A|a][L|l] [A|a][N|n][S|s][W|w][E|e][R|r]', messages[-1]['content']) or \
                messages[-1]['content'] == '':
            print('return without summary!')
            return messages

        post_transform_messages.insert(0, system_message)
        # summarize the messages
        summary_seq_msgs = []
        summary_seq_tokens = 0
        for id in range (1, len(messages)):
            msg = copy.deepcopy(messages[id])
            # don't summarize the tool_calls message for the last one
            if msg['content'] == '' or 'tool_calls' in msg:
                # preserve the order of summarized messages
                if self._append_summary_seq_msgs(summary_seq_msgs=summary_seq_msgs,
                                                 post_transform_messages=post_transform_messages):
                    assert(len(summary_seq_msgs) == 0)
                    summary_seq_tokens = 0
                    # print('\n==after append summary seq: ', summary_seq_msgs,
                    # "\npost_transform_messages = ", post_transform_messages)
                # append to the post transform messages
                post_transform_messages.append(msg)
            elif msg['role'] == 'tool':
                # preserve more information
                # preserve the order of summarized messages
                if self._append_summary_seq_msgs(summary_seq_msgs=summary_seq_msgs,
                                                 post_transform_messages=post_transform_messages):
                    assert (len(summary_seq_msgs) == 0)
                    summary_seq_tokens = 0
                    # print('\n==after append summary seq: ', summary_seq_msgs,
                    #      "\npost_transform_messages = ", post_transform_messages)
                # only summarize the content
                if 'content' in msg:
                    prompt = LLMTransformMessages.DEFAULT_SUMMARY_CONTENT_PROMPT.format(Content=msg['content'])
                    summary_messages = [{"content": prompt, "role": "user"}]
                    response = self.client.create(messages=summary_messages)
                    extracted_response = self.client.extract_text_or_completion_object(response)[0]
                    msg['content'] = extracted_response
                # append to the post transform messages
                post_transform_messages.append(msg)
            else:
                summary_seq_msgs.append(msg)
                summary_seq_tokens += _count_tokens(msg["content"])

            # summary each chunk of msgs if it exceeds the threshold
            if summary_seq_tokens > 4000:
                self._append_summary_seq_msgs(summary_seq_msgs=summary_seq_msgs,
                                              post_transform_messages=post_transform_messages)
                assert(len(summary_seq_msgs) == 0)
                summary_seq_tokens = 0
                # print('after append summary seq: ', summary_seq_msgs, post_transform_messages)

        if len(summary_seq_msgs) > 0:
            # append to the post transform messages
            post_transform_messages.extend(self._summarize_messages(summary_seq_msgs))

        print('after summarize tokens: ', self._get_processed_messages_tokens(post_transform_messages))
        return post_transform_messages
