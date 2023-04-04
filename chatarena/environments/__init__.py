from .base import Environment, TimeStep
from .conversation import Conversation, ModeratedConversation
from .chameleon import Chameleon
from .pettingzoo_chess import ChessEnvironment

from ..config import EnvironmentConfig

ALL_ENVIRONMENTS = [
    Conversation,
    ModeratedConversation,
    Chameleon,
    ChessEnvironment,
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
