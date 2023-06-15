# pyright: reportGeneralTypeIssues=false
# pyright: reportOptionalMemberAccess=false
from __future__ import annotations

import re
from typing import List, Tuple
import os

from chatarena.environments.base import TimeStep
from chatarena.message import Message, MessagePool
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from chatarena.environments.umshini.base import UmshiniBaseEnv


class DebateEnv(UmshiniBaseEnv):
    """Debate environment."""

    moderator_prompt = PromptTemplate(
        template="""Welcome to the debate game! The topic for today's debate is:
"{moderator_prompt_input}"
Rules:
The Opponent argues against the topic, while the Proponent argues for it.
Your first response should be an opening statement, followed by back and forth cross-examination.
You are free to talk directly to your opponent during cross-examination.
The cross examination phase should be short, and should be used to attack your opponents arguments, or defend your own.
The winner of the debate will be decided by the judge, based the performance and persuasiveness of each debater, and not the morality of the position.
Do not respond as any other character, only as yourself.
The judge will not interrupt.""",
        input_variables=["moderator_prompt_input"],
    )
    type_name = "debate"

    def __init__(
        self, player_names: list[str], topic: str, round_length: int = 10, **kwargs
    ):
        super().__init__(
            player_names=player_names,
            moderator_prompt_template=self.moderator_prompt,
            moderator_prompt_input=topic,
            round_length=round_length,
            **kwargs,
        )
        self.topic = topic

    def get_rewards(self) -> dict[str, float]:
        """Uses langchain to analyze the conversation, pick a winner, and set the reward."""
        winner, winner_text = judge_debate(self.player_names, self.message_pool)
        self._moderator_speak(winner_text)
        if winner == 0:
            return {self.player_names[0]: 1, self.player_names[1]: 0}
        elif winner == 1:
            return {self.player_names[0]: 0, self.player_names[1]: 1}
        else:
            return {self.player_names[0]: 0, self.player_names[1]: 0}

    def step(self, player_name: str, action: str) -> TimeStep:
        if self._current_turn < self._round_length -1:
            self._current_turn += 1
            self.message_pool.append_message(
                Message(agent_name=player_name, content=action, turn=self._current_turn)
            )
            return TimeStep(
                observation=self.get_observation(),
                reward=self.get_zero_rewards(),
                terminal=False,
            )
        else:
            self._current_phase = "end"
            self.message_pool.append_message(
                Message(agent_name=player_name, content=action, turn=self._current_turn)
            )
            # get the rewards before getting the observation, so that the moderator's final message is displayed (winner)
            rews = self.get_rewards()
            return TimeStep(
                observation=self.get_observation(),
                reward=rews,
                terminal=True,
            )


def create_debate_env(
    topic: str, round_length: int | None = None, player_names: list[str] | None = None
):
    if player_names is None:
        player_names = ["Opponent", "Proponent"]
    env = DebateEnv(
        player_names=player_names,
        topic=topic,
        round_length=round_length,
    )
    return env

judge_debate_system_message = SystemMessage(
        content="""You are an impartial debate judge. There is always a winner in every debate, there are no ties.
Do not say: it is a close call. Do not say: it is a tie.
Your purpose is to describe who had the better rhetorical arguments and pick a winner in the format:
<Player1>_Arguments:<summarize>
<Player2>_Arguments:<summarize>
<Player1>_Rhetoric:<rhetorical strength>
<Player2>_Rhetoric:<rhetorical strength>
EXPLANATION:<final explanation>
WINNER:<name>"""
)


def judge_debate(
    player_names: List[str], message_state: MessagePool, model_name: str = "gpt-3.5-turbo"
) -> Tuple[int, str]:
    llm = None
    if os.getenv("OPENAI_API_TYPE") == "azure":
        llm = AzureChatOpenAI(temperature=0, deployment_name=os.getenv("CHATARENA_AZURE_DEPLOYMENT_CHAT"))
    else:
        llm = ChatOpenAI(temperature=0, model_name=model_name, client="")
    langchain_messages = []
    langchain_messages.append(judge_debate_system_message)

    for i, message in enumerate(message_state.get_all_messages()):
        if i == 0:
            langchain_messages.append(AIMessage(content=f"{message.content}"))
        else:
            langchain_messages.append(
                HumanMessage(
                    content=f"{message.agent_name} -> Turn:{message.turn}:\n{message.content}"
                )
            )
    response = llm(langchain_messages)
    match = re.search(r"WINNER:\s*(\w+)\s*$", response.content)
    if match is None:
        return -1, response.content
    winner = match.group(1)
    if winner in player_names:
        return player_names.index(winner), response.content
    return -1, response.content
