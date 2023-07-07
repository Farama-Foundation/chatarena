import unittest
from unittest import TestCase

from chatarena.environments import (
    PettingzooTicTacToe
)


class TestEnvironments(TestCase):
    def test_chess_environment(self):
        player_names = ["player1", "player2"]
        env = PettingzooTicTacToe(player_names)

        env.reset()
        assert env.get_next_player() == "player1"
        env.print()

        moves = ["X: (3, 1)", "O: (2, 2)", "X: (1, 2)", "O: (1, 1)"]

        for i, move in enumerate(moves):
            assert env.check_action(move, env.get_next_player())
            timestep = env.step(env.get_next_player(), move)
            print(timestep.reward)
            print(timestep.terminal)
            env.print()


if __name__ == "__main__":
    unittest.main()
