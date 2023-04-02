from typing import List, Union

from .base import TimeStep, Environment
from ..message import Message, MessagePool
from ..agent import Moderator, SIGNAL_END_OF_CONVERSATION
from ..config import EnvironmentConfig


class Conversation(Environment):
    """
    Turn-based fully observable conversation environment.
    Next speaker order is either parallel or round-robin.
    """
    type_name = "conversation"

    def __init__(self, config: EnvironmentConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self._require_fields_in_config(['env_desc', 'parallel'])

        # The "state" of the environment is maintained by the message pool
        self.message_pool = MessagePool()

        self._current_turn = 0
        self._next_player_idx = 0

    def reset(self):
        self._current_turn = 0
        self._next_player_idx = 0
        self.message_pool.reset()

        init_timestep = TimeStep(observation=[],
                                 reward=self.get_zero_rewards(),
                                 terminal=False)
        return init_timestep

    def print(self):
        self.message_pool.print()

    def get_next_player(self) -> str:
        """
        get the next player
        """
        return self.player_names[self._next_player_idx]

    def get_observation(self, player_name=None) -> List[Message]:
        """
        get observation for the player
        """
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=self._current_turn)

    def is_terminal(self) -> bool:
        """
        check if the conversation is over
        """
        # If the last message is the signal, then the conversation is over
        if self.message_pool.last_message.content == SIGNAL_END_OF_CONVERSATION:
            return True

    def step(self, player_name: str, action: str) -> TimeStep:
        """
        step function that is called by the arena
        Args:
            player_name: the name of the player that takes the action
            action: the action that the agents wants to take
        """
        message = Message(agent_name=player_name, content=action, turn=self._current_turn)
        self.message_pool.append_message(message)

        # Update the counters
        if not self.config.parallel or self._next_player_idx == 0:
            self._current_turn += 1
        self._next_player_idx = (self._next_player_idx + 1) % self.num_players

        timestep = TimeStep(observation=self.get_observation(),
                            reward=self.get_zero_rewards(),
                            terminal=self.is_terminal())  # Return all the messages
        return timestep


class ModeratedConversation(Conversation):
    """
    Turn-based fully observable conversation environment.
    Next speaker order is either parallel or round-robin.
    Moderator is a special agent that can see all messages and can decide whether the conversation is over.
    """

    type_name = "moderated_conversation"

    def __init__(self, config: EnvironmentConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self._require_fields_in_config(['moderator', 'moderator_visibility'])

        moderator_config = self.config.moderator
        self.moderator = Moderator(moderator_config)
        # Check the moderator's env_desc matches the environment's env_desc
        assert self.moderator.config.env_desc == self.config.env_desc, \
            f"Moderator's env_desc {self.moderator.config.env_desc} does not match the environment's env_desc {self.config.env_desc}"

    def step(self, player_name: str, action: str) -> TimeStep:
        """
        step function that is called by the arena
        Args:
            player_name: the name of the player that takes the action
            action: the action that the agents wants to take
        """
        message = Message(agent_name=player_name, content=action, turn=self._current_turn)
        self.message_pool.append_message(message)

        # Moderator's turn
        moderator_history = self.message_pool.get_all_messages()
        moderator_response = self.moderator(moderator_history)
        moderator_message = Message(agent_name=self.moderator.name,
                                    content=moderator_response,
                                    turn=self._current_turn,
                                    visible_to=self.config.moderator_visibility)
        self.message_pool.append_message(moderator_message)

        terminal = self.moderator.is_terminal(moderator_history) or self.is_terminal()

        # Update the counters
        if not self.config.parallel or self._next_player_idx == 0:
            self._current_turn += 1

        # Round-robin order for the next player
        self._next_player_idx = (self._next_player_idx + 1) % self.num_players

        timestep = TimeStep(observation=self.get_observation(),
                            reward=self.get_zero_rewards(),
                            terminal=terminal)  # Return all the messages
        return timestep
