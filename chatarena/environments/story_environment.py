from typing import List, Union

from chatarena.config import EnvironmentConfig
from chatarena.environments import TimeStep
from chatarena.environments.base import Environment
from chatarena.message import MessagePool, Message
from chatarena.agent import SIGNAL_END_OF_CONVERSATION

PLAYER_TERMINAL = -1


class Story(Environment):
    type_name = "Story"

    def __init__(self, player_names: List[str], **kwargs):
        super().__init__(player_names, **kwargs)
        self.global_message_pool = MessagePool()
        self.scene_message_pool = MessagePool()
        self._current_stage = "init"
        self._next_stage = "init"
        self._current_turn = 0
        self._next_player_idx = 0

    def reset(self):
        self._current_stage = "init"
        self._next_stage = "init"
        self._current_turn = 0
        self.global_message_pool.reset()
        self.scene_message_pool.reset()

    def get_next_player(self) -> str:
        if self._current_stage == "init":
            return "Designer"
        elif self._current_stage == "pick":
            return "Controller"
        else:
            return self.player_names[self._next_player_idx]

    def get_observation(self, player_name=None) -> List[Message]:
        if player_name is None:
            return self.scene_message_pool.get_all_messages()
        else:
            return self.global_message_pool.get_visible_messages(player_name, turn=self._current_turn) + \
                self.scene_message_pool.get_visible_messages(player_name, turn=self._current_turn)

    def print(self):
        self.global_message_pool.print()
        self.scene_message_pool.print()

    # def _controller_speak(self, text: str, visible_to: Union[str, List[str]] = "all"):
    #     message = Message(agent_name="Controller", content=text, turn=self._current_turn, visible_to=visible_to)
    #     self.global_message_pool.append_message(message)

    def is_terminal(self) -> bool:
        """
        check if the conversation is over
        """
        # If the last message is the signal, then the conversation is over
        if self.scene_message_pool.last_message.content.startswith(SIGNAL_END_OF_CONVERSATION):
            return True
        if self.global_message_pool.last_message.content.startswith(SIGNAL_END_OF_CONVERSATION):
            return True
        return False

    @staticmethod
    def _parse_picked_player(text: str) -> str:
        name = text.split('Next: ')[1].split('.')[0]
        return name

    def step(self, player_name: str, action: str) -> TimeStep:
        self._current_stage = self._next_stage
        terminal = False
        if self._current_stage == "init":
            message = Message(agent_name=player_name, content=action, turn=self._current_turn)
            self.global_message_pool.append_message(message)
            self._next_stage = "pick"
        elif self._current_stage == "pick":
            self._next_player_idx = self.player_names.index(self._parse_picked_player(action))
            if self._next_player_idx == PLAYER_TERMINAL:
                self._next_stage = "end of scene"
            else:
                self._next_stage = "act"
        elif self._current_stage == "act":
            message = Message(agent_name=player_name, content=action, turn=self._current_turn)
            self.scene_message_pool.append_message(message)
            self._next_stage = "pick"
        elif self._current_stage == "end of scene":
            terminal = True
        terminal = terminal or self.is_terminal()
        timestep = TimeStep(observation=self.get_observation(), reward=self.get_zero_rewards(), terminal=terminal)
        return timestep

    def check_action(self, action: str, player_name: str) -> bool:
        if "As an AI language model" in action:  # GPT not act as the agent
            return False
        if player_name == "Controller" and self._parse_picked_player(action) not in self.player_names:
            return False
        return True

    def to_config(self) -> EnvironmentConfig:
        return super().to_config()
