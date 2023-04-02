from typing import List
import re
from tenacity import RetryError
import logging

from .backends import IntelligenceBackend, load_backend
from .message import Message
from .config import AgentConfig, Configurable

# A special signal sent by the player to indicate that it is not possible to continue the conversation, and it requests to end the conversation.
# It contains a random UUID string to avoid being exploited by any of the players.
SIGNAL_END_OF_CONVERSATION = '<<<<<<END_OF_CONVERSATION>>>>>>f2d7c727-b99c-4a7e-9d05-b61ae88c69d0'


class Agent(Configurable):

    def __init__(self, config: AgentConfig, *args, **kwargs):
        super().__init__(config=config, *args, **kwargs)
        self._require_fields_in_config(['name'])
        self.name = self.config.name


class Player(Agent):
    """
    Player of the game. It can takes the observation from the environment and return an action
    """

    def __init__(self, config: AgentConfig, backend: IntelligenceBackend = None, *args, **kwargs):
        super().__init__(config=config, *args, **kwargs)
        self._require_fields_in_config(['role_desc', 'env_desc'])

        if backend is not None:
            self.backend = backend
        else:
            self._require_fields_in_config(['backend'])
            self.backend = load_backend(self.config.backend)

    def __call__(self, observation: List[Message]) -> str:
        """
        Call the agents to generate a response (equivalent to taking an action).
        """
        try:
            response = self.backend.query(
                agent_name=self.name,
                role_desc=self.config.role_desc,
                env_desc=self.config.env_desc,
                history_messages=observation,
                request_msg=None)
        except RetryError as e:
            logging.warning(f"Agent {self.name} failed to generate a response. "
                            f"Error: {e.last_attempt.exception()}. "
                            f"Sending signal to end the conversation.")
            response = SIGNAL_END_OF_CONVERSATION

        return response

    def to_config(self) -> AgentConfig:
        return AgentConfig(
            name=self.name,
            role_desc=self.config.role_desc,
            env_desc=self.config.env_desc,
            backend=self.backend.to_config()
        )

    def reset(self):
        self.backend.reset()


class Moderator(Agent):
    """
    A special type of agent that moderates the conversation (and is usually used as part of environment).
    """

    def __init__(self, config: AgentConfig, backend: IntelligenceBackend = None, *args, **kwargs):
        # Override the agent name to "Moderator" in the config
        config.name = "Moderator"
        super().__init__(config=config, *args, **kwargs)
        self._require_fields_in_config(['role_desc', 'env_desc', 'terminal_condition'])

        if backend is not None:
            self.backend = backend
        else:
            self._require_fields_in_config(['backend'])
            self.backend = load_backend(self.config.backend)

    def to_config(self) -> AgentConfig:
        return AgentConfig(
            name=self.name,
            role_desc=self.config.role_desc,
            env_desc=self.config.env_desc,
            terminal_condition=self.config.terminal_condition,
            backend=self.backend.to_config(),
        )

    def is_terminal(self, history: List[Message], *args, **kwargs) -> bool:
        """
        check whether the conversation is over
        """
        # If the last message is the signal, then the conversation is over
        if history[-1].content == SIGNAL_END_OF_CONVERSATION:
            return True

        try:
            response = self.backend.query(
                agent_name=self.name,
                role_desc=self.config.role_desc,
                env_desc=self.config.env_desc,
                history_messages=history,
                request_msg=Message(agent_name=self.name, content=self.config.terminal_condition, turn=-1),
                *args, **kwargs
            )
        except RetryError as e:
            logging.warning(f"Agent {self.name} failed to generate a response. "
                            f"Error: {e.last_attempt.exception()}.")
            return True

        if re.match(r"yes|y|yea|yeah|yep|yup|sure|ok|okay|alright", response, re.IGNORECASE):
            print(f"Decision: {response}. Conversation is ended by moderator.")
            return True
        else:
            return False

    def __call__(self, observation: List[Message]) -> str:
        """
        Call the moderator to generate an updated game state.
        """
        try:
            response = self.backend.query(
                agent_name=self.name,
                role_desc=self.config.role_desc,
                env_desc=self.config.env_desc,
                history_messages=observation,
                request_msg=None)
        except RetryError as e:
            logging.warning(f"Agent {self.name} failed to generate a response. "
                            f"Error: {e.last_attempt.exception()}. "
                            f"Sending signal to end the conversation.")
            response = SIGNAL_END_OF_CONVERSATION

        return response

    def reset(self):
        self.backend.reset()
