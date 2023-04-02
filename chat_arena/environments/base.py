from dataclasses import dataclass
from typing import List, Dict, Union
from abc import abstractmethod

from ..message import Message
from ..agent import Player
from ..utils import AttributedDict
from ..config import EnvironmentConfig, Configurable


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

    def __init__(self, config: EnvironmentConfig, *args, **kwargs):
        # Check the backend_type matches the class type_name
        assert config["env_type"] == self.__class__.type_name

        super().__init__(config=config, *args, **kwargs)
        self._players = []

    def __init_subclass__(cls, **kwargs):
        # check if the subclass has the required attributes
        for required in ('type_name',):
            if getattr(cls, required) is None:
                raise TypeError(f"Can't instantiate abstract class {cls.__name__} without {required} attribute defined")

        return super().__init_subclass__(**kwargs)

    @abstractmethod
    def reset(self):
        """
        reset the environment
        """
        pass

    def register_players(self, players: Union[Player, List[Player]]):
        """
        register the players
        """
        if isinstance(players, Player):
            players = [players]

        # Check if the players are unique and not already registered, then add them to the list
        for player in players:
            assert isinstance(player, Player)
            if player.name in self.player_names:
                raise ValueError(f"Player {player.name} already registered")

            # Check the player's env_desc matches the environment's env_desc
            assert player.config.env_desc == self.config.env_desc, \
                f"Player {player.name} env_desc {player.config.env_desc} does not match environment env_desc {self.config.env_desc}"

            self._players.append(player)

    @property
    def players(self) -> List[Player]:
        """
        get the players
        """
        return self._players

    @property
    def player_names(self) -> List[str]:
        """
        get the player names
        """
        return [player.name for player in self.players]

    @property
    def num_players(self) -> int:
        """
        get the number of players
        """
        return len(self.players)

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
    def check_action(self, action: str, player: Player) -> bool:
        """
        check whether the action is valid
        """
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        """
        check whether the environment is in terminal state
        """
        pass

    def get_zero_rewards(self) -> Dict[str, float]:
        return {player_name: 0. for player_name in self.player_names}
