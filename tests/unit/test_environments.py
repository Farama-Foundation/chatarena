import unittest
from unittest import TestCase

from chatarena.config import AgentConfig, BackendConfig, EnvironmentConfig
from chatarena.environments import (
    Chameleon,
    Environment,
    ModeratedConversation,
    PettingzooChess,
    PettingzooTicTacToe,
    load_environment,
    register_env,
)


class TestEnvironments(TestCase):
    def test_env_registration(self):
        @register_env
        class TestEnv(Environment):
            type_name = "test"

            @classmethod
            def from_config(cls, config: EnvironmentConfig):
                return cls(player_names=config.player_names)

        env_config = EnvironmentConfig(
            env_type="test", player_names=["player1", "player2"]
        )
        env = load_environment(env_config)
        assert isinstance(env, TestEnv)


class TestTicTacToeEnvironment(TestCase):
    def config(self):
        return EnvironmentConfig(
            env_type="pettingzoo:tictactoe", player_names=["player1", "player2"]
        )

    def test_registration_and_loading(self):
        env = load_environment(self.config())
        assert isinstance(env, PettingzooTicTacToe)

    def test_game(self):
        env = load_environment(self.config())
        env.reset()
        assert env.get_next_player() == "player1"

        moves = ["X: (3, 1)", "O: (2, 2)", "X: (1, 2)", "O: (1, 1)"]

        for i, move in enumerate(moves):
            assert env.check_action(move, env.get_next_player())
            env.step(env.get_next_player(), move)
            assert not env.is_terminal()


class TestChameleonEnvironment(TestCase):
    def test_registration_and_loading(self):
        config = EnvironmentConfig(
            env_type="chameleon", player_names=["player1", "player2"]
        )
        env = load_environment(config)
        assert isinstance(env, Chameleon)


class TestConversationEnvironment(TestCase):
    def test_registration_and_loading(self):
        config = EnvironmentConfig(
            env_type="conversation", player_names=["player1", "player2"]
        )
        env = load_environment(config)
        assert isinstance(env, Environment)


class TestModeratedConversationEnvironment(TestCase):
    def test_registration_and_loading(self):
        moderator = AgentConfig(
            role_desc="moderator",
            backend=BackendConfig(backend_type="human"),
            terminal_condition="all_done",
        )
        config = EnvironmentConfig(
            env_type="moderated_conversation",
            player_names=["player1", "player2"],
            moderator=moderator,
        )
        env = load_environment(config)
        assert isinstance(env, ModeratedConversation)


class TestPettingzooChessEnvironment(TestCase):
    def test_registration_and_loading(self):
        config = EnvironmentConfig(
            env_type="pettingzoo:chess", player_names=["player1", "player2"]
        )
        env = load_environment(config)
        assert isinstance(env, PettingzooChess)


if __name__ == "__main__":
    unittest.main()
