import numpy as np
from typing import List, Dict, Union
from chatarena.agent import Player
from chatarena.backends import OpenAIChat, Claude
from langchain.document_loaders import OnlinePDFLoader

from chatarena.environments.base import Environment, TimeStep
from chatarena.message import Message, MessagePool
from chatarena.agent import SIGNAL_END_OF_CONVERSATION
from chatarena.arena import Arena
import json

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

class Trading(Environment):
    type_name = "trading"

    def __init__(self, doc:str=""):
        super().__init__(player_names=["researcher", "trader"])

        self.doc = doc
        # The "state" of the environment is maintained by the message pool
        self.message_pool = MessagePool()
        self.phase = "research" # "research" or "discussion"
        self._terminal = False
        self.reset()

    def reset(self):
        self.current_player = "researcher"
        self.turn = 0
        self.message_pool.reset()

        self._moderator_speak(f"Here's the whitepaper of a new cryptocurrency. Please read it carefully:\n {self.doc}",
                              visible_to="researcher")
        observation = self.get_observation(self.get_next_player())
        self._terminal = False
        self.phase = "discussion"
        return TimeStep(observation=observation,
                        reward=self.get_zero_rewards(),
                        terminal=self._terminal)


    def get_next_player(self) -> str:
        if self.phase == "research":
            return "researcher"
        elif self.phase == "discussion":
            if self.current_player == "researcher":
                return "trader"
            elif self.current_player == "trader":
                return "researcher"
        else:
            raise ValueError(f"Unknown phase {self.phase}")

    def get_observation(self, player_name=None) -> List[Message]:
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=self.turn + 1)

    def _moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all"):
        """
        moderator say something
        """
        message = Message(agent_name="Moderator", content=text, turn=self.turn, visible_to=visible_to)
        self.message_pool.append_message(message)

    def is_terminal(self) -> bool:
        return self._terminal

    def step(self, player_name: str, action: str) -> TimeStep:
        assert player_name == self.get_next_player(), f"Wrong player! It is {self.get_next_player()} turn."
        message = Message(agent_name=player_name, content=action, turn=self.turn)
        self.message_pool.append_message(message)
        if is_json(action) and player_name=="trader":
            self._terminal = True

        self.turn += 1
        self.current_player = self.get_next_player()
        return TimeStep(observation=self.get_observation(self.get_next_player()),
                        reward=self.get_zero_rewards(),
                        terminal=self._terminal)

if __name__ == "__main__":
    researcher_role_description = """
    You are a researcher for crypto-trading.
    You are going to analyse the whitepaper of a new cryptocurrency.
    After finishing the reading, you'll dicuss with a trader, helping him to make a decision.
    """

    trader_role_description = """
    You are managing a crypto fund.
    You are going to discuss with a researcher about a new cryptocurrency called impt.io whose market cap is 5.2 million dollars.
    Try to figure out all the information you need to make a decision.
    Try to ask at least 3 round of questions before you make the decision.
    When you are ready to make the decision, output a json with the following format:
    { 
    "reasong": the reason for your decision,
    "decision": "long" or "short"",
    }
    """

    loader = OnlinePDFLoader("https://impt.io/assets/documents/whitepaper/en.pdf")
    doc = loader.load()

    researcher = Player(name="researcher", role_desc=researcher_role_description,
                         global_prompt="", backend=Claude(max_tokens=1024, model="claude-v1.3-100k"))
    trader = Player(name="trader", role_desc=trader_role_description,
                            global_prompt="", backend=OpenAIChat())
    env = Trading(doc=str(doc))
    arena = Arena([researcher, trader], env)
    arena.launch_cli()
