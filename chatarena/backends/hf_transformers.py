from typing import List
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ..message import Message, SYSTEM_NAME as SYSTEM

# Try to import the transformers package
try:
    import transformers
    from transformers import pipeline
    from transformers.pipelines.conversational import Conversation, ConversationalPipeline
except ImportError:
    is_transformers_available = False
else:
    is_transformers_available = True


class TransformersConversational(IntelligenceBackend):
    """
    Interface to the Transformers ConversationalPipeline
    """
    stateful = False
    type_name = "transformers:conversational"

    def __init__(self, model: str, device: int = -1, **kwargs):
        super().__init__(model=model, device=device, **kwargs)
        self.model = model
        self.device = device

        assert is_transformers_available, "Transformers package is not installed"
        self.chatbot = pipeline(task="conversational", model=self.model, device=self.device)

    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
    def _get_response(self, conversation):
        conversation = self.chatbot(conversation)
        response = conversation.generated_responses[-1]
        return response

    @staticmethod
    def _msg_template(agent_name, content):
        return f"[{agent_name}]: {content}"

    def query(self, agent_name: str, role_desc: str, history_messages: List[Message], global_prompt: str = None,
              request_msg: Message = None, *args, **kwargs) -> str:
        user_inputs, generated_responses = [], []
        all_messages = [(SYSTEM, global_prompt), (SYSTEM, role_desc)] if global_prompt else [(SYSTEM, role_desc)]

        for msg in history_messages:
            all_messages.append((msg.agent_name, msg.content))
        if request_msg:
            all_messages.append((SYSTEM, request_msg.content))

        prev_is_user = False  # Whether the previous message is from the user
        for i, message in enumerate(all_messages):
            if i == 0:
                assert message[0] == SYSTEM  # The first message should be from the system

            if message[0] != agent_name:
                if not prev_is_user:
                    user_inputs.append(self._msg_template(message[0], message[1]))
                else:
                    user_inputs[-1] += "\n" + self._msg_template(message[0], message[1])
                prev_is_user = True
            else:
                if prev_is_user:
                    generated_responses.append(message[1])
                else:
                    generated_responses[-1] += "\n" + message[1]
                prev_is_user = False

        assert len(user_inputs) == len(generated_responses) + 1
        past_user_inputs = user_inputs[:-1]
        new_user_input = user_inputs[-1]

        # Recreate a conversation object from the history messages
        conversation = Conversation(text=new_user_input, past_user_inputs=past_user_inputs,
                                    generated_responses=generated_responses)

        # Get the response
        response = self._get_response(conversation)
        return response

# conversation = Conversation("Going to the movies tonight - any suggestions?")
#
# # Steps usually performed by the model when generating a response:
# # 1. Mark the user input as processed (moved to the history)
# conversation.mark_processed()
# # 2. Append a mode response
# conversation.append_response("The Big lebowski.")
#
# conversation.add_user_input("Is it good?")
