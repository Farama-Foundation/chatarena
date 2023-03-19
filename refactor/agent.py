from typing import List, Dict, Tuple, Union
from refactor.intelligence import IntelligenceSource
from refactor.message import Message
import re

class Agent():
    def __init__(self, name,
                 intelligence_source: IntelligenceSource,
                 public_prompt: str,
                 private_prompt: str,):
        self.name = name
        self.intelligence_source = intelligence_source
        self.public_prompt = public_prompt
        self.private_prompt = private_prompt

    def __call__(self, history: List[Message]) -> str:
        """
        """
        background_prompt = self.public_prompt + '\n' + self.private_prompt
        # remind the model that the next message is from the specified agent
        prefix = f"[{self.name}]: "
        prefix_message = Message(self.name, prefix, turn=-1)

        response = self.intelligence_source.query(self.name,
                                                  background_info=background_prompt,
                                                  visible_history=history+[prefix_message],
                                                  request="")

        # remove the prefix the model added it incorrectly
        if response.startswith(prefix):
            response = response[len(prefix):]
        return f"[{self.name}]: {response}"


class Player(Agent):
    """
    Player of the game. It can takes the observation from the environment and return an action
    """

class Moderator(Agent):
    def __init__(self, intelligence_source: IntelligenceSource,
                 public_prompt: str,
                 private_prompt: str,
                 terminate_prompt: str,
                 ):
        super(Moderator, self).__init__(name="Moderator", intelligence_source=intelligence_source,
                                        public_prompt=public_prompt, private_prompt=private_prompt)
        self.terminate_prompt = terminate_prompt

    def is_terminal(self, history: List[Message]) -> bool:
        """
        check whether the conversation is over
        """
        prompt = self.public_prompt + '\n' + self.private_prompt
        response = self.intelligence_source.query(self.name,
                                                  background_info=prompt,
                                                  visible_history=history,
                                                  request=self.terminate_prompt,
                                                  temperature=0.0,
                                                  max_tokens=2)
        if re.match(r"yes|y|yea|yeah|yep|yup|sure|ok|okay|alright", response, re.IGNORECASE):
            print(f"Decision: {response}. Conversation is ended by moderator.")
            return True
        else:
            return False



