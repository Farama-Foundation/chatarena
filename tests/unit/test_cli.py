import unittest
from unittest import TestCase

from chatarena.arena import Arena

import warnings

class TestCLI(TestCase):
    def test_cli_1(self):
        arena = Arena.from_config("examples/nlp-classroom.json")
        arena.launch_cli(max_steps=10, interactive=False)

    def test_cli_2(self):
        # arena = Arena.from_config("examples/chameleon.json")
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
        arena = Arena.from_config("examples/pettingzoo_chess.json")
        arena.launch_cli(max_steps=10, interactive=False)

    def test_cli_7(self):
        # Suppress ResourceWarning
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

        arena = Arena.from_config("examples/chatgpt_claude_ai_collaboration.json")
        arena.launch_cli(max_steps=6, interactive=False)

    def test_cli_8(self):
        arena = Arena.from_config("examples/interview.json")
        arena.launch_cli(max_steps=16, interactive=False)

    def test_cli_9(self):
        arena = Arena.from_config("examples/chatgpt_claude_ai_collaboration.json")
        arena.launch_cli(max_steps=6, interactive=False)

    def test_cli_10(self):
        arena = Arena.from_config("examples/prisoners_dilemma.json")
        arena.launch_cli(max_steps=3, interactive=False)

    def test_cli_11(self):
        arena = Arena.from_config("examples/pettingzoo_tictactoe.json")
        arena.launch_cli(max_steps=9, interactive=False)


if __name__ == "__main__":
    unittest.main()
