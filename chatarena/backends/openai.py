from typing import List
import os
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ..message import Message
from ..config import BackendConfig

try:
    import openai
except ImportError:
    is_openai_available = False
    logging.warning("OpenAI package is not installed")
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
        assert is_openai_available, "OpenAI package is not installed or the API key is not set"
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

    # def _hidden_prompt(self, agent_name: str):
    #     """
    #     The hidden prompt for the ChatGPT/GPT-4 API to improve the quality of the response.
    #     The prompts here are mainly to improve the understanding of agency.
    #     """
    #     stop_prompt = "You will end your answer with <EOS>"
    #     remember_your_role_prompt = f"Never pretend to be the other players."
    #     other_player_tags = "Messages from other players will be tagged with [player_name]."
    #     do_not_output_tags = "However, you do not need to output your name tag in your answer."
    #
    #     return {"role": "system", "content": "\n".join([stop_prompt, other_player_tags,
    #                                                     remember_your_role_prompt, do_not_output_tags])}

    def query(self, agent_name: str, prompt: str, history_messages: List[Message], global_prompt: str = None,
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

        # system_prompt_str = f"Your name is {agent_name}.\n{prompt}\n" \
        #                     f"Other instructions:\n{self._hidden_prompt(agent_name)}"

        if global_prompt:  # Prepend the global prompt if it exists
            system_prompt_str = f"{global_prompt.strip()}\n{prompt}"
        else:
            system_prompt_str = prompt
        system_prompt = {"role": "system", "content": system_prompt_str}

        if request_msg:
            request_prompt = [{"role": "user", "content": request_msg.content}]
        else:
            request_prompt = []

        response = self._get_response([system_prompt] + conversations + request_prompt, *args, **kwargs)

        # Remove the prefix if the response starts with it
        prefix = f"[{agent_name}]:"
        if response.startswith(prefix):
            response = response[len(prefix):].strip()

        return response
