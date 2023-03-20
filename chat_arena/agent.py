from typing import List
import re
from abc import ABC
import gradio as gr

from .backend import IntelligenceBackend, OpenAIChat
from .message import Message


class Agent(ABC):
    def __init__(self, name: str, *args, **kwargs):
        self.name = name


class Player(Agent):
    """
    Player of the game. It can takes the observation from the environment and return an action
    """

    def __init__(self, name: str, role_desc: str = None, env_desc: str = None,
                 backend: IntelligenceBackend = None, *args, **kwargs):
        super().__init__(name=name, *args, **kwargs)
        self.role_desc = role_desc
        self.env_desc = env_desc
        self.backend = backend

    def __call__(self, observation: List[Message]) -> str:
        """
        Call the agents to generate a response (equivalent to taking an action).
        """
        response = self.backend.query(
            agent_name=self.name,
            role_desc=self.role_desc,
            env_desc=self.env_desc,
            history_messages=observation,
            request_msg=None)
        return response

    def get_components(self):
        role_desc = gr.Textbox(show_label=False, lines=3, visible=True,
                               placeholder=f"Enter the role description for {self.name}",
                               value=self.role_desc)
        with gr.Accordion(f"{self.name} Parameters", open=False):
            temperature = gr.Slider(minimum=0, maximum=2.0, step=0.1, interactive=True,
                                    label=f"{self.name} temperature",
                                    value=self.backend.temperature)
            max_tokens = gr.Slider(minimum=10, maximum=500, step=10, interactive=True,
                                   label=f"{self.name} max tokens per response",
                                   value=self.backend.max_tokens)

        return role_desc, temperature, max_tokens

    @staticmethod
    def parse_components(components, name, start_idx):
        env_desc = components[0]
        role_desc = components[start_idx]
        temperature = components[start_idx + 1]
        max_tokens = components[start_idx + 2]
        new_player = Player(name, role_desc, env_desc,
                            backend=OpenAIChat(temperature, max_tokens))
        return new_player, start_idx + 3


class Moderator(Agent):
    """
    A special type of agent that moderates the conversation (and is usually used as part of environment).
    """

    def __init__(self, role_desc: str = None, env_desc: str = None,
                 backend: IntelligenceBackend = None, terminal_condition: str = None, *args, **kwargs):

        super().__init__(name="Moderator", *args, **kwargs)
        self.role_desc = role_desc
        self.env_desc = env_desc
        self.backend = backend
        self.terminal_condition = terminal_condition

    def is_terminal(self, history: List[Message], *args, **kwargs) -> bool:
        """
        check whether the conversation is over
        """
        response = self.backend.query(
            agent_name=self.name,
            role_desc=self.role_desc,
            env_desc=self.env_desc,
            history_messages=history,
            request_msg=Message(agent_name=self.name, content=self.terminal_condition, turn=-1),
            *args, **kwargs
        )

        if re.match(r"yes|y|yea|yeah|yep|yup|sure|ok|okay|alright", response, re.IGNORECASE):
            print(f"Decision: {response}. Conversation is ended by moderator.")
            return True
        else:
            return False

    def __call__(self, observation: List[Message]) -> str:
        """
        Call the moderator to generate an updated game state.
        """
        response = self.backend.query(
            agent_name=self.name,
            role_desc=self.role_desc,
            env_desc=self.env_desc,
            history_messages=observation,
            request_msg=None)
        return response

    def get_components(self):
        name = "Moderator"
        role_desc = gr.Textbox(show_label=False, lines=2, visible=True,
                               placeholder=f"Enter the role description for {name}",
                               value=self.role_desc)
        with gr.Accordion(f"{name} Advanced Parameters", open=False):
            terminal_condition = gr.Textbox(show_label=False, lines=2, visible=True,
                                            placeholder="Enter the end criteria for the conversation",
                                            value=self.terminal_condition)
            temperature = gr.Slider(minimum=0, maximum=2.0, step=0.1, interactive=True,
                                    label=f"{name} temperature", value=self.backend.temperature)
            max_tokens = gr.Slider(minimum=20, maximum=1000, step=10, interactive=True,
                                   label=f"{name} max tokens per response",
                                   value=self.backend.max_tokens)

        return role_desc, terminal_condition, temperature, max_tokens

    @staticmethod
    def parse_components(components, start_idx):
        env_desc = components[0]
        role_desc = components[start_idx]
        terminal_condition = components[start_idx + 1]
        temperature = components[start_idx + 2]
        max_tokens = components[start_idx + 3]

        new_moderator = Moderator(role_desc, env_desc,
                                  backend=OpenAIChat(temperature, max_tokens),
                                  terminal_condition=terminal_condition)
        return new_moderator, start_idx + 4
