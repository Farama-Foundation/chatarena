import re
from pettingzoo.classic import tictactoe_v3

from chatarena.environments.base import Environment, TimeStep
from typing import List, Union

from ..message import Message, MessagePool


def action_string_to_action(action: str) -> int:
    pattern = r"(X|O): \((\d), (\d)\)"
    match = re.match(pattern, action)

    if not match:
        return -1
    items = [item for item in match.groups()]
    coords = [int(coord) for coord in items[1:]]
    row, column = coords
    if row not in [1, 2, 3]:
        return -1
    if column not in [1, 2, 3]:
        return -1

    row = row - 1
    column = column - 1
    return row + column * 3


class PettingzooTicTacToe(Environment):
    type_name = "pettingzoo:tictactoe"

    def __init__(self, player_names: List[str], **kwargs):
        super().__init__(player_names=player_names, **kwargs)
        self.env = tictactoe_v3.env()

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

        message = Message(agent_name=player_name, content=action, turn=self.turn)
        self.message_pool.append_message(message)
        # Convert the action to the AlphaZero format
        action_index = action_string_to_action(action)
        if action_index == -1:
            raise ValueError(f"Invalid action: {action}")

        self.env.step(action_index)
        obs_dict, reward, terminal, truncation, info = self.env.last()

        self._terminal = terminal  # Update the terminal state
        reward = {self.player_names[self.current_player]: reward,
                  self.player_names[1 - self.current_player]: 0}

        self.current_player = 1 - self.current_player
        self.turn += 1
        self._moderator_speak("\n" + self.render_ansi(obs_dict["observation"]))

        return TimeStep(observation=self.get_observation(), reward=reward, terminal=terminal)

    def check_action(self, action: str, agent_name: str) -> bool:
        # This can be implemented depending on how you want to validate actions for a given agent
        action_index = action_string_to_action(action)
        if action_index == -1:
            return False
        elif self.env.last()[0]["action_mask"][action_index] == 0:
            return False
        else:
            return True

    def render_ansi(self, observation):
        string = ""
        observation = observation.transpose(1, 0, 2)
        for row in observation:
            string += "|"
            for column in row:
                symbol = "_"
                if column[self.current_player] == 1:
                    symbol = "X"
                elif column[1 - self.current_player] == 1:
                    symbol = "O"
                string += " " + symbol + " |"
            string += "\n"
        return string

    def print(self):
        obs_dict, reward, terminal, truncation, info = self.env.last()
        print(self.render_ansi(obs_dict["observation"]))
