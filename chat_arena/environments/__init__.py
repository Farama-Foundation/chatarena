from .environment import Environment, TimeStep, Conversation, ModeratedConversation
from .chameleon import Chameleon

ENV_REGISTRY = {
    "conversation": Conversation,
    "moderated_conversation": ModeratedConversation,
    "chameleon": Chameleon,
}

# Load an environment from a config dictionary
def load_environment(config):
    env_cls = ENV_REGISTRY[config["env_type"]]
    env = env_cls.from_config(config)
    return env
