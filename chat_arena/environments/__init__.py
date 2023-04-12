from .base import Environment, TimeStep
from .conversation import Conversation, ModeratedConversation
from .chameleon import Chameleon
from .pettingzoo_chess import ChessEnvironment

ENV_REGISTRY = {
    "conversation": Conversation,
    "moderated_conversation": ModeratedConversation,
    "chameleon": Chameleon,
    "chess": ChessEnvironment,
}


# Load an environment from a config dictionary
def load_environment(config):
    env_cls = ENV_REGISTRY[config["env_type"]]
    env = env_cls.from_config(config)
    return env
