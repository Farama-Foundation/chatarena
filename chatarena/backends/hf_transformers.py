import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from typing import List

from tenacity import retry, stop_after_attempt, wait_random_exponential
import torch

from ..message import SYSTEM_NAME
from ..message import Message
from .base import IntelligenceBackend, register_backend

END_OF_MESSAGE = "<EOS>"  # End of message token specified by us not OpenAI
BASE_PROMPT = f"The messages always end with the token {END_OF_MESSAGE}."
DEFAULT_MAX_TOKENS = 256


@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull."""
    with open(os.devnull, "w") as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield (err, out)


with suppress_stdout_stderr():
    # Try to import the transformers package
    try:
        import transformers
        from transformers import pipeline
        from transformers.pipelines.text_generation import (
            TextGenerationPipeline,
        )
    except ImportError:
        is_transformers_available = False
    else:
        is_transformers_available = True


@register_backend
class TransformersConversational(IntelligenceBackend):
    """Interface to the Transformers ConversationalPipeline."""

    stateful = False
    type_name = "transformers:conversational"

    def __init__(
        self,
        model: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        merge_other_agents_as_one_user: bool = True,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.model = model
        self.max_tokens = max_tokens

        assert is_transformers_available, "Transformers package is not installed"
        self.chatbot = pipeline(
            task="text-generation",
            model=self.model,
            device_map="auto",
            model_kwargs={"torch_dtype": torch.bfloat16},
        )
        self.terminators = [
            self.chatbot.tokenizer.eos_token_id,
            self.chatbot.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
        ]
        self.merge_other_agent_as_user = merge_other_agents_as_one_user

    def _get_response(self, conversation):

        conversation = self.chatbot(
            conversation,
            max_new_tokens=self.max_tokens,
            eos_token_id=self.terminators,
            pad_token_id=self.chatbot.tokenizer.eos_token_id,
        )
        response = conversation[0]["generated_text"][-1]["content"]
        return response

    def query(
        self,
        agent_name: str,
        role_desc: str,
        history_messages: List[Message],
        global_prompt: str = None,
        request_msg: Message = None,
        *args,
        **kwargs,
    ) -> str:
        if global_prompt:  # Prepend the global prompt if it exists
            system_prompt = f"You are a helpful assistant.\n{global_prompt.strip()}\n{BASE_PROMPT}\n\nYour name is {agent_name}.\n\nYour role:{role_desc}"
        else:
            system_prompt = f"You are a helpful assistant. Your name is {agent_name}.\n\nYour role:{role_desc}\n\n{BASE_PROMPT}"

        all_messages = [(SYSTEM_NAME, system_prompt)]
        for msg in history_messages:
            if msg.agent_name == SYSTEM_NAME:
                all_messages.append((SYSTEM_NAME, msg.content))
            else:  # non-system messages are suffixed with the end of message token
                all_messages.append((msg.agent_name, f"{msg.content}{END_OF_MESSAGE}"))

        if request_msg:
            all_messages.append((SYSTEM_NAME, request_msg.content))
        else:  # The default request message that reminds the agent its role and instruct it to speak
            all_messages.append(
                (SYSTEM_NAME, f"Now you speak, {agent_name}.{END_OF_MESSAGE}")
            )

        messages = []
        for i, msg in enumerate(all_messages):
            if i == 0:
                assert (
                    msg[0] == SYSTEM_NAME
                )  # The first message should be from the system
                messages.append({"role": "system", "content": msg[1]})
            else:
                if msg[0] == agent_name:
                    messages.append({"role": "assistant", "content": msg[1]})
                else:
                    if messages[-1]["role"] == "user":  # last message is from user
                        if self.merge_other_agent_as_user:
                            messages[-1][
                                "content"
                            ] = f"{messages[-1]['content']}\n\n[{msg[0]}]: {msg[1]}"
                        else:
                            messages.append(
                                {"role": "user", "content": f"[{msg[0]}]: {msg[1]}"}
                            )
                    elif (
                        messages[-1]["role"] == "assistant"
                    ):  # consecutive assistant messages
                        # Merge the assistant messages
                        messages[-1]["content"] = f"{messages[-1]['content']}\n{msg[1]}"
                    elif messages[-1]["role"] == "system":
                        messages.append(
                            {"role": "user", "content": f"[{msg[0]}]: {msg[1]}"}
                        )
                    else:
                        raise ValueError(f"Invalid role: {messages[-1]['role']}")

        # Get the response
        response = self._get_response(messages)
        return response
