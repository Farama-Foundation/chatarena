import unittest
from unittest import TestCase
import logging

from chatarena.backends.hf_transformers import TransformersConversational
from chatarena.config import BackendConfig
from chatarena.message import Message

# set logger level to info
logging.basicConfig(level=logging.INFO)


class TestHFTransformers(TestCase):
    def test_transformers_conv_1(self):
        backend = TransformersConversational(config=BackendConfig(
            backend_type="transformers:conversational",
            model="facebook/blenderbot-400M-distill"))

        history_messages = [
            Message(agent_name="User",
                    content="Hello, I want to cook pasta, can you give me a recipe?", turn=1),
        ]

        response = backend.query(
            agent_name="Chatbot",
            role_desc="You are a chatbot that can talk to you about anything.",
            env_desc="You are chatting with a human.",
            history_messages=history_messages,
        )
        logging.info(response)
        self.assertTrue(True)

    def test_transformers_conv_2(self):
        backend = TransformersConversational(config=BackendConfig(
            backend_type="transformers:conversational",
            model="facebook/blenderbot-400M-distill"))

        history_messages = [
            Message(agent_name="User",
                    content="Hello, I want to cook pasta, can you give me a recipe?", turn=1),
            Message(agent_name="Chatbot",
                    content="Sure, what kind of pasta do you like? I like spaghetti and meatballs.", turn=2),
            Message(agent_name="User",
                    content="I like Bucatini better. Could you suggest a recipe?", turn=3),
        ]

        response = backend.query(
            agent_name="Chatbot",
            role_desc="You are an expert in food.",
            env_desc="You are chatting with a human.",
            history_messages=history_messages,
        )
        logging.info(response)
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
