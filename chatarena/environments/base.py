from dataclasses import dataclass
from typing import List, Dict
from abc import abstractmethod

from ..message import Message
from ..utils import AttributedDict
from ..config import Configurable, EnvironmentConfig


@dataclass
class TimeStep(AttributedDict):
    observation: List[Message]
    reward: Dict[str, float]
    terminal: bool


class Environment(Configurable):
    """
    The environment that the agents interacts with.
    """
    type_name = None

    @abstractmethod
    def __init__(self, player_names: List[str], **kwargs):
        super().__init__(player_names=player_names, **kwargs)  # registers the arguments with Configurable
        self.player_names = player_names

    def __init_subclass__(cls, **kwargs):
        # check if the subclass has the required attributes
        for required in ('type_name',):
            if getattr(cls, required) is None:
                cls.type_name = cls.__name__.lower()

        return super().__init_subclass__(**kwargs)

    @abstractmethod
    def reset(self):
        """
        reset the environment
        """
        pass

    def to_config(self) -> EnvironmentConfig:
        self._config_dict["env_type"] = self.type_name
        return EnvironmentConfig(**self._config_dict)

    @property
    def num_players(self) -> int:
        """
        get the number of players
        """
        return len(self.player_names)

    @abstractmethod
    def get_next_player(self) -> str:
        """
        get name of the next player
        """
        pass

    @abstractmethod
    def get_observation(self, player_name=None) -> List[Message]:
        """
        get observation for the player
        """
        pass

    @abstractmethod
    def print(self):
        """
        print the environment state
        """
        pass

    @abstractmethod
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

    @abstractmethod
    def check_action(self, action: str, player_name: str) -> bool:
        """
        check whether the action is valid
        """
        return True

    @abstractmethod
    def is_terminal(self) -> bool:
        """
        check whether the environment is in terminal state
        """
        pass

    def get_zero_rewards(self) -> Dict[str, float]:
        return {player_name: 0. for player_name in self.player_names}
