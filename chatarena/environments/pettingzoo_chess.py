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

    def get_next_player(self) -> str:
        return self.player_names[self.current_player]

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

    def step(self, player_name: str, action: str) -> TimeStep:
        assert player_name == self.get_next_player(), f"Wrong player! It is {self.get_next_player()} turn."
        self._moderator_speak("\n" + self.env.render())

        message = Message(agent_name=player_name, content=action, turn=self.turn)
        self.message_pool.append_message(message)
        # Convert the action to the AlphaZero format
        alphazero_move = action_string_to_alphazero_format(action, self.current_player)
        if alphazero_move == -1:
            raise ValueError(f"Invalid action: {action}")

        obs_dict, reward, terminal, truncation, info = self.env.last()
        self.env.step(alphazero_move)
        self._terminal = terminal  # Update the terminal state
        reward = {self.player_names[self.current_player]: reward,
                  self.player_names[1 - self.current_player]: 0}

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


def test_chess_environment():
    player_names = ["player1", "player2"]
    env = PettingzooChess(player_names)

    env.reset()
    assert env.get_next_player() == "player1"
    env.print()

    # Move sequence: 1. e4 e5 2. Nf3 Nc6
    moves = ["Move (4, 1) to (4, 3)", "Move (4, 6) to (4, 4)",
             "Move (6, 0) to (5, 2)", "Move (1, 7) to (2, 5)"]

    for i, move in enumerate(moves):
        assert env.check_action(move, env.get_next_player())
        timestep = env.step(env.get_next_player(), move)
        print(timestep.reward)
        print(timestep.terminal)
        env.print()


if __name__ == "__main__":
    env = chess_v5.env()

    # Test the conversion function with an example action string
    action = "Move (0, 1) to (0, 3)"
    alphazero_move = action_string_to_alphazero_format(action, 0)
    print(alphazero_move)

    test_chess_environment()
