from dataclasses import dataclass
from abc import ABC
from typing import List

from ..message import Message
from ..agent import Agent


@dataclass
class TimeStep():
    observation: List[Message]
    reward: List[float]
    terminal: bool


class Environment(ABC):
    """
    The environment that the agents interacts with.
    """

    def __init__(self, player_names: List[str], env_desc: str):
        self.player_names = player_names
        self.env_desc = env_desc

    @classmethod
    def from_config(cls, config: dict):
        pass

    def to_config(self) -> dict:
        pass

    def get_next_player(self) -> str:
        """
        get name of the next player
        """
        pass

    def get_observation(self, player_name=None) -> List[Message]:
        """
        get observation for the player
        """
        pass

    def print(self):
        pass

    def step(self, player_name: str, action: str) -> TimeStep:
        """
        step function that is called by the arena
        Args:
            player_name: the name of the player
            action: the action that the agents wants to take
        Returns:
            timestep: the timestep that contains the observation, reward and done
        """
        pass

    def check_action(self, action: str, agent_name: str) -> bool:
        """
        check whether the action is valid
        """
        pass

    def reset(self):
        """
        reset the environment
        """
        pass

    def get_zero_rewards(self):
        return [0 for _ in self.player_names]
