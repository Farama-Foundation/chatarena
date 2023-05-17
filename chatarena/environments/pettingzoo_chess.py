from pettingzoo.classic.chess.chess_utils import *
import re
from pettingzoo.classic import chess_v5

from chatarena.environments.base import Environment, TimeStep
from typing import List, Dict, Union

from ..message import Message, MessagePool
from ..config import EnvironmentConfig


def action_string_to_alphazero_format(action: str, player_index: int) -> int:
    pattern = r"Move \((\d), (\d)\) to \((\d), (\d)\)"
    match = re.match(pattern, action)

    if not match:
        return -1

    coords = [int(coord) for coord in match.groups()]
    x1, y1, x2, y2 = coords

    if player_index == 1:
        x1, y1, x2, y2 = 7 - x1, 7 - y1, 7 - x2, 7 - y2
    move = chess.Move(from_square=8 * y1 + x1, to_square=8 * y2 + x2, promotion=None)
    move_plane = get_move_plane(move)

    return x1 * 8 * 73 + y1 * 73 + move_plane


class PettingzooChess(Environment):
    type_name = "pettingzoo:chess"

    def __init__(self, player_names: List[str], **kwargs):
        super().__init__(player_names=player_names, **kwargs)
        self.env = chess_v5.env(render_mode="ansi")

        # The "state" of the environment is maintained by the message pool
        self.message_pool = MessagePool()
        self._terminal = False
        self.reset()

    def reset(self):
        self.env.reset()
        self.current_player = 0
        self.turn = 0
        self.message_pool.reset()

        obs_dict, reward, terminal, truncation, info = self.env.last()
        observation = self.get_observation()
        self._terminal = terminal
        return TimeStep(observation=observation, reward=reward, terminal=terminal)

    def get_next_players(self) -> List[str]:
        return [self.player_names[self.current_player]]

    def get_observation(self, player_name=None) -> List[Message]:
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=self.turn + 1)

    def _moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all"):
        """
        moderator say something
        """
        message = Message(agent_name="Moderator", content=text, turn=self.turn, visible_to=visible_to)
        self.message_pool.append_message(message)

    def is_terminal(self) -> bool:
        return self._terminal

    def step(self, player_actions: str) -> TimeStep:
        assert player_actions == self.get_next_players()[0], f"Wrong player! It is {self.get_next_players()[0]} turn."
        self._moderator_speak("\n" + self.env.render())

        message = Message(agent_name=player_actions, content=action, turn=self.turn)
        self.message_pool.append_message(message)
        # Convert the action to the AlphaZero format
        alphazero_move = action_string_to_alphazero_format(action, self.current_player)
        if alphazero_move == -1:
            raise ValueError(f"Invalid action: {action}")

        obs_dict, reward, terminal, truncation, info = self.env.last()
        print(obs_dict["action_mask"])
        self.env.step(alphazero_move)
        self._terminal = terminal  # Update the terminal state
        reward = reward  # TODO: bug here, reward needs to be a dict

        self.current_player = 1 - self.current_player
        self.turn += 1

        return TimeStep(observation=self.get_observation(), reward=reward, terminal=terminal)

    def check_action(self, action: str, agent_name: str) -> bool:
        # This can be implemented depending on how you want to validate actions for a given agent
        alphazero_move = action_string_to_alphazero_format(action, self.current_player)
        if alphazero_move == -1:
            return False
        elif self.env.last()[0]["action_mask"][alphazero_move] == 0:
            return False
        else:
            return True

    def print(self):
        print(self.env.render())
