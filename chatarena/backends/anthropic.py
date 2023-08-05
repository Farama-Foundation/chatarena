from typing import List
import os
import re
import logging
import litellm 
from litellm import completion 
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ..message import Message, SYSTEM_NAME, MODERATOR_NAME

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
    def _get_response(self, messages):
        response = completion(
            messages=messages,
            stop=anthropic.HUMAN_PROMPT,
            model=self.model,
            max_tokens=self.max_tokens,
        )

        response = completion.choices[0]['message']['content']
        response = response.strip()
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
        all_messages = [(SYSTEM_NAME, global_prompt), (SYSTEM_NAME, role_desc)] if global_prompt else [(SYSTEM_NAME, role_desc)]
        for message in history_messages:
            all_messages.append((message.agent_name, message.content))
        if request_msg:
            all_messages.append((SYSTEM_NAME, request_msg.content))
        messages = []
        for i, msg in enumerate(all_messages):
            if i == 0:
                assert msg[0] == SYSTEM_NAME  # The first message should be from the system
                messages.append({"role": "system", "content": msg[1]})
            else:
                if msg[0] == agent_name:
                    messages.append({"role": "assistant", "content": msg[1]})
                else:
                    if messages[-1]["role"] == "user":  # last message is from user
                        if self.merge_other_agent_as_user:
                            messages[-1]["content"] = f"{messages[-1]['content']}\n\n[{msg[0]}]: {msg[1]}"
                        else:
                            messages.append({"role": "user", "content": f"[{msg[0]}]: {msg[1]}"})
                    elif messages[-1]["role"] == "assistant":  # consecutive assistant messages
                        # Merge the assistant messages
                        messages[-1]["content"] = f"{messages[-1]['content']}\n{msg[1]}"
                    elif messages[-1]["role"] == "system":
                        messages.append({"role": "user", "content": f"[{msg[0]}]: {msg[1]}"})
                    else:
                        raise ValueError(f"Invalid role: {messages[-1]['role']}")

        response = self._get_response(messages, *args, **kwargs)

        # Remove the agent name if the response starts with it
        response = re.sub(rf"^\s*\[{agent_name}]:?", "", response).strip()

        return response
