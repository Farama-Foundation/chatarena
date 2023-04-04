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

    def __init__(self, players: List[Player], environment: Environment, global_prompt: str = None):
        # Create a container for the players and environment and reset the game
        self.players = players
        self.environment = environment
        self.global_prompt = global_prompt

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

        global_prompt = config.get("global_prompt", None)

        # Create the players
        players = []
        for player_config in config.players:
            # Add public_prompt to the player config
            if global_prompt is not None:
                player_config["global_prompt"] = global_prompt

            player = Player.from_config(player_config)
            players.append(player)

        # Check that the player names are unique
        player_names = [player.name for player in players]
        assert len(player_names) == len(set(player_names)), "Player names must be unique"

        # Create the environment
        config.environment["player_names"] = player_names  # add the player names to the environment config
        env = load_environment(config.environment)

        return cls(players, env, global_prompt=global_prompt)

    def to_config(self) -> dict:
        """
        convert the arena to a config
        """
        return {
            "players": [player.to_config() for player in self.players],
            "environment": self.environment.to_config(),
            "global_prompt": self.global_prompt
        }

    def launch_cli(self, max_steps: int = None, interactive: bool = True):
        """
        launch the command line interface
        """
        from .ui.cli import ArenaCLI
        cli = ArenaCLI(self)
        cli.launch(max_steps=max_steps, interactive=interactive)
