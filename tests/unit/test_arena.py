import os
import unittest
from unittest import TestCase

import pytest

import chatarena
from chatarena import EXAMPLES_DIR
from chatarena.arena import Arena


class TestArena(TestCase):
    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_1(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "nlp-classroom.json"))

        print("=== Step 1 ===")
        arena.step()
        arena.environment.print()

        print("=== Step 2 ===")
        arena.step()
        arena.environment.print()

        print("=== Step 3 ===")
        arena.step()
        arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_2(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "nlp-classroom.json"))

        arena.run(num_steps=10)
        arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_3(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "tic-tac-toe.json"))

        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_4(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "chameleon.json"))
        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_5(self):
        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "rock-paper-scissors.json")
        )
        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_6(self):
        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "nlp-classroom-3players.json")
        )
        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    @pytest.mark.xfail(raises=chatarena.arena.TooManyInvalidActions)
    def test_arena_7(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "pettingzoo_chess.json"))
        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.environ.get("ANTHROPIC_API_KEY"),
        "Anthropic API key must be set to run this test.",
    )
    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_8(self):
        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "chatgpt_claude_ai_collaboration.json")
        )
        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_9(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "interview.json"))
        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    def test_arena_10(self):
        arena = Arena.from_config(os.path.join(EXAMPLES_DIR, "prisoners_dilemma.json"))
        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OpenAI API key must be set to run this test.",
    )
    @pytest.mark.xfail(raises=(chatarena.arena.TooManyInvalidActions, ValueError))
    def test_arena_11(self):
        arena = Arena.from_config(
            os.path.join(EXAMPLES_DIR, "pettingzoo_tictactoe.json")
        )
        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
