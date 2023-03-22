from typing import List
import re
from abc import ABC

from .backend import IntelligenceBackend
from .message import Message
# from .utils import load_backend


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

    @classmethod
    def from_config(cls, config: dict):
        name = config["name"]
        role_desc = config["role_desc"]
        env_desc = config["env_desc"]
        backend = load_backend(config["backend"])
        return cls(name=name, role_desc=role_desc, env_desc=env_desc, backend=backend)

    def to_config(self) -> dict:
        return {"name": self.name, "role_desc": self.role_desc, "env_desc": self.env_desc,
                "backend": self.backend.to_config()}

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

    # @staticmethod
    # def get_components(config):
    #     role_desc = gr.Textbox(show_label=False, lines=3, visible=True,
    #                            placeholder=f"Enter the role description for {config['name']}",
    #                            value=config["role_desc"])
    #     player_name = gr.Textbox(label="Player Name", value=config["name"], visible=False)
    #     backend_type = gr.Textbox(label="Backend Type", value=config["backend"]["backend_type"], visible=False)
    #
    #     with gr.Accordion(f"{config['name']} Backend Parameters", open=False):
    #         # Get the backend and call its get_components
    #         backend_cls = BACKEND_REGISTRY[config["backend"]["backend_type"]]
    #         backend_components = backend_cls.get_components(config["backend"])
    #
    #     return [role_desc, player_name, backend_type, *backend_components]
    #
    # @staticmethod
    # def parse_components(components, start_idx):
    #     env_desc = components[0]
    #     role_desc = components[start_idx]
    #     player_name = components[start_idx + 1]
    #     backend_type = components[start_idx + 2]
    #
    #     # Load the backend
    #     backend_cls = BACKEND_REGISTRY[backend_type]
    #     backend, end_idx = backend_cls.parse_components(components, start_idx + 3)
    #
    #     new_player = Player(player_name, role_desc, env_desc, backend=backend)
    #     return new_player, end_idx


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

    @classmethod
    def from_config(cls, config: dict):
        role_desc = config["role_desc"]
        env_desc = config["env_desc"]
        backend = load_backend(config["backend"])
        terminal_condition = config["terminal_condition"]
        return cls(role_desc=role_desc, env_desc=env_desc, backend=backend,
                   terminal_condition=terminal_condition)

    def to_config(self) -> dict:
        return {"role_desc": self.role_desc, "env_desc": self.env_desc,
                "backend": self.backend.to_config(),
                "terminal_condition": self.terminal_condition}

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

    # @staticmethod
    # def get_components(config):
    #     name = "Moderator"
    #     role_desc = gr.Textbox(show_label=False, lines=3, visible=True,
    #                            placeholder=f"Enter the role description for {name}",
    #                            value=config["role_desc"])
    #     backend_type = gr.Textbox(label="Backend Type", value=config["backend"]["backend_type"], visible=False)
    #     terminal_condition = gr.Textbox(show_label=False, lines=2, visible=True,
    #                                     placeholder="Enter the end criteria for the conversation",
    #                                     value=config["terminal_condition"])
    #
    #     with gr.Accordion(f"{name} Parameters", open=False):
    #         # Get the backend and call its get_components
    #         backend_cls = BACKEND_REGISTRY[config["backend"]["backend_type"]]
    #         backend_components = backend_cls.get_components(config["backend"])
    #
    #     return [role_desc, backend_type, terminal_condition, *backend_components]
    #
    # @staticmethod
    # def parse_components(components, start_idx):
    #     env_desc = components[0]
    #     role_desc = components[start_idx]
    #     backend_type = components[start_idx + 1]
    #     terminal_condition = components[start_idx + 2]
    #
    #     # Load the backend
    #     backend_cls = BACKEND_REGISTRY[backend_type]
    #     backend, end_idx = backend_cls.parse_components(components, start_idx + 3)
    #
    #     new_moderator = Moderator(role_desc, env_desc,
    #                               backend=backend, terminal_condition=terminal_condition)
    #     return new_moderator, end_idx
