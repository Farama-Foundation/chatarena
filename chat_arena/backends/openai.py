from typing import List
import os
import openai

from .base import IntelligenceBackend
from ..message import Message
from ..config import BackendConfig

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Default config follows the OpenAI playground
OPENAI_CHAT_DEFAULT_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 256,
    "model": "gpt-3.5-turbo"
}

STOP = ("<EOS>", "[EOS]", "(EOS)")  # End of sentence token


class OpenAIChat(IntelligenceBackend):
    """
    Interface to the ChatGPT style model with system, user, assistant roles separation
    """
    stateful = False
    type_name = "openai-chat"

    def __init__(self, config: BackendConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        # If temperature, max_tokens, or model are not specified, use the default values
        for key, value in OPENAI_CHAT_DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = value

    def _get_response(self, messages, *args, **kwargs):
        # Make a deepcopy of the config to avoid modifying the original config
        config = self.config.deepcopy()
        # update the config with the new values
        config.update(*args, **kwargs)

        completion = openai.ChatCompletion.create(
            model=config.model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            stop=STOP
        )

        response = completion.choices[0]['message']['content']
        response = response.strip()
        return response

    def _hidden_prompt(self, agent_name: str):
        stop_prompt = "You will end your answer with <EOS>"
        remember_your_role_prompt = f"Remember that your are {agent_name}. Do not pretend to be someone else."
        other_player_tags = "Messages from other players will be tagged with [player_name]."
        do_not_output_tags = "However, you do not need to output your own tag in your answer, despite others may do that."

        return {"role": "system", "content": "\n".join([stop_prompt, remember_your_role_prompt,
                                                        other_player_tags, do_not_output_tags])}

    def query(self, agent_name: str, role_desc: str, env_desc: str,
              history_messages: List[Message], request_msg: Message = None,
              *args, **kwargs) -> str:
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

        system_prompt = [
            {"role": "system", "content": env_desc},
            {"role": "system", "content": role_desc},
            self._hidden_prompt(agent_name),
        ]

        if request_msg:
            request_prompt = [{"role": "system", "content": request_msg.content}]
        else:
            request_prompt = []

        response = self._get_response(system_prompt + conversations + request_prompt, *args, **kwargs)

        # Remove the prefix if the response starts with it
        prefix = f"[{agent_name}]:"
        if response.startswith(prefix):
            response = response[len(prefix):].strip()

        return response
