from typing import List
import re
from abc import ABC

from .backend import IntelligenceBackend
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


class Moderator(Agent):
    """
    A special type of agent that moderates the conversation.
    """

    def __init__(self, role_desc: str = None, env_desc: str = None,
                 backend: IntelligenceBackend = None, terminal_condition: str = None, *args, **kwargs):

        super().__init__(name="Moderator", *args, **kwargs)
        self.role_desc = role_desc
        self.env_desc = env_desc
        self.backend = backend
        self.terminate_prompt = terminal_condition

    def is_terminal(self, history: List[Message], *args, **kwargs) -> bool:
        """
        check whether the conversation is over
        """
        response = self.backend.query(
            agent_name=self.name,
            role_desc=self.role_desc,
            env_desc=self.env_desc,
            history_messages=history,
            request_msg=Message(agent_name=self.name, content=self.terminate_prompt, turn=-1),
            *args, **kwargs
        )

        if re.match(r"yes|y|yea|yeah|yep|yup|sure|ok|okay|alright", response, re.IGNORECASE):
            print(f"Decision: {response}. Conversation is ended by moderator.")
            return True
        else:
            return False
