import os
import unittest
import warnings
from unittest import TestCase

from chatarena import EXAMPLES_DIR
from chatarena.arena import Arena


class TestCLI(TestCase):
    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_1(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "nlp-classroom.json"))
        arena.launch_cli(max_steps=10, interactive=False)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_2(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "chameleon.json"))
        arena.launch_cli(max_steps=10, interactive=False)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_3(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "tic-tac-toe.json"))
        arena.launch_cli(max_steps=10, interactive=False)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_4(self):
        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "rock-paper-scissors.json")
        )
        arena.launch_cli(max_steps=10, interactive=False)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_5(self):
        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "nlp-classroom-3players.json")
        )
        arena.launch_cli(max_steps=10, interactive=False)

    @unittest.skip("TODO: fix failing test")
    def test_cli_6(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "pettingzoo_chess.json"))
        arena.launch_cli(max_steps=10, interactive=False)

    @unittest.skipIf(
        not os.environ.get("ANTHROPIC_API_KEY"),
        "Anthropic API key must be set to run this test.",
    )
    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_7(self):
        # Suppress ResourceWarning
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning
        )

        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "chatgpt_claude_ai_collaboration.json")
        )
        arena.launch_cli(max_steps=6, interactive=False)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_8(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "interview.json"))
        arena.launch_cli(max_steps=16, interactive=False)

    @unittest.skipIf(
        not os.environ.get("ANTHROPIC_API_KEY"),
        "Anthropic API key must be set to run this test.",
    )
    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_9(self):
        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "chatgpt_claude_ai_collaboration.json")
        )
        arena.launch_cli(max_steps=6, interactive=False)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_10(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "prisoners_dilemma.json"))
        arena.launch_cli(max_steps=3, interactive=False)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_cli_11(self):
        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "pettingzoo_tictactoe.json")
        )
        arena.launch_cli(max_steps=9, interactive=False)


if __name__ == "__main__":
    unittest.main()
