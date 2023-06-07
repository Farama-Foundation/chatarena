from typing import List
import os
import re
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ..message import Message, SYSTEM_NAME as SYSTEM

try:
    import anthropic
except ImportError:
    is_anthropic_available = False
    # logging.warning("anthropic package is not installed")
else:
    anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
    if anthropic_api_key is None:
        # logging.warning("Anthropic API key is not set. Please set the environment variable ANTHROPIC_API_KEY")
        is_anthropic_available = False
    else:
        is_anthropic_available = True

DEFAULT_MAX_TOKENS = 256
DEFAULT_MODEL = "claude-v1"


class Claude(IntelligenceBackend):
    """
    Interface to the Claude offered by Anthropic.
    """
    stateful = False
    type_name = "claude"

    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, model: str = DEFAULT_MODEL, **kwargs):
        assert is_anthropic_available, "anthropic package is not installed or the API key is not set"
        super().__init__(max_tokens=max_tokens, model=model, **kwargs)

        self.max_tokens = max_tokens
        self.model = model

        self.client = anthropic.Client(os.environ['ANTHROPIC_API_KEY'])

    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
    def _get_response(self, prompt: str):
        response = self.client.completion(
            prompt=prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            model=self.model,
            max_tokens_to_sample=self.max_tokens,
        )

        response = response['completion'].strip()
        return response

    def query(self, agent_name: str, role_desc: str, history_messages: List[Message], global_prompt: str = None,
              request_msg: Message = None, *args, **kwargs) -> str:
        """
        format the input and call the Claude API
        args:
            agent_name: the name of the agent
            role_desc: the description of the role of the agent
            env_desc: the description of the environment
            history_messages: the history of the conversation, or the observation for the agent
            request_msg: the request from the system to guide the agent's next response
        """
        all_messages = [(SYSTEM, global_prompt), (SYSTEM, role_desc)] if global_prompt else [(SYSTEM, role_desc)]

        for message in history_messages:
            all_messages.append((message.agent_name, message.content))
        if request_msg:
            all_messages.append((SYSTEM, request_msg.content))

        prompt = ""
        prev_is_human = False  # Whether the previous message is from human (in anthropic, the human is the user)
        for i, message in enumerate(all_messages):
            if i == 0:
                assert message[0] == SYSTEM  # The first message should be from the system

            if message[0] == agent_name:
                if prev_is_human:
                    prompt = f"{prompt}{anthropic.AI_PROMPT} {message[1]}"
                else:
                    prompt = f"{prompt}\n\n{message[1]}"
                prev_is_human = False
            else:
                if prev_is_human:
                    prompt = f"{prompt}\n\n[{message[0]}]: {message[1]}"
                else:
                    prompt = f"{prompt}{anthropic.HUMAN_PROMPT}\n[{message[0]}]: {message[1]}"
                prev_is_human = True
        assert prev_is_human  # The last message should be from the human
        # Add the AI prompt for Claude to generate the response
        prompt = f"{prompt}{anthropic.AI_PROMPT}"

        response = self._get_response(prompt, *args, **kwargs)

        # Remove the agent name if the response starts with it
        response = re.sub(rf"^\s*\[{agent_name}]:?", "", response).strip()

        return response
