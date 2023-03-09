from typing import List

from .agent import Agent, Player, Moderator
from .message import MessagePool


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
                 rotary_speaker: bool = True, max_turns: int = 10, auto_terminate: bool = False):
        self.message_pool = MessagePool()
        self.moderator = moderator
        self.players = players

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
        for agent in self.all_agents:
            agent.reset()

    def get_next_player(self, current_player: Player):
        """
        Get the next player to speak.

        The next player is determined by the moderator.
        """
        raise NotImplementedError

    def is_end(self):
        """
        Check if the conversation has ended.
        """
        raise NotImplementedError
