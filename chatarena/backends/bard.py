from typing import List
import os
import re
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ..message import Message, SYSTEM_NAME as SYSTEM

try:
    import bardapi
except ImportError:
    is_bard_available = False
    # logging.warning("bard package is not installed")
else:
    bard_api_key = os.environ.get('_BARD_API_KEY')
    if bard_api_key is None:
        # logging.warning(
        #     "Bard API key is not set. Please set the environment variable _BARD_API_KEY")
        is_bard_available = False
    else:
        is_bard_available = True

DEFAULT_MAX_TOKENS = 4096


class Bard(IntelligenceBackend):
    """
    Interface to the Bard offered by Google.
    """
    stateful = False
    type_name = "bard"

    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, **kwargs):
        assert is_bard_available, "bard package is not installed or the API key is not set"
        super().__init__(max_tokens=max_tokens, **kwargs)

        self.max_tokens = max_tokens

        self.client = bardapi.core.Bard()

    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
    def _get_response(self, prompt: str):
        response = self.client.get_answer(
            input_text=prompt,
        )

        response = response['content'].strip()
        return response

    def query(self, agent_name: str, role_desc: str, history_messages: List[Message], global_prompt: str = None,
              request_msg: Message = None, *args, **kwargs) -> str:
        """
        format the input and call the Bard API
        args:
            agent_name: the name of the agent
            role_desc: the description of the role of the agent
            env_desc: the description of the environment
            history_messages: the history of the conversation, or the observation for the agent
            request_msg: the request from the system to guide the agent's next response
        """
        all_messages = [(SYSTEM, global_prompt), (SYSTEM, role_desc)
                        ] if global_prompt else [(SYSTEM, role_desc)]

        for message in history_messages:
            all_messages.append((message.agent_name, message.content))
        if request_msg:
            all_messages.append((SYSTEM, request_msg.content))

        # current bard api doesn't support role system, so just dump the raw messages as prompt
        response = self._get_response(str(all_messages), *args, **kwargs)

        # Remove the agent name if the response starts with it
        response = re.sub(rf"^\s*\[{agent_name}]:?", "", response).strip()

        return response
