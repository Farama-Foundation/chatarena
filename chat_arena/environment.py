from dataclasses import dataclass
from typing import List, Union
from abc import ABC

from .message import Message, MessagePool
from .agent import Agent, Moderator


@dataclass
class TimeStep():
    observation: List[Message]
    reward: float
    terminal: bool


class Environment(ABC):
    """
    The environment that the agents interacts with.
    """

    def get_next_player(self) -> str:
        """
        get name of the next player
        """
        pass

    def get_observation(self, player_name) -> List[Message]:
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

    def check_action(self, action: str, agent: Agent) -> bool:
        """
        check whether the action is valid
        """
        pass

    def reset(self):
        """
        reset the environment
        """
        pass


class Conversation(Environment):
    """
    Turn-based fully observable conversation environment.
    Next speaker order is either parallel or round-robin.
    """

    def __init__(self, player_names: List[str], env_desc: str, parallel: bool = False):
        self.player_names = player_names
        self.message_pool = MessagePool()
        self.env_desc = env_desc
        self.parallel = parallel  # if True, all players speak at the same time

        self._current_turn = 0
        self._next_player_idx = 0

    def reset(self):
        self._current_turn = 0
        self._next_player_idx = 0
        self.message_pool.reset()

        init_timestep = TimeStep(observation=[], reward=0, terminal=False)
        return init_timestep

    def print(self):
        self.message_pool.print()

    def get_next_player(self) -> str:
        """
        get the next player
        """
        return self.player_names[self._next_player_idx]

    def get_observation(self, player_name=None) -> List[Message]:
        """
        get observation for the player
        """
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=self._current_turn)

    def step(self, player_name: str, action: str) -> TimeStep:
        """
        step function that is called by the arena
        Args:
            player_name: the name of the player that takes the action
            action: the action that the agents wants to take
        """
        message = Message(agent_name=player_name, content=action, turn=self._current_turn)
        self.message_pool.append_message(message)

        # Update the counters
        if not self.parallel or self._next_player_idx == 0:
            self._current_turn += 1
        self._next_player_idx = (self._next_player_idx + 1) % len(self.player_names)

        timestep = TimeStep(observation=self.get_observation(), reward=0, terminal=False)  # Return all the messages
        return timestep
