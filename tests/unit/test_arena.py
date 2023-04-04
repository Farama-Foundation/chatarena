import unittest
from unittest import TestCase

from chatarena.arena import Arena


class TestArena(TestCase):
    def test_arena_1(self):
        arena = Arena.from_config("examples/nlp-classroom.json")

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

    def test_arena_2(self):
        arena = Arena.from_config("examples/nlp-classroom.json")

        arena.run(num_steps=10)
        arena.environment.print()

        self.assertTrue(True)

    def test_arena_3(self):
        arena = Arena.from_config("examples/tic-tac-toe.json")

        for i in range(1, 10):
            print(f"=== Step {i} ===")
            arena.step()
            arena.environment.print()

        self.assertTrue(True)

    # def test_arena_4(self):
    #     with open("examples/nlp-classroom.json", "r") as fp:
    #         config = json.load(fp)
    #     arena = Arena.from_config(config)
    #     arena.launch_gradio()
    #
    #     self.assertTrue(True)
    #
    # def test_arena_5(self):
    #     with open("examples/tic-tac-toe.json", "r") as fp:
    #         config = json.load(fp)
    #     arena = Arena.from_config(config)
    #     arena.launch_gradio()
    #
    #     self.assertTrue(True)
    #
    # def test_arena_6(self):
    #     with open("examples/nlp-classroom-gpt4.json", "r") as fp:
    #         config = json.load(fp)
    #     arena = Arena.from_config(config)
    #     arena.launch_gradio()
    #
    #     self.assertTrue(True)
    #
    # def test_arena_7(self):
    #     with open("examples/tic-tac-toe-gpt4.json", "r") as fp:
    #         config = json.load(fp)
    #     arena = Arena.from_config(config)
    #     arena.launch_gradio()
    #
    #     self.assertTrue(True)
    #
    # def test_arena_8(self):
    #     with open("examples/nlp-classroom-3players.json", "r") as fp:
    #         config = json.load(fp)
    #     arena = Arena.from_config(config)
    #     arena.launch_gradio()
    #
    #     self.assertTrue(True)
    #
    #
    # def test_arena_9(self):
    #     with open("examples/rock-paper-scissors.json", "r") as fp:
    #         config = json.load(fp)
    #     arena = Arena.from_config(config)
    #     arena.launch_gradio()
    #
    #     self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
