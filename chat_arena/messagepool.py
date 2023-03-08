from collections import namedtuple
from typing import List

Message = namedtuple('Message', ['turn', 'role', 'content'])

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
    def __init__(self):
        self._pool = []

    def get_pool(self) -> List[Message]:
        return self._pool

    def append_message(self, message:str, role:str, increase_turn:bool):
        if len(self._pool) == 0:
            last_turn = 0
        else:
            last_turn = self._pool[-1].turn
        turn = last_turn + 1 if increase_turn else last_turn

        self._pool.append(Message(turn, role, message))

    def reset(self):
        self._pool = []

    def get_visible_messages(self, self_role:str, env_roles:List[str], turn:int):
        """
        Get the visible messages to the current role.

        then format the chat gpt input list (of dict) from the messages.
        each dictionary has the following keys: role, content
        the self messages will have the role "assistant", and the env messages will have the role "user"
        """
        visible_messages = []
        for message in self._pool:
            if message.turn <= turn:
                if message.role == self_role:
                    visible_messages.append({"role": "assistnat", "content": message.content})
                elif message.role in env_roles:
                    visible_messages.append({"role": "user", "content": message.content})
        return visible_messages


# Test case
if __name__ == "__main__":
    message_pool = MessagePool()
    p1_message = "I'm player 1"
    p2_message = "I'm player 2"
    message_pool.append_message(p1_message, "player1", True)
    message_pool.append_message(p2_message, "player2", True)
    api_inputs = message_pool.get_visible_messages("player1", ["player2"], 2)
    print(f"api_inputs for player1 is: {api_inputs}")

