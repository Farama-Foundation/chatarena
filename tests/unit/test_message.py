import unittest
from unittest import TestCase

from chatarena.message import MessagePool, Message


# Write a test case for the message pool
class TestMessagePool(TestCase):

    # Test the append message function
    def test_append_message_1(self):
        message_pool = MessagePool()
        p1_message = "I'm player 1"
        p2_message = "I'm player 2"
        message_pool.append_message(Message("player1", p1_message, 1, visible_to=["player2"]))
        message_pool.append_message(Message("player2", p2_message, 2, visible_to=["player1"]))

        self.assertEqual(message_pool.get_visible_messages("player1", 3)[0].content, p2_message)
        self.assertEqual(message_pool.get_visible_messages("player2", 2)[0].content, p1_message)


if __name__ == "__main__":
    unittest.main()
