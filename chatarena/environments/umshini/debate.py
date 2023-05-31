# pyright: reportGeneralTypeIssues=false
from __future__ import annotations

from chatarena.environments.base import TimeStep
from chatarena.message import Message
from langchain.prompts import PromptTemplate

from chatarena.environments.umshini.base import UmshiniBaseEnv
from chatarena.environments.umshini.langchain_agents import judge_debate


class DebateEnv(UmshiniBaseEnv):
    """Debate environment."""

    moderator_prompt = PromptTemplate(
        template="""Welcome to the debate game! The topic for today's debate is:
"{moderator_prompt_input}"
Rules:
You will represent the position given to you.
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
        if self._current_turn <= self._round_length:
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
            return TimeStep(
                observation=self.get_observation(),
                reward=self.get_rewards(),
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
