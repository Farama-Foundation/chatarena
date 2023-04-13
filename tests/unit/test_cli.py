import unittest
from unittest import TestCase

from chatarena.arena import Arena

import warnings


class TestArenaCLI(TestCase):
    def test_cli_1(self):
        arena = Arena.from_config("examples/nlp-classroom.json")
        arena.launch_cli(max_steps=10, interactive=False)

    def test_cli_2(self):
        arena = Arena.from_config("examples/chameleon.json")
        arena.launch_cli(max_steps=10, interactive=False)

    def test_cli_3(self):
        arena = Arena.from_config("examples/tic-tac-toe.json")
        arena.launch_cli(max_steps=10, interactive=False)

    def test_cli_4(self):
        arena = Arena.from_config("examples/rock-paper-scissors.json")
        arena.launch_cli(max_steps=10, interactive=False)

    def test_cli_5(self):
        arena = Arena.from_config("examples/nlp-classroom-3players.json")
        arena.launch_cli(max_steps=10, interactive=False)

    def test_cli_6(self):
        arena = Arena.from_config("examples/chess.json")
        arena.launch_cli(max_steps=10, interactive=False)

    def test_cli_7(self):
        # Suppress ResourceWarning
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

        arena = Arena.from_config("examples/chatgpt_claude_ai_collaboration.json")
        arena.launch_cli(max_steps=6, interactive=False)


if __name__ == "__main__":
    unittest.main()
