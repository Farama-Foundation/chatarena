# pyright: reportGeneralTypeIssues=false

from typing import Dict, List, Union

from chatarena.environments.base import Environment, TimeStep
from chatarena.message import Message, MessagePool
from langchain.prompts import PromptTemplate
from pettingzoo.utils import agent_selector


class UmshiniBaseEnv(Environment):
    type_name = "base"
    _colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "end": "\033[0m",
    }

    def __init__(
        self,
        player_names: List[str],
        moderator_prompt_template: PromptTemplate,
        moderator_prompt_input: str,
        round_length: int = 10,
        **kwargs
    ):
        """Base environment for all Umshini game environments.

        Must call super().reset() if being overwritten.
        """
        super().__init__(player_names=player_names, **kwargs)
        self._initialized = False
        self._moderator_prompt_template = moderator_prompt_template
        self._moderator_prompt_input = moderator_prompt_input
        self._round_length = round_length
        self.agent_selector = agent_selector(self.player_names)
        self.reset()

    def reset(self):
        """Reset the environment. Sets basic LangEnv variables.

        Must call super().reset() if being overwritten, call moderator_speak, and return the timestep.
        """
        self.message_pool = MessagePool()
        self._current_turn = 0
        self._next_player_idx = 0
        self._current_phase_length = 0
        self._current_phase = "start"
        self._winner = None
        self._initialized = True
        self.agent_selector = agent_selector(self.player_names)
        self._moderator_speak(
            self._moderator_prompt_template.format(
                moderator_prompt_input=self._moderator_prompt_input
            )
        )
        return TimeStep(
            observation=self.get_observation(),
            reward=self.get_zero_rewards(),
            terminal=False,
        )

    def _moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all"):
        """Moderator say something to both players."""
        message = Message(
            agent_name="Moderator",
            content=text,
            turn=self._current_turn,
            visible_to=visible_to,
        )
        self.message_pool.append_message(message)

    def print(self):
        self.message_pool.print()

    def pretty_print(self):
        """Prints out formatted and colored full message pool."""
        agent_name_to_color = {
            agent_name: color
            for agent_name, color in zip(self.player_names, self._colors.values())
        }

        for m in self.message_pool.get_all_messages():
            sb = (
                agent_name_to_color[m.agent_name]
                + m.agent_name
                + self._colors["end"]
                + "\t"
                + self._colors["blue"]
                + str(m.turn)
                + self._colors["end"]
                + "\n"
                + m.content
                + "\n"
            )
            print(sb)

    def pretty_print_last(self):
        """Prints out formatted and colored last message from message pool."""
        agent_name_to_color = {
            agent_name: color
            for agent_name, color in zip(self.player_names, self._colors.values())
        }
        l_m = self.message_pool.last_message
        assert l_m is not None
        sb = (
            agent_name_to_color[l_m.agent_name]
            + l_m.agent_name
            + self._colors["end"]
            + "\t"
            + self._colors["blue"]
            + str(l_m.turn)
            + self._colors["end"]
            + "\n"
            + l_m.content
            + "\n"
        )
        print(sb)

    def get_observation(self, player_name: str = None) -> List[Message]:  # type: ignore
        """Get observation for the player."""
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            # Initial moderator message counts as a turn for ChatArena message pool, so our turn 0 is its turn 1
            return self.message_pool.get_visible_messages(
                player_name, turn=self._current_turn + 1
            )

    def is_terminal(self) -> bool:
        """Check if the conversation is over."""
        return self._current_phase == "end"

    def get_next_player(self) -> str:
        """Get the name of the next player."""
        return self.agent_selector.next()

    def get_rewards(self) -> Dict[str, float]:
        """Use langchain to analyze the conversation, pick a winner, and set the reward."""
        raise NotImplementedError

    def step(self, player_name: str, action: str) -> TimeStep:
        raise NotImplementedError
