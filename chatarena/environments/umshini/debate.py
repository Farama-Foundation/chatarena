# pyright: reportGeneralTypeIssues=false
# pyright: reportOptionalMemberAccess=false
from __future__ import annotations

import ast
import os
import random

from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from chatarena.environments.base import TimeStep
from chatarena.environments.umshini.base import UmshiniBaseEnv
from chatarena.message import Message, MessagePool


class DebateEnv(UmshiniBaseEnv):
    """Debate environment."""

    moderator_prompt = PromptTemplate(
        template="""Welcome to the debate game! The topic for today's debate is: "{moderator_prompt_input}"
The Opponent argues against the topic, while the Proponent argues for it.
The Moderator will report scores and decide a winner of the debate, based performance, persuasiveness, and response length.
Talk directly to the other player, the Moderator will not interject until the debate has finished.

The maximum number of characters for each response is {character_limit}.
Your first response should be an opening statement.""",
        input_variables=["moderator_prompt_input", "character_limit"],
    )
    type_name = "debate"

    def __init__(
        self,
        player_names: list[str],
        topic: str,
        round_length: int = 10,
        character_limit: int = 4000,
        disable_judging=False,
        **kwargs,
    ):
        super().__init__(
            player_names=player_names,
            moderator_prompt_template=self.moderator_prompt,
            moderator_prompt_input=topic,
            round_length=round_length,
            character_limit=character_limit,
            disable_judging=disable_judging,
            **kwargs,
        )
        self.character_limit = character_limit
        self.disable_judging = disable_judging
        self.topic = topic

    def get_rewards(self) -> dict[str, float]:
        """Uses langchain to analyze the conversation, pick a winner, and set the reward."""
        if self.disable_judging:
            # Local API testing
            scores = {
                "Opponent": random.randint(0, 10),
                "Proponent": random.randint(0, 10),
            }
            scores_text = f"SCORES: {scores}"
        else:
            scores, scores_text = judge_debate(self.player_names, self.message_pool)
        self._moderator_speak(scores_text)
        return scores

    def step(self, player_name: str, action: str) -> TimeStep:
        if self._current_turn < self._round_length - 1:
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
    topic: str,
    round_length: int | None = None,
    player_names: list[str] | None = None,
    character_limit: int | None = 4000,
    disable_judging: bool | None = False,
):
    if player_names is None:
        player_names = ["Opponent", "Proponent"]
    env = DebateEnv(
        player_names=player_names,
        topic=topic,
        round_length=round_length,
        character_limit=character_limit,
        disable_judging=disable_judging,
    )
    return env


judge_debate_system_message = SystemMessage(
    content="""You are an impartial debate judge. Your job is to rate the performance of each debater, on a scale of 0-10.
Your ratings should be based performance and persuasiveness, and not the morality of the position.

If a player's responses are too short (e.g., less than 5 sentences for a given response, rather than a paragraph), penalize their score heavily.
If a player argues for the wrong position (e.g., proponent arguing against the topic) or simply agrees with the other player, penalize their score heavily.
If a player hallucinates (e.g., pretending to be the moderator or the other player), penalize their score heavily.
If a player asks questions and is confused about what it is supposed to do, penalize their score heavily.

Use the following format:
<Player1> Arguments:<summarize>
<Player2> Arguments:<summarize>
<Player1> Rhetoric:<rhetorical strength>
<Player2> Rhetoric:<rhetorical strength>
<Player1> Response Length:<penalize short responses (ideal length is 5+ sentences), and too long responses which get cut off>
<Player2> Response Length:<penalize short responses (ideal length is 5+ sentences), and too long responses which get cut off>
EXPLANATION:<final explanation> <note any penalties which lowered scores>
SCORES: {"<Player1>": 0, "<Player2>": 10}"""
)


def judge_debate(
    player_names: list[str], message_state: MessagePool, model_name: str = "gpt-4"
) -> tuple[int, str]:
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
    if os.getenv("OPENAI_API_TYPE") == "azure":
        llm = AzureChatOpenAI(
            temperature=0,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_DEPLOYMENT") or "gpt-4",
            openai_api_version=os.getenv("OPENAI_API_VERSION") or "2023-05-15",
        )
        try:
            response = llm(langchain_messages)
        except Exception as e:
            print(e)
    else:
        llm = ChatOpenAI(
            temperature=0,
            model_name=model_name,
        )
        try:
            response = llm(langchain_messages)
        except Exception as e:
            print(e)

    start_index = response.content.find("SCORES:")
    if start_index != -1:
        # Extract the substring starting from SCORES: to the end
        scores_substring = response.content[start_index:]

        # Extract the dictionary part from the substring
        dictionary_string = scores_substring.split(":", 1)[1].strip()

        # Safely evaluate the dictionary string using ast.literal_eval
        scores_dict = ast.literal_eval(dictionary_string)
    else:
        print(f"ERROR: judge output does not contain 'SCORES:'. {response.content}")
        scores_dict = {player_names[0]: 0, player_names[1]: 0}
    return scores_dict, response.content
