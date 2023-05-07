from typing import List
import os
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ..message import Message

# Try to import the cohere package and check whether the API key is set
try:
    import cohere
except ImportError:
    is_cohere_available = False
else:
    if os.environ.get('COHEREAI_API_KEY') is None:
        is_cohere_available = False
    else:
        is_cohere_available = True

# Default config follows the [Cohere documentation](https://cohere-sdk.readthedocs.io/en/latest/cohere.html#cohere.client.Client.chat)
DEFAULT_TEMPERATURE = 0.8
DEFAULT_MAX_TOKENS = 200
DEFAULT_MODEL = "command-xlarge"


class CohereAIChat(IntelligenceBackend):
    """
    Interface to the Cohere API
    """
    stateful = True
    type_name = "cohere-chat"

    def __init__(self, temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS,
                 model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(temperature=temperature, max_tokens=max_tokens, model=model, **kwargs)

        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model

        assert is_cohere_available, "Cohere package is not installed or the API key is not set"
        self.client = cohere.Client(os.environ.get('COHEREAI_API_KEY'))

        # Stateful variables
        self.session_id = None  # The session id for the last conversation
        self.last_msg_hash = None  # The hash of the last message of the last conversation

    def reset(self):
        self.session_id = None
        self.last_msg_hash = None

    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
    def _get_response(self, new_message: str, persona_prompt: str):
        response = self.client.chat(
            new_message,
            persona_prompt=persona_prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            session_id=self.session_id
        )

        self.session_id = response.session_id  # Update the session id
        return response.reply

    def query(self, agent_name: str, role_desc: str, history_messages: List[Message], global_prompt: str = None,
              request_msg: Message = None, *args, **kwargs) -> str:
        """
        format the input and call the Cohere API
        args:
            agent_name: the name of the agent
            role_desc: the description of the role of the agent
            env_desc: the description of the environment
            history_messages: the history of the conversation, or the observation for the agent
            request_msg: the request for the CohereAI
        """
        # Find the index of the last message of the last conversation
        new_message_start_idx = 0
        if self.last_msg_hash is not None:
            for i, message in enumerate(history_messages):
                if message.msg_hash == self.last_msg_hash:
                    new_message_start_idx = i + 1
                    break

        new_messages = history_messages[new_message_start_idx:]
        assert len(new_messages) > 0, "No new messages found (this should not happen)"

        new_conversations = []
        for message in new_messages:
            if message.agent_name != agent_name:
                # Since there are more than one player, we need to distinguish between the players
                new_conversations.append(f"[{message.agent_name}]: {message.content}")

        if request_msg:
            new_conversations.append(f"[{request_msg.agent_name}]: {request_msg.content}")

        # Concatenate all new messages into one message because the Cohere API only accepts one message
        new_message = "\n".join(new_conversations)
        persona_prompt = f"Environment:\n{global_prompt}\n\nYour role:\n{role_desc}"

        response = self._get_response(new_message, persona_prompt)

        # Only update the last message hash if the API call is successful
        self.last_msg_hash = new_messages[-1].msg_hash

        return response
