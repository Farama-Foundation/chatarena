from ..config import EnvironmentConfig
from .base import Environment, TimeStep
from .chameleon import Chameleon
from .conversation import Conversation, ModeratedConversation
from .pettingzoo_chess import PettingzooChess
from .pettingzoo_tictactoe import PettingzooTicTacToe

ALL_ENVIRONMENTS = [
    Conversation,
    ModeratedConversation,
    Chameleon,
    PettingzooChess,
    PettingzooTicTacToe,
]

ENV_REGISTRY = {env.type_name: env for env in ALL_ENVIRONMENTS}


# Load an environment from a config dictionary
def load_environment(config: EnvironmentConfig):
    try:
        env_cls = ENV_REGISTRY[config["env_type"]]
    except KeyError:
        raise ValueError(f"Unknown environment type: {config['env_type']}")

    env = env_cls.from_config(config)
    return env
