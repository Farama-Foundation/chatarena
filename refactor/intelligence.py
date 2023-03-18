from typing import List, Dict, Tuple, Union
from refactor.message import Message
import openai

EOS = ("<EOS>", "[EOS]", "(EOS)")  # End of sentence token

class IntelligenceSource():
    def query(self, agent_name: str, background_info: str, visible_history: List[Message], request: str,
              temperature=None, max_tokens=None) -> str:
        """
        """
        pass


class Humand(IntelligenceSource):
    pass


class OpenAIChat(IntelligenceSource):
    """
    Interface to the ChatGPT style model with system, user, assistant roles seperation
    """
    def __init__(self, temperature, max_tokens, model_name="gpt-3.5-turbo"):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model_name
        self.stop = EOS

    def get_response(self, messages, temperature=None, max_tokens=None):
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature, max_tokens=max_tokens, stop=self.stop)

        response = completion.choices[0]['message']['content']
        return response


    def query(self, agent_name: str, background_info: str, visible_history: List[Message], request: str,
              temperature=None, max_tokens=None) -> str:
        """
        format the input and call the ChatGPT/GPT-4 API
        args:
            agent_name: the name of the agent
            background_info: the background information of the agent
            visible_history: the history of the conversation, or the observation for the agent
            request: the request for the chatGPT
        """
        conversations = []
        for i, message in enumerate(visible_history):
            if message.agent_name == agent_name:
                conversations.append({"role": "assistant", "content": message.content})
            else:
                # Since there are more than one player, we need to distinguish between the players
                conversations.append({"role": "user", "content": f"[{message.agent_name}]: {message.content}"})

        system_prompt = [{"role": "system", "content": background_info}]
        if request:
            request_prompt = [{"role": "system", "content": request}]
        else:
            request_prompt = []

        response = self.get_response(system_prompt+conversations+request_prompt,
                                     temperature=temperature,
                                     max_tokens=max_tokens)
        return response

