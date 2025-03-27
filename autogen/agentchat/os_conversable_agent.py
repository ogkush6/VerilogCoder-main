from .conversable_agent import ConversableAgent
import asyncio
import copy
import functools
import inspect
import json
import logging
import re
import warnings
from collections import defaultdict
from functools import partial
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union

from openai import BadRequestError

from autogen.exception_utils import InvalidCarryOverType, SenderRequired

from .._pydantic import model_dump
from ..cache.cache import AbstractCache
from ..code_utils import (
    PYTHON_VARIANTS,
    UNKNOWN,
    check_can_use_docker_or_throw,
    content_str,
    decide_use_docker,
    execute_code,
    extract_code,
    infer_lang,
)
from ..coding.base import CodeExecutor
from ..coding.factory import CodeExecutorFactory
from ..formatting_utils import colored
from ..function_utils import get_function_schema, load_basemodels_if_needed, serialize_to_str
from ..io.base import IOStream
from ..oai.client import ModelClient, OpenAIWrapper
from ..runtime_logging import log_event, log_new_agent, logging_enabled
from .agent import Agent, LLMAgent
from .chat import ChatResult, a_initiate_chats, initiate_chats
from .utils import consolidate_chat_info, gather_usage_summary

__all__ = ("OS_ConversableAgent",)

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


# Updated version of ConversableAgent that works for open-source models, such as llama models.
# Relies on the model outputting the function call in the ReAct format properly.
# TODO: Cover edge cases of the regex used to allow for variability in function calling.
# TODO: Current version only supports single function call per reply. Implement "tools_call" key for parallel function calling.
class OS_ConversableAgent(ConversableAgent):
    def __init__(self, *args, **kwargs):
        # Initialize the parent class
        super().__init__(*args, **kwargs)

        # Custom initialization logic for OS_ConversableAgent
        logger.info("OS_ConversableAgent initialized")

        # Register replies with custom generate_oai_reply methods
        self.register_reply([Agent, None], OS_ConversableAgent.generate_oai_reply)
        self.register_reply([Agent, None], OS_ConversableAgent.a_generate_oai_reply, ignore_async_in_sync_chat=True)

    def generate_oai_reply(
            self,
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[OpenAIWrapper] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """
        Generate a reply using autogen that is compatible with open-source models.

        Args:
            messages (Optional[List[Dict]]): List of messages for context.
            sender (Optional[Agent]): Sender agent information.
            config (Optional[OpenAIWrapper]): OpenAI configuration.

        Returns:
            Tuple[bool, Union[str, Dict, None]]: A tuple indicating success and the generated response.
        """
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages.get(sender, [])

        # Generate reply using the client
        extracted_response = self._generate_oai_reply_from_client(
            client, self._oai_system_message + messages, self.client_cache
        )

        if isinstance(extracted_response, str):
            testing_content = extracted_response
        elif isinstance(extracted_response, dict):
            testing_content = extracted_response.get('content', '')
        
        # print("testing_content = ", testing_content, "\nextracted_response = ",  extracted_response)
        # Extract function name from the response using regex
        function_pattern = r"Action: Call (\w+) \w+"
        function_match = re.search(function_pattern, testing_content)
        if function_match:
            function_name = function_match.group(1)
            logger.info(f"Function Name: {function_name}")

        # Extract dictionary from the response using regex
        # Mark: Todo: Parsing the pattern but failed if there are \{ \} in the dict content especially for coding
        dict_pattern = r"Action Input: ```(\{.*?\})```"
        dict_match = re.search(dict_pattern, testing_content, re.DOTALL)  # re.DOTALL to match across newlines
        if dict_match:
            action_input = dict_match.group(1)
            logger.info(f"Action Input: {action_input}")

        if isinstance(extracted_response, str) and function_match and dict_match:
            content_to_add = extracted_response
            function_call = {'name': function_name, 'arguments': action_input}
            extracted_response = {'content': content_to_add, 'function_call': function_call}

        return (False, None) if extracted_response is None else (True, extracted_response)

    async def a_generate_oai_reply(
            self,
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using autogen.oai asynchronously."""
        iostream = IOStream.get_default()

        def _generate_oai_reply(
                self, iostream: IOStream, *args: Any, **kwargs: Any
        ) -> Tuple[bool, Union[str, Dict, None]]:
            with IOStream.set_default(iostream):
                return self.generate_oai_reply(*args, **kwargs)

        return await asyncio.get_event_loop().run_in_executor(
            None,
            functools.partial(
                _generate_oai_reply, self=self, iostream=iostream, messages=messages, sender=sender, config=config
            ),
        )
