from typing import List, Union
from dataclasses import dataclass
import time
from uuid import uuid1
import hashlib


def _hash(input: str):
    hex_dig = hashlib.sha256(input.encode()).hexdigest()
    return hex_dig


@dataclass
class Message:
    agent_name: str
    content: str  # it can be an image or a text
    turn: int
    timestamp: int = time.time_ns()
    visible_to: Union[str, List[str]] = 'all'
    msg_type: str = "text"
    logged: bool = False  # Whether the message is logged in the database

    @property
    def msg_hash(self):
        # Generate a unique message id given the content, timestamp and role
        return _hash(
            f"agent: {self.agent_name}\ncontent: {self.content}\ntimestamp: {str(self.timestamp)}\nturn: {self.turn}\nmsg_type: {self.msg_type}")


class MessagePool():
    """
    A message pool to manage the messages. This allows a unified treatment of the visibility of the messages.
    Draft design:
    The message pool is a list of (named) tuples, where each tuple has (turn, role, content).

    There should be two potential configurations for step definition: multiple players can act in the same turn (rock-paper-scissors).
    The agents can only see the messages that
    1) before the current turn, and
    2) visible to the current role
    """

    def __init__(self):
        self.conversation_id = str(uuid1())
        self._messages: List[Message] = []  # TODO: for the sake of thread safety, use a queue instead
        self._last_message_idx = 0

    def reset(self):
        self._messages = []

    def append_message(self, message: Message):
        self._messages.append(message)

    def print(self):
        for message in self._messages:
            print(f"[{message.agent_name}->{message.visible_to}]: {message.content}")

    @property
    def last_turn(self):
        if len(self._messages) == 0:
            return 0
        else:
            return self._messages[-1].turn

    @property
    def last_message(self):
        if len(self._messages) == 0:
            return None
        else:
            return self._messages[-1]

    def get_all_messages(self) -> List[Message]:
        return self._messages

    def get_visible_messages(self, agent_name, turn: int) -> List[Message]:
        """
        get the messages that are visible to the agents before the specified turn
        """

        # Get the messages before the current turn
        prev_messages = [message for message in self._messages if message.turn < turn]

        visible_messages = []
        for message in prev_messages:
            if message.visible_to == "all" or agent_name in message.visible_to or agent_name == "Moderator":
                visible_messages.append(message)
        return visible_messages
