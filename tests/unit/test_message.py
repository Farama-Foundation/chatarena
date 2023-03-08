from unittest import TestCase

from chat_arena.message import MessagePool

# Write a test case for the message pool
class TestMessagePool(TestCase):

    # Test the append message function
    def test_append_message_1(self):
        message_pool = MessagePool()
        message_pool.append_message("hello", "user", True)
        self.assertEqual(message_pool.get_pool()[0].content, "hello")
        self.assertEqual(message_pool.get_pool()[0].role, "user")
        self.assertEqual(message_pool.get_pool()[0].turn, 1)
        message_pool.append_message("hello", "user", False)
        self.assertEqual(message_pool.get_pool()[1].content, "hello")
        self.assertEqual(message_pool.get_pool()[1].role, "user")
        self.assertEqual(message_pool.get_pool()[1].turn, 1)
        message_pool.append_message("hello", "user", True)
        self.assertEqual(message_pool.get_pool()[2].content, "hello")
        self.assertEqual(message_pool.get_pool()[2].role, "user")
        self.assertEqual(message_pool.get_pool()[2].turn, 2)

    def test_append_message_2(self):
        message_pool = MessagePool()
        p1_message = "I'm player 1"
        p2_message = "I'm player 2"
        message_pool.append_message(p1_message, "player1", True)
        message_pool.append_message(p2_message, "player2", True)
        api_inputs = message_pool.get_visible_messages("player1", ["player2"], 2)
        self.assertEqual(api_inputs[0]["content"], p2_message)
