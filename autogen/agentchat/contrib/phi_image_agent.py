import os
import json
import copy
from typing import Dict, List, Optional, Tuple, Union, Annotated

from autogen import OpenAIWrapper
from autogen.agentchat import Agent, ConversableAgent
from autogen.agentchat.contrib.img_utils import (
    gpt4v_formatter,
    message_formatter_pil_to_b64,
)
from autogen.code_utils import content_str

from autogen._pydantic import model_dump
import base64
import httpx

DEFAULT_LMM_SYS_MSG = """You are a helpful AI assistant."""
DEFAULT_MODEL = "gpt-4-vision-preview"

# Original Author: Chen-Chia Cheng
'''Conversable Agent for Phi-vision (Still need for testing for multi-agent setting)'''
class PhiVConversableAgent(ConversableAgent):
    def __init__(
            self,
            name: str,
            system_message: Optional[Union[str, List]] = DEFAULT_LMM_SYS_MSG,
            is_termination_msg: str = None,
            *args,
            **kwargs,
    ):
        """
        Args:
            name (str): agent name.
            system_message (str): system message for the OpenAIWrapper inference.
                Please override this attribute if you want to reprogram the agent.
            **kwargs (dict): Please refer to other kwargs in
                [ConversableAgent](../conversable_agent#__init__).
        """
        super().__init__(
            name,
            system_message,
            is_termination_msg=is_termination_msg,
            *args,
            **kwargs,
        )
        # call the setter to handle special format.
        self.update_system_message(system_message)
        self._is_termination_msg = (
            is_termination_msg
            if is_termination_msg is not None
            else (lambda x: content_str(x.get("content")) == "TERMINATE")
        )

        # Override the `generate_oai_reply`
        self.replace_reply_func(ConversableAgent.generate_oai_reply, PhiVConversableAgent.generate_oai_reply)
        self.replace_reply_func(
            ConversableAgent.a_generate_oai_reply,
            PhiVConversableAgent.a_generate_oai_reply,
        )

    def update_system_message(self, system_message: Union[Dict, List, str]):
        """Update the system message.

        Args:
            system_message (str): system message for the OpenAIWrapper inference.
        """
        self._oai_system_message[0]["content"] = self._message_to_dict(system_message)["content"]
        self._oai_system_message[0]["role"] = "system"

    @staticmethod
    def _message_to_dict(message: Union[Dict, List, str]) -> Dict:
        """Convert a message to a dictionary. This implementation
        handles the GPT-4V formatting for easier prompts.

        The message can be a string, a dictionary, or a list of dictionaries:
            - If it's a string, it will be cast into a list and placed in the 'content' field.
            - If it's a list, it will be directly placed in the 'content' field.
            - If it's a dictionary, it is already in message dict format. The 'content' field of this dictionary
            will be processed using the gpt4v_formatter.
        """
        if isinstance(message, str):
            return {"content": gpt4v_formatter(message, img_format="pil")}
        if isinstance(message, list):
            return {"content": message}
        if isinstance(message, dict):
            assert "content" in message, "The message dict must have a `content` field"
            if isinstance(message["content"], str):
                message = copy.deepcopy(message)
                message["content"] = gpt4v_formatter(message["content"], img_format="pil")
            try:
                content_str(message["content"])
            except (TypeError, ValueError) as e:
                print("The `content` field should be compatible with the content_str function!")
                raise e
            return message
        raise ValueError(f"Unsupported message type: {type(message)}")

    def generate_oai_reply(
            self,
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[OpenAIWrapper] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using autogen.oai."""
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]

        '''
        [Chen-Chia] Customize this part to accomodate with Phi-vision-128k-instruct and Neva-22B
        Begin:
        '''
        messages_with_b64_img = message_formatter_pil_to_b64(self._oai_system_message + messages)
        context = ""
        current_role = ""
        for content_dict in messages_with_b64_img:
            for content in content_dict['content']:
                if content['type'] == 'text':
                    if current_role != content_dict["role"]:
                        context += (content_dict["role"] + ": " + content['text'] + ' ')
                        current_role = content_dict["role"]
                    else:
                        context += (content['text'] + ' ')

        # print(image_url)
        # print('context', context)
        messages = [
            {"role": "user",
             "content": [
                 {"type": "text", "text": context},
                 {"type": "image_url", "image_url": messages_with_b64_img[1]['content'][1]["image_url"]['url']}
                 # or image/jpeg
             ]
             },
        ]
        response = client.create(context=messages[-1].pop("context", None), messages=messages)
        '''
        [Chen-Chia] End.
        '''
        # print('finish request')

        # TODO: line 301, line 271 is converting messages to dict. Can be removed after ChatCompletionMessage_to_dict is merged.
        extracted_response = client.extract_text_or_completion_object(response)[0]
        if not isinstance(extracted_response, str):
            extracted_response = model_dump(extracted_response)
        return True, extracted_response
