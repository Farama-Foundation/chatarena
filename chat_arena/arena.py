from typing import List

from .agent import Player
from .backend import OpenAIChat
from .environment import Environment, Conversation, TimeStep


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

    def run(self, num_turns: int = 100):
        """
        run the game for num_turns
        """
        for i in range(num_turns):
            timestep = self.step()
            if timestep.terminal:
                break

    @staticmethod
    def from_config(config):
        env_config = config["environment"]

        players = []
        for player_idx, player_config in enumerate(config["players"]):
            player = Player(
                name=f"Player {player_idx + 1}",
                role_desc=player_config["role_desc"],
                env_desc=env_config["env_desc"],
                backend=OpenAIChat(
                    temperature=player_config["temperature"],
                    max_tokens=player_config["max_tokens"],
                    model_name=player_config["model_name"],
                )
            )
            players.append(player)

        env = Conversation(
            player_names=[player.name for player in players],
            env_desc=env_config["env_desc"],
            parallel=env_config["parallel"],
        )
        return Arena(players, env)

    @staticmethod
    def save_config(config):
        raise NotImplementedError()
