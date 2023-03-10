from typing import List
import logging
from enum import Enum
import random

from .base import Agent
from .agent import Player, Moderator
from .message import MessagePool, Message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class NextSpeakerStrategy(Enum):
    ROTARY = "Round-robin"
    RANDOM = "Random"
    MODERATOR = "Moderator"
    PARALLEL = "Parallel"

    @staticmethod
    def options():
        return [strategy.value for strategy in NextSpeakerStrategy]

    @staticmethod
    def get_strategy(strategy: str):
        for s in NextSpeakerStrategy:
            if s.value == strategy:
                return s
        raise ValueError(f"Invalid strategy: {strategy}")


# Environment class that models the environment in which the conversation takes place
class Arena:
    """
    The Arena environment class that models the environment in which the conversation takes place.

    The environment is responsible for
    1) managing the message pool
    2) managing the agents
    3) managing the conversation state
    """

    def __init__(self, players: List[Player], moderator: Moderator = None,
                 next_speaker_strategy: str = NextSpeakerStrategy.ROTARY.value, max_turns: int = 10,
                 auto_terminate: bool = False):
        self.message_pool = MessagePool()
        self.moderator = moderator
        self.players = players
        self.next_speaker_strategy = NextSpeakerStrategy.get_strategy(next_speaker_strategy)
        self.max_turns = max_turns
        self.auto_terminate = auto_terminate
        self.turn_counter = 0

    @property
    def num_players(self):
        return len(self.players)

    @property
    def all_agents(self) -> List[Agent]:
        return self.players + [self.moderator]

    def add_player(self, player: Player):
        self.players.append(player)

    def get_agent(self, agent_name: str):
        for agent in self.all_agents:
            if agent.name == agent_name:
                return agent

    def get_agent_by_role(self, role: str):
        for agent in self.all_agents:
            if role in agent.name:
                return agent

    def reset(self):
        self.message_pool.reset()
        self.turn_counter = 0

    def get_next_players(self) -> List[Player]:
        """
        Get the next player to speak.
        """
        if self.next_speaker_strategy == NextSpeakerStrategy.ROTARY:
            next_player_idx = self.turn_counter % self.num_players
            next_players = [self.players[next_player_idx]]
        elif self.next_speaker_strategy == NextSpeakerStrategy.MODERATOR:
            # Ask the moderator who should speak next
            next_player_idx = self.moderator.get_next_player(self)
            if next_player_idx is None:
                next_player_idx = self.turn_counter % self.num_players
                logger.warning(f"Resorting to round-robin order: {next_player_idx}")
            next_players = [self.players[next_player_idx]]
        elif self.next_speaker_strategy == NextSpeakerStrategy.RANDOM:
            next_players = [random.sample(self.players, 1)[0]]
        elif self.next_speaker_strategy == NextSpeakerStrategy.PARALLEL:
            next_players = self.players
        else:
            raise ValueError(f"Invalid next_speaker_strategy: {self.next_speaker_strategy}")

        return next_players

    def is_terminal(self):
        """
        Check if the conversation has ended.
        """
        if self.auto_terminate:  # Ask the moderator if the conversation has ended
            return self.moderator.is_terminal(self)
        else:
            return self.turn_counter >= self.max_turns

    # Get the visible state of the conversation for a particular player
    def get_visible_history(self, agent: Agent, turn: int = None) -> dict:
        """
        Get the visible state of the conversation for a particular agent.
        """
        if turn is None:
            turn = self.turn_counter
        return self.message_pool.get_visible_messages(agent, self.all_agents, turn)

    def step(self):
        """
        Take a step in the conversation.
        """
        # Get the next player to speak
        next_players = self.get_next_players()
        for idx, player in enumerate(next_players):
            # Take a step in the conversation and get the player's message
            player_msg = player.step(self, turn=self.turn_counter)  # assign turn number to the message

            self.message_pool.append_message(player_msg)

        moderator_msg = self.moderator.step(self, turn=self.turn_counter+1)  # Moderator takes an action
        self.message_pool.append_message(moderator_msg)

        self.turn_counter += 1  # Increment the turn counter
