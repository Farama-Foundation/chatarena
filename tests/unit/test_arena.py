import unittest
from unittest import TestCase
import json

from chat_arena.arena import Arena


class TestArena(TestCase):
    def test_arena_1(self):
        with open("examples/nlp-classroom.json", "r") as fp:
            config = json.load(fp)
        arena = Arena.from_config(config)

        print("=== Step 1 ===")
        arena.step()
        arena.environment.print()

        print("=== Step 2 ===")
        arena.step()
        arena.environment.print()

        print("=== Step 3 ===")
        arena.step()
        arena.environment.print()

        self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main()
