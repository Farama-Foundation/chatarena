from typing import List
import os
import re
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ..message import Message

try:
    import openai
except ImportError:
    is_openai_available = False
    logging.warning("openai package is not installed")
else:
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if openai.api_key is None:
        logging.warning("OpenAI API key is not set. Please set the environment variable OPENAI_API_KEY")
        is_openai_available = False
    else:
        is_openai_available = True

# Default config follows the OpenAI playground
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 256
DEFAULT_MODEL = "gpt-3.5-turbo"

STOP = ("<EOS>", "[EOS]", "(EOS)")  # End of sentence token


class OpenAIChat(IntelligenceBackend):
    """
    Interface to the ChatGPT style model with system, user, assistant roles separation
    """
    stateful = False
    type_name = "openai-chat"

    def __init__(self, temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS,
                 model: str = DEFAULT_MODEL, **kwargs):
        assert is_openai_available, "openai package is not installed or the API key is not set"
        super().__init__(temperature=temperature, max_tokens=max_tokens, model=model, **kwargs)

        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model

    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
    def _get_response(self, messages):
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=STOP
        )

        response = completion.choices[0]['message']['content']
        response = response.strip()
        return response

    def query(self, agent_name: str, role_desc: str, history_messages: List[Message], global_prompt: str = None,
              request_msg: Message = None, *args, **kwargs) -> str:
        """
        format the input and call the ChatGPT/GPT-4 API
        args:
            agent_name: the name of the agent
            role_desc: the description of the role of the agent
            env_desc: the description of the environment
            history_messages: the history of the conversation, or the observation for the agent
            request_msg: the request for the chatGPT
        """
        conversations = []
        for i, message in enumerate(history_messages):
            if message.agent_name == agent_name:
                conversations.append({"role": "assistant", "content": message.content})
            else:
                # Since there are more than one player, we need to distinguish between the players
                conversations.append({"role": "user", "content": f"[{message.agent_name}]: {message.content}"})

        if global_prompt:  # Prepend the global prompt if it exists
            system_prompt_str = f"{global_prompt.strip()}\n{role_desc}"
        else:
            system_prompt_str = role_desc
        system_prompt = {"role": "system", "content": system_prompt_str}

        if request_msg:
            request_prompt = [{"role": "user", "content": request_msg.content}]
        else:
            request_prompt = []

        response = self._get_response([system_prompt] + conversations + request_prompt, *args, **kwargs)

        # Remove the agent name if the response starts with it
        response = re.sub(rf"^\s*\[{agent_name}]:?", "", response).strip()

        return response
