from typing import List, Union
from dataclasses import dataclass
from uuid import uuid1
import time

from .base import Agent

import hashlib


def _hash(input: str):
    hex_dig = hashlib.sha256(input.encode()).hexdigest()
    return hex_dig


@dataclass
class Message:
    role: Agent
    content: str
    turn: int = None
    timestamp: int = time.time_ns()
    visible_to: Union[None, str, List[Agent]] = "all"

    def get_receivers(self, all_agents: List[Agent]):
        receivers = []
        if self.visible_to is None:
            return []
        elif isinstance(self.visible_to, str):
            if self.visible_to == "all":
                receivers = all_agents
            else:
                receivers = [agent for agent in all_agents if self.visible_to in agent.name]
        elif isinstance(self.visible_to, list):
            receivers = self.visible_to

        # Exclude the sender itself from the receivers
        receivers = [agent for agent in receivers if agent != self.role]
        return receivers

    @property
    def msg_id(self):
        # Generate a unique message id given the content, timestamp and role
        return _hash(f"msg: {self.content}\ntimestamp: {str(self.timestamp)}\nrole: {self.role.name}")


class MessagePool:
    """
    A message pool to manage the messages. This allows a unified treatment of the visibility of the messages.
    Draft design:
    The message pool is a list of (named) tuples, where each tuple has (turn, role, content).

    There should be two potential configurations for step definition: multiple players can act in the same turn (rock-paper-scissors).
    The agent can only see the messages that
    1) before the current turn, and
    2) visible to the current role
    """

    conversation_id: str

    def __init__(self):
        self.message_pool: List[Message] = []
        self.conversation_id = str(uuid1())  # TODO: generate a UUID for the conversation

    def append_message(self, message: Message):
        self.message_pool.append(message)

    @property
    def last_turn(self):
        if len(self.message_pool) == 0:
            return 0
        else:
            return self.message_pool[-1].turn

    def reset(self):
        self.message_pool = []

    def get_visible_messages(self, recv_agent: Agent, all_agents: List[Agent], turn: int = None):
        """
        Get the visible messages to the current role.

        then format the chat gpt input list (of dict) from the messages.
        each dictionary has the following keys: role, content
        the self messages will have the role "assistant", and the env messages will have the role "user"
        """
        if turn is None:
            turn = self.last_turn

        visible_messages = []
        for message in self.message_pool:
            if message.turn < turn:  # only messages before the current turn are visible (to avoid seeing parallel messages)
                if recv_agent == message.role or recv_agent in message.get_receivers(all_agents):
                    visible_messages.append(message)

        return visible_messages
