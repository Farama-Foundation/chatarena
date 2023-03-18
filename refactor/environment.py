from refactor.message import Message, MessagePool
from dataclasses import dataclass
from refactor.agent import Agent, Player, Moderator
from refactor.intelligence import IntelligenceSource
from typing import List, Dict, Tuple, Union

@dataclass
class Timestep():
    observation: List[Message]
    reward: float
    terminal: bool


class Environment():
    """
    The environment that the agents interacts with.
    The moderator (if exists) is a special agent that drive the game dynamics
    """
    def get_next_player(self) -> Player:
        """
        get the next player
        """
        pass

    def step(self, action: str) -> Timestep:
        """
        step function that is called by the arena
        Args:
            action: the action that the agent wants to take
        Returns:
            timestep: the timestep that contains the observation, reward and done
        """
        pass

    def check_action(self, action: str, agent: Agent) -> bool:
        """
        check whether the action is valid
        """
        pass


class Conversation(Environment):
    """
    Turn-based fully observable conversation environment.
    Conversation can be either parallel or sequential.
    There is a moderator that decides weather the conversation is over according to the public prompts and moderator prompts.
    """
    def __init__(self,
                 moderator_intelligence_source: IntelligenceSource,
                 moderator_role_description: str,
                 public_prompt: str,
                 terminate_prompt: str,
                 parallel: bool,
                 max_turns: int,
                 auto_terminate: bool,
                 players: List[Player]):
        self.parallel = parallel
        self.max_turns = max_turns
        self.auto_terminate = auto_terminate
        self.players = players
        self.message_pool = MessagePool()
        self._current_turn = 0
        self._next_player_idx = 0
        self.moderator = Moderator(moderator_intelligence_source,
                                   public_prompt=public_prompt,
                                   private_prompt=moderator_role_description,
                                   terminate_prompt=terminate_prompt)

    def reset(self):
        self._current_turn = 0
        self._next_player_idx = 0
        self.message_pool = MessagePool()
        timestep = Timestep(observation=self.get_next_player_observation(), reward=0, terminal=False)
        return timestep


    def print_message_pool(self):
        self.message_pool.print()

    def get_next_player(self) -> Player:
        """
        get the next player
        """
        return self.players[self._next_player_idx]

    def get_next_player_observation(self) -> List[Message]:
        """
        get the next player's observation
        """
        return self.message_pool.get_visible_messages(self.get_next_player().name, turn=self._current_turn)

    def step(self, action: str) -> Timestep:
        """
        step function that is called by the arena
        Args:
            action: the action that the agent wants to take
        Returns:
            timestep: the timestep that contains the observation, reward and done
        """
        player = self.get_next_player()
        message = Message(player.name, action, turn=self._current_turn)
        self.message_pool.append_message(message)

        moderator_visible_messages = self.message_pool.get_visible_messages(self.moderator.name, turn=self._current_turn+1)
        moderator_message = Message(self.moderator.name,
                                    self.moderator.decide(moderator_visible_messages),
                                    turn=self._current_turn)
        self.message_pool.append_message(moderator_message)
        terminal = self.moderator.is_terminal(moderator_visible_messages)
        observation = self.get_next_player_observation()
        timestep = Timestep(observation=observation, reward=0, terminal=terminal)

        # update counters

        self._next_player_idx += 1

        if self._next_player_idx == len(self.players):
            self._current_player_idx = 0

        if self.parallel==False:
            self._current_turn += 1
        else:
            if self._next_player_idx == 0:
                self._current_turn += 1

        return timestep
