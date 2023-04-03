from typing import List, Dict, Union
import uuid

from .agent import Player
from .environments import Environment, TimeStep, load_environment
from .backends import Human
from .config import ArenaConfig


class Arena:
    """
    Utility class that manages the game environment and players
    """

    def __init__(self, players: List[Player], environment: Environment):
        # Create a container for the players and environment and reset the game
        self.players = players
        self.environment = environment
        self.current_timestep = environment.reset()
        self.uuid = uuid.uuid4()  # Generate a unique id for the game

    @property
    def num_players(self):
        return self.environment.num_players

    @property
    def name_to_player(self) -> Dict[str, Player]:
        return {player.name: player for player in self.players}

    def reset(self) -> TimeStep:
        # Reset the environment
        self.current_timestep = self.environment.reset()
        # Reset the players
        for player in self.players:
            player.reset()
        # Reset the uuid
        self.uuid = uuid.uuid4()
        return self.current_timestep

    def step(self) -> TimeStep:
        """
        Take a step in the game: one player takes an action and the environment updates
        """
        player_name = self.environment.get_next_player()
        player = self.name_to_player[player_name]  # get the player object
        observation = self.environment.get_observation(player_name)  # get the observation for the player
        action = player(observation)  # take an action
        timestep = self.environment.step(player_name, action)  # update the environment
        return timestep

    def next_is_human(self):
        """
        check if the next player is human
        """
        player_name = self.environment.get_next_player()
        player = self.name_to_player[player_name]
        return isinstance(player.backend, Human)

    def run(self, num_steps: int = 1):
        """
        run the game for num_turns
        """
        for i in range(num_steps):
            timestep = self.step()
            if timestep.terminal:
                break

    @classmethod
    def from_config(cls, config: Union[str, ArenaConfig]):
        """
        create an arena from a config
        """
        # If config is a path, load the config
        if isinstance(config, str):
            config = ArenaConfig.load(config)

        # Load the players
        players = []
        for player_config in config.players:
            # Add env_desc to the player config if it is not there
            if "env_desc" not in player_config:
                player_config.env_desc = config.environment.env_desc

            player = Player.from_config(player_config)
            players.append(player)

        # Load the environment
        env = load_environment(config.environment)

        # Register the players with the environment
        env.register_players(players)
        # Check that the player names in environment agree with the players
        assert set(env.player_names) == set([player.name for player in players])

        return cls(players, env)

    def to_config(self) -> dict:
        """
        convert the arena to a config
        """
        return {
            "players": [player.to_config() for player in self.players],
            "environment": self.environment.to_config(),
        }

    def launch_cli(self, max_steps: int = None, interactive: bool = True):
        """
        launch the command line interface
        """
        from .ui.cli import ArenaCLI
        cli = ArenaCLI(self)
        cli.launch(max_steps=max_steps, interactive=interactive)
