from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Type

from ..config import Configurable, EnvironmentConfig
from ..message import Message
from ..utils import AttributedDict


@dataclass
class TimeStep(AttributedDict):
    """
    Represents a single step in time within the simulation.

    It includes observation, reward, and terminal state.

    Attributes:
        observation (List[Message]): A list of messages (observations) for the current timestep.
        reward (Dict[str, float]): A dictionary with player names as keys and corresponding rewards as values.
        terminal (bool): A boolean indicating whether the current state is terminal (end of episode).
    """

    observation: List[Message]
    reward: Dict[str, float]
    terminal: bool


class Environment(Configurable):
    """
    Abstract class representing an environment.

    It defines the necessary methods any environment must implement.

    Inherits from:
        Configurable: A custom class that provides methods to handle configuration settings.

    Attributes:
        type_name (str): Type of the environment, typically set to the lower case of the class name.

    Note:
        Subclasses should override and implement the abstract methods defined here.
    """

    type_name = None

    @abstractmethod
    def __init__(self, player_names: List[str], **kwargs):
        """
        Initialize the Environment.

        Parameters:
            player_names (List[str]): Names of the players in the environment.
        """
        super().__init__(
            player_names=player_names, **kwargs
        )  # registers the arguments with Configurable
        self.player_names = player_names

    def __init_subclass__(cls, **kwargs):
        """
        Automatically called when a subclass is being initialized.

        Here it's used to check if the subclass has the required attributes.
        """
        for required in ("type_name",):
            if getattr(cls, required) is None:
                cls.type_name = cls.__name__.lower()

        return super().__init_subclass__(**kwargs)

    @abstractmethod
    def reset(self):
        """
        Reset the environment to its initial state.

        Note:
            This method must be implemented by subclasses.
        """
        pass

    def to_config(self) -> EnvironmentConfig:
        self._config_dict["env_type"] = self.type_name
        return EnvironmentConfig(**self._config_dict)

    @property
    def num_players(self) -> int:
        """Get the number of players."""
        return len(self.player_names)

    @abstractmethod
    def get_next_player(self) -> str:
        """
        Return the name of the next player.

        Note:
            This method must be implemented by subclasses.

        Returns:
            str: The name of the next player.
        """
        pass

    @abstractmethod
    def get_observation(self, player_name=None) -> List[Message]:
        """
        Return observation for a given player.

        Note:
            This method must be implemented by subclasses.

        Parameters:
            player_name (str, optional): The name of the player for whom to get the observation.

        Returns:
            List[Message]: The observation for the player in the form of a list of messages.
        """
        pass

    @abstractmethod
    def print(self):
        """Print the environment state."""
        pass

    @abstractmethod
    def step(self, player_name: str, action: str) -> TimeStep:
        """
        Execute a step in the environment given an action from a player.

        Note:
            This method must be implemented by subclasses.

        Parameters:
            player_name (str): The name of the player.
            action (str): The action that the player wants to take.

        Returns:
            TimeStep: An object of the TimeStep class containing the observation, reward, and done state.
        """
        pass

    @abstractmethod
    def check_action(self, action: str, player_name: str) -> bool:
        """
        Check whether a given action is valid for a player.

        Note:
            This method must be implemented by subclasses.

        Parameters:
            action (str): The action to be checked.
            player_name (str): The name of the player.

        Returns:
            bool: True if the action is valid, False otherwise.
        """
        return True

    @abstractmethod
    def is_terminal(self) -> bool:
        """
        Check whether the environment is in a terminal state (end of episode).

        Note:
            This method must be implemented by subclasses.

        Returns:
            bool: True if the environment is in a terminal state, False otherwise.
        """
        pass

    def get_zero_rewards(self) -> Dict[str, float]:
        """
        Return a dictionary with all player names as keys and zero as reward.

        Returns:
            Dict[str, float]: A dictionary of players and their rewards (all zero).
        """
        return {player_name: 0.0 for player_name in self.player_names}

    def get_one_rewards(self) -> Dict[str, float]:
        """
        Return a dictionary with all player names as keys and one as reward.

        Returns:
            Dict[str, float]: A dictionary of players and their rewards (all one).
        """
        return {player_name: 1.0 for player_name in self.player_names}


ENV_REGISTRY: Dict[str, Type[Environment]] = {}


def register_env(cls: Type[Environment]) -> Type[Environment]:
    """
    Register an environment class.

    Parameters:
        cls (Type[Environment]): The class to register.

    Returns:
        Type[Environment]: The class that was registered.
    """
    ENV_REGISTRY[cls.type_name] = cls
    return cls
