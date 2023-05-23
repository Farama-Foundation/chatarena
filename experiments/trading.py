import numpy as np
from typing import List, Dict, Union
from chatarena.agent import Player
from chatarena.backends import OpenAIChat, Claude
from langchain.document_loaders import OnlinePDFLoader

from chatarena.environments.base import Environment, TimeStep
from chatarena.message import Message, MessagePool
from chatarena.agent import SIGNAL_END_OF_CONVERSATION
from chatarena.arena import Arena
from chatarena.utils import is_json_inside

DEFAULT_ORDER_BOOK = {
    "bids": [
        {"price": 3.98, "amount": 862},
        {"price": 3.99, "amount": 562},
        {"price": 4.00, "amount": 431},
    ],
    "asks": [
        {"price": 4.02, "amount": 12},
        {"price": 4.03, "amount": 285},
        {"price": 4.04, "amount": 210},
    ]
}


class Trading(Environment):
    type_name = "trading"

    def __init__(self, doc: str = ""):
        super().__init__(player_names=["researcher", "manager", "trader"])

        self.doc = doc
        # The "state" of the environment is maintained by the message pool
        self.message_pool = MessagePool()
        self.phase = "research"  # "research", "discussion", "trading"
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
                return "manager"
            elif self.current_player == "manager":
                return "researcher"
        elif self.phase == "trading":
            return "trader"
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
        if self.phase == "trading":
            self._terminal = True
        if is_json_inside(action) and self.phase == "discussion" and player_name == "manager":
            self.phase = "trading"
            self._moderator_speak(f"Here's the order book please put orders \n{DEFAULT_ORDER_BOOK}",
                                  visible_to="trader")

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

    manager_role_description = """
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

    trader_role_description = """
    You are a trader for crypto-fund.
    You are going to follow the "long" or "short" decision of your manager and put limit orders accorrding to the information in the order book.
    If the decision is "long", you should put a buy order (amount be position) otherwise you should put a sell order (amount be negative).
    The price should always be in favor of the fund this means if the decision is "long", the price should be lower than the lowest ask price in the order book,
    otherwise the price should be higher than highest ask price in the order book.
    You should a output a json with the following format:
    {
    "orders": [
        {"price": price of the order, "amount": amount to buy or sell. positive means buy, negative means sell},
    ]
    }   
    """

    loader = OnlinePDFLoader("https://impt.io/assets/documents/whitepaper/en.pdf")
    doc = loader.load()

    researcher = Player(name="researcher", role_desc=researcher_role_description,
                        global_prompt="", backend=Claude(max_tokens=1024, model="claude-v1.3-100k"))
    manager = Player(name="manager", role_desc=manager_role_description,
                     global_prompt="", backend=OpenAIChat(max_tokens=1024, model="gpt-4"))
    trader = Player(name="trader", role_desc=trader_role_description,
                    global_prompt="", backend=OpenAIChat(max_tokens=1024))
    env = Trading(doc=str(doc))
    arena = Arena([researcher, manager, trader], env)
    arena.launch_cli()
