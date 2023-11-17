from typing import List

from chatarena.config import EnvironmentConfig
from chatarena.environments import TimeStep
from chatarena.environments.base import Environment
from chatarena.message import MessagePool, Message


class Story(Environment):
    type_name = "Story"

    def __init__(self, player_names: List[str], **kwargs):
        super().__init__(player_names, **kwargs)
        self.message_pool = MessagePool()
        self._current_turn = 0
        self._controller_idx = 0
        self._next_player_idx = 0

    def reset(self):
        self._current_turn = 0
        self.message_pool.reset()

    def get_next_player(self) -> str:
        if self._current_turn == 0:
            return self.player_names[self._controller_idx]
        else:
            return self.player_names[self._next_player_idx]

    def get_observation(self, player_name=None) -> List[Message]:
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=self._current_turn)

    def print(self):
        pass

    def step(self, player_name: str, action: str) -> TimeStep:
        pass

    def check_action(self, action: str, player_name: str) -> bool:
        pass

    def is_terminal(self) -> bool:
        pass


