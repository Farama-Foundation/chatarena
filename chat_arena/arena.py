from typing import List

from .agent import Player
from .environments import Environment, TimeStep, load_environment
from .backend import Human


class Arena():
    """
    Utility class that manages the game environment and players
    """

    def __init__(self, players: List[Player], environment: Environment):
        self.players = players
        self.environment = environment
        self.current_timestep = self.environment.reset()
        self._name2player = {player.name: player for player in self.players}

    @property
    def num_players(self):
        return len(self.players)

    def step(self) -> TimeStep:
        """
        Take a step in the game: one player takes an action and the environment updates
        """
        player_name = self.environment.get_next_player()
        player = self._name2player[player_name]  # get the player object
        observation = self.environment.get_observation(player_name)  # get the observation for the player
        action = player(observation)  # take an action
        timestep = self.environment.step(player_name, action)  # update the environment
        return timestep

    def next_is_human(self):
        """
        check if the next player is human
        """
        player_name = self.environment.get_next_player()
        player = self._name2player[player_name]
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
    def from_config(cls, config):
        """
        create an arena from a config
        """
        # Load the players
        players = []
        for player_config in config["players"]:
            # Add env_desc to the player config if it is not there
            if "env_desc" not in player_config:
                player_config["env_desc"] = config["environment"]["env_desc"]

            player = Player.from_config(player_config)
            players.append(player)

        # Load the environment
        env = load_environment(config["environment"])

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
