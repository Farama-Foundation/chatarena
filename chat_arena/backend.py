from typing import List
from abc import abstractmethod
import os
import openai

from .message import Message

openai.api_key = os.environ.get("OPENAI_API_KEY")


class IntelligenceBackend:
    """An abstraction of the intelligence source of the agents."""

    @abstractmethod
    def query(self, agent_name: str, role_desc: str, env_desc: str,
              history_messages: List[Message], request_msg: Message = None,
              *args, **kwargs) -> str:
        pass


class HumanIntelligence(IntelligenceBackend):
    def query(self, *args, **kwargs) -> str:
        raise NotImplementedError


class OpenAIChat(IntelligenceBackend):
    """
    Interface to the ChatGPT style model with system, user, assistant roles seperation
    """

    def __init__(self, temperature, max_tokens, model_name="gpt-3.5-turbo"):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model_name
        self.stop = ("<EOS>", "[EOS]", "(EOS)")  # End of sentence token

    def _get_response(self, messages, temperature=None, max_tokens=None):
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature, max_tokens=max_tokens, stop=self.stop)

        response = completion.choices[0]['message']['content']
        response = response.strip()
        return response

    def query(self, agent_name: str, role_desc: str, env_desc: str,
              history_messages: List[Message], request_msg: Message = None,
              *args, **kwargs) -> str:
        """
        format the input and call the ChatGPT/GPT-4 API
        args:
            agent_name: the name of the agents
            role_desc: the description of the role of the agents
            env_desc: the description of the environment
            history_messages: the history of the conversation, or the observation for the agents
            request_msg: the request for the chatGPT
        """
        conversations = []
        for i, message in enumerate(history_messages):
            if message.agent_name == agent_name:
                conversations.append({"role": "assistant", "content": message.content})
            else:
                # Since there are more than one player, we need to distinguish between the players
                conversations.append({"role": "user", "content": f"[{message.agent_name}]: {message.content}"})

        system_prompt = [
            {"role": "system", "content": env_desc},
            {"role": "system", "content": role_desc},
        ]

        if request_msg:
            request_prompt = [{"role": "system", "content": request_msg.content}]
        else:
            request_prompt = []

        # To make ChatGPT be aware of its own role, append a message with its own name
        prefix = f"[{agent_name}]: "
        # request_prompt.append({"role": "assistant", "content": prefix})

        response = self._get_response(system_prompt + conversations + request_prompt,
                                      temperature=kwargs.get("temperature", None),
                                      max_tokens=kwargs.get("max_tokens", None))

        # Remove the prefix if the response starts with it
        if response.strip().startswith(prefix):
            response = response.strip()[len(prefix):]

        return response
