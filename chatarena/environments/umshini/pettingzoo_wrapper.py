"""Wrapper to convert a ChatArena environment into a PettingZoo compatible environment."""
# pyright: reportGeneralTypeIssues=false, reportUnboundVariable=false, reportOptionalMemberAccess=false
from __future__ import annotations

import functools
import string

from colorama import Fore
from gymnasium import spaces
from gymnasium.utils import EzPickle
from pettingzoo import AECEnv
from pettingzoo.utils.env import AgentID, ObsType

from chatarena.environments import Environment
from chatarena.environments.base import TimeStep
from chatarena.environments.umshini.content_moderation import (
    create_content_moderation_env,
)
from chatarena.environments.umshini.debate import create_debate_env
from chatarena.environments.umshini.deception import create_deception_env
from chatarena.environments.umshini.symmetric_content_moderation import (
    create_symmetric_content_moderation_env,
)
from chatarena.environments.umshini.symmetric_deception import (
    create_symmetric_deception_env,
)
from chatarena.message import Message

CHAR_SET = string.printable


class PettingZooCompatibilityV0(AECEnv, EzPickle):
    """This compatibility wrapper converts a ChatArena environment into a PettingZoo environment.

    Unique arguments for umshini environments: env_name topic, moderation_policy, restricted_action, player_names, round_length
    """

    metadata = {
        "render_modes": ["human"],
        "name": "PettingZooCompatibilityV0",
        "is_parallelizable": False,
        "render_fps": 2,
    }

    def __init__(
        self,
        env: Environment | None = None,
        env_name: str | None = None,
        topic: str | None = None,
        moderation_policy: str | None = None,
        restricted_action: str | None = None,
        player_names: list | None = None,
        round_length: int | None = 8,
        string_observation: bool | None = True,
        character_limit: int | None = 4000,
        render_mode: str | None = None,
        save_json: bool | None = False,
        disable_judging: bool | None = False,
    ):
        """Wrapper to convert a ChatArena environment into a PettingZoo environment.

        Args:
            env (chatarena.environments.Environment): chatarena arena to wrap
            env_name (str): name of chatarena environment to load (options: "debate", "content_moderation", "deception")
            topic (Optional[str]): topic for debate environment
            moderation_policy (Optional[str]): moderation policy for content moderation environment
            restricted_action (Optional[str]): restricted action for deception environment
            player_names (Optional[str]): name of players in the environment
            round_length (Optional[int]): number of rounds before swapping roles for symmetric envs, total rounds for asymmetric envs
            string_observation (Optional[bool]): send observations as a single string (rather than a dict)
            character_limit (Optional[int]): maximum number of characters for observations and actions
            render_mode (Optional[str]): rendering mode
            save_json (Optional[bool]): flag to save a json file to the disk containing a chat log
        """
        EzPickle.__init__(
            self,
            env,
            env_name,
            topic,
            moderation_policy,
            restricted_action,
            player_names,
            round_length,
            string_observation,
            character_limit,
            render_mode,
            save_json,
        )
        super().__init__()

        if env is None and env_name is None:
            raise TypeError(
                "ChatArena Environment or environment name must be specified"
            )
        elif env is not None:
            self._env = env
            if self._env.type_name == "debate":
                self.env_name = "debate"
                self.topic = topic
                self.max_turns = round_length
            elif self._env.type_name == "content_moderation":
                self.env_name = "content_moderation"
                self.moderation_policy = env.moderation_policy
                self.max_turns = round_length
            elif self._env.type_name == "symmetric_content_moderation":
                self.env_name = "symmetric_content_moderation"
                self.moderation_policy = env.moderation_policy
                self.max_turns = round_length * 2
            elif self._env.type_name == "deception":
                self.env_name = "deception"
                self.restricted_action = env.restricted_action
                self.max_turns = round_length
            elif self._env.type_name == "symmetric_deception":
                self.env_name = "symmetric_deception"
                self.restricted_action = env.restricted_action
                self.max_turns = round_length * 2
        elif env_name is not None:
            self.env_name = env_name
            if env_name == "debate":
                assert topic is not None, "topic must be specified for debate env"
                self._env = create_debate_env(
                    topic=topic,
                    player_names=player_names,
                    round_length=round_length,
                    character_limit=character_limit,
                    disable_judging=disable_judging,
                )
                self.topic = topic
                self.max_turns = round_length
            elif env_name == "content_moderation":
                assert (
                    moderation_policy is not None
                ), "moderation policy must be specified for content moderation env"
                self._env = create_content_moderation_env(
                    moderation_policy=moderation_policy,
                    player_names=player_names,
                    round_length=round_length,
                    character_limit=character_limit,
                    disable_judging=disable_judging,
                )
                self.moderation_policy = moderation_policy
                self.max_turns = round_length
            elif env_name == "symmetric_content_moderation":
                assert (
                    moderation_policy is not None
                ), "moderation policy must be specified for content moderation env"
                self._env = create_symmetric_content_moderation_env(
                    moderation_policy=moderation_policy,
                    player_names=player_names,
                    round_length=round_length,
                    character_limit=character_limit,
                    disable_judging=disable_judging,
                )
                self.moderation_policy = moderation_policy
                self.max_turns = round_length * 2
            elif env_name == "deception":
                assert (
                    restricted_action is not None
                ), "restricted action must be specified for deception env"
                self._env = create_deception_env(
                    restricted_action=restricted_action,
                    player_names=player_names,
                    round_length=round_length,
                    character_limit=character_limit,
                    disable_judging=disable_judging,
                )
                self.restricted_action = restricted_action
                self.max_turns = round_length
            elif env_name == "symmetric_deception":
                assert (
                    restricted_action is not None
                ), "restricted action must be specified for deception env"
                self._env = create_symmetric_deception_env(
                    restricted_action=restricted_action,
                    player_names=player_names,
                    round_length=round_length,
                    character_limit=character_limit,
                    disable_judging=disable_judging,
                )
                self.restricted_action = restricted_action
                self.max_turns = round_length * 2
            else:
                raise TypeError(
                    f"Environment not found: {env_name}. Options: debate, content_moderation, deception, symmetric_content_moderation, symmetric_deception"
                )
        else:
            raise TypeError(
                "Only one environment argument may be specified: either env or env_name."
            )

        # Reset the underlying ChatArena environment
        self._env.reset()

        # Arguments
        self.string_observation = string_observation
        self.character_limit = character_limit
        self.render_mode = render_mode
        self.save_json = save_json

        # PettingZoo arguments
        self.possible_agents = list(self._env.player_names)
        self.all_agents = [
            "Moderator",
            self.possible_agents[0],
            self.possible_agents[1],
        ]

        self.observations = {agent: {} for agent in self.possible_agents}
        self.rewards = {agent: {} for agent in self.possible_agents}
        self.terminations = {agent: {} for agent in self.possible_agents}
        self.truncations = {agent: {} for agent in self.possible_agents}
        self.infos = {
            agent: {"turn": 0, "obs_dict": {}, "new_messages": [], "all_messages": []}
            for agent in self.possible_agents
        }

        # Custom attributes for housekeeping
        self.total_rewards = {agent: 0.0 for agent in self.possible_agents}
        self.current_turn = 0

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent: AgentID):
        """Observation_space.

        We get the observation space from the underlying environment.
        Supports both string and dict observations spaces.

        Args:
            agent (AgentID): agent
        """
        if self.string_observation:
            observation_space = spaces.Text(
                max_length=self.character_limit, min_length=0, charset=CHAR_SET
            )
        else:
            observation_space = spaces.Dict(
                {
                    agent: spaces.Text(
                        max_length=self.character_limit, min_length=0, charset=CHAR_SET
                    )
                    for agent in self.all_agents
                }
            )
        return observation_space

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent: AgentID):
        """Action_space.

        Get the action space from the underlying environment.
        Action space currently only supports messages to all players, but could be extended to support private messages.

        Args:
            agent (AgentID): agent

        Returns:
            space
        """
        return spaces.Text(
            max_length=self.character_limit, min_length=0, charset=CHAR_SET
        )

    def render(self):
        """Render.

        Print the current game state.
        """
        if not hasattr(self, "initial_timestep"):
            raise UserWarning(
                "You must reset the environment using reset() before calling render()."
            )

        if self.render_mode == "human":
            new_messages = self.infos[self.agent_selection].get("new_messages")
            if new_messages is None:
                raise Exception("New messages not found")
            else:
                for message in new_messages:
                    # Don't repeat things from previous turns
                    if not self.current_turn > message.turn:
                        if message.agent_name == "Moderator":
                            color = Fore.BLACK
                            role = ""
                        else:
                            if self.infos[message.agent_name]["role"] == "attacker":
                                color = Fore.RED
                                role = "(attacker)"
                            elif self.infos[message.agent_name]["role"] == "defender":
                                color = Fore.BLUE
                                role = "(defender)"
                            elif self.infos[message.agent_name]["role"] == "proponent":
                                color = Fore.BLUE
                                role = "(proponent)"
                            elif self.infos[message.agent_name]["role"] == "opponent":
                                color = Fore.RED
                                role = "(opponent)"
                            else:
                                raise Exception("Glitch in internal logic")
                        print(
                            color
                            + f"[{message.agent_name} {role}-> {message.visible_to}]: {message.content}\n "
                            + Fore.BLACK
                        )

    def observe(self, agent: AgentID) -> ObsType:
        """Observe.

        Args:
            agent (AgentID): agent (e.g., "Player 1")

        Returns:
            observation
        """
        # When PettingZoo agents die, they are removed from the info dict (as well as obs, cumulative rewards, termination, truncation)
        if agent not in self.agents:
            return None
        # Observations and infos are calculated in step(), but need to be calculated before the first step() call
        elif not isinstance(agent, str):
            raise TypeError("AgentID must be a string")
        else:
            # get only the messages that this agent can see
            messages = self._env.get_observation(agent)

            # calculate current turn
            if len(messages) > 0:
                self.current_turn = messages[-1].turn
            else:
                self.current_turn = 0

            # filter to only new messages for this agent (observation is limited to only the current message)
            new_messages = [m for m in messages if m.turn == self.current_turn]

            # string observation (optional flag)
            if self.string_observation:
                observation = ""
                for m in new_messages:
                    observation += f"{m.agent_name}: {m.content}"
            # dict observation
            else:
                observation = {m.agent_name: m.content for m in new_messages}

            # We return info in the form of ChatArena messages objects, as well as strings, and a dictionary, to allow for maximum flexibility.
            # Dict prevents you from having to parse the message to determine the agent, which may lead to errors if LLMs repeat the agent name (common from my testing)
            # I'd argue we might want to use it as the default return type for that reason alone
            self.infos[agent]["turn"] = self.current_turn
            self.infos[agent]["new_messages"] = new_messages
            self.infos[agent]["all_messages"] = messages
            self.infos[agent]["obs_dict"] = {
                m.agent_name: m.content for m in new_messages
            }
            self.infos[agent]["player_name"] = self.agent_selection

            # Role in symmetric environments (not applicable if env has terminated)
            if self.env_name == "debate":
                if not any(self.terminations.values()):
                    self.infos[self.possible_agents[0]]["role"] = self._env.roles[
                        self.possible_agents[0]
                    ]
                    self.infos[self.possible_agents[1]]["role"] = self._env.roles[
                        self.possible_agents[1]
                    ]
            elif self.env_name in [
                "content_moderation",
                "deception",
                "symmetric_content_moderation",
                "symmetric_deception",
            ]:
                if hasattr(self._env, "_current_phase") and not any(
                    self.terminations.values()
                ):
                    if (
                        self._env._current_phase == "player_2_attack"
                        or "Roles are being swapped" in new_messages[-1].content
                    ):
                        self.infos[self.possible_agents[0]]["role"] = "defender"
                        self.infos[self.possible_agents[1]]["role"] = "attacker"
                    else:
                        self.infos[self.possible_agents[0]]["role"] = "attacker"
                        self.infos[self.possible_agents[1]]["role"] = "defender"

            # info: generate string of full chat log
            if self.string_observation:
                all_messages_string = ""
                for m in messages:
                    all_messages_string += f"[{m.agent_name}->all]: {m.content}\n"
                self.infos[agent]["all_messages_string"] = all_messages_string

            # info: environment specific information
            if hasattr(self, "restricted_action"):
                self.infos[agent]["restricted_action"] = self.restricted_action
            if hasattr(self, "moderation_policy"):
                self.infos[agent]["moderation_policy"] = self.moderation_policy
            if hasattr(self, "topic"):
                self.infos[agent]["topic"] = self.topic

            return observation

    def close(self):
        """Close."""
        msg_lst: list[Message] = self._env.message_pool.get_all_messages()
        formatted_state = [
            {"name": m.agent_name, "turn": m.turn, "text": m.content} for m in msg_lst
        ]
        if self.save_json:
            import json
            import os
            from pathlib import Path

            Path("env_logs").mkdir(exist_ok=True)
            os.chdir("env_logs")
            files = os.listdir()
            files = [
                f
                for f in files
                if f.startswith(self.metadata["name"]) and f.endswith(".json")
            ]
            json.dump(
                formatted_state,
                open(self.metadata["name"] + str(len(files)) + ".json", "w"),
            )
            print(
                f"Chatlog has been saved to disk: {self.metadata['name'] + str(len(files)) + '.json'}"
            )
        else:
            return formatted_state

    def _unravel_timestep(self, timestep: TimeStep):
        # get observation
        messages = timestep.observation

        # calculate current turn
        if len(messages) > 0:
            self.current_turn = messages[-1].turn
        else:
            self.current_turn = 0

        # filter to only new messages (observation is limited to only the current message)
        new_messages = [m for m in messages if m.turn == self.current_turn]

        # string observation (optional flag)
        if self.string_observation:
            observation = ""
            for m in new_messages:
                observation += f"{m.agent_name}: {m.content}"

        # dict observation
        else:
            observation = {m.agent_name: m.content for m in new_messages}

        # get rewards
        rewards = timestep.reward

        # get termination
        termination = timestep.terminal

        # get truncation
        truncation = (
            self.current_turn >= self.max_turns
        )  # pyright: ignore[reportGeneralTypeIssues]

        info = {}

        info["turn"] = self.current_turn
        info["new_messages"] = new_messages
        info["all_messages"] = messages
        info["obs_dict"] = {m.agent_name: m.content for m in new_messages}
        info["player_name"] = self.agent_selection

        # info: generate string of full chat log
        if self.string_observation:
            all_messages_string = ""
            for m in messages:
                all_messages_string += f"[{m.agent_name}->all]: {m.content}\n"
            info["all_messages_string"] = all_messages_string

        # Role in debate environment
        if self.env_name == "debate":
            self.infos[self.possible_agents[0]]["role"] = self._env.roles[
                self.possible_agents[0]
            ]
            self.infos[self.possible_agents[1]]["role"] = self._env.roles[
                self.possible_agents[1]
            ]
        # Role in symmetric environments
        elif hasattr(self._env, "_current_phase"):
            if (
                self._env._current_phase == "player_2_attack"
                or self._env._current_phase == "end"
            ):
                self.infos[self.possible_agents[0]]["role"] = "defender"
                self.infos[self.possible_agents[1]]["role"] = "attacker"
            else:
                self.infos[self.possible_agents[0]]["role"] = "attacker"
                self.infos[self.possible_agents[1]]["role"] = "defender"

        info["role"] = self.infos[self.agent_selection]["role"]

        # info: environment specific information
        if hasattr(self, "restricted_action"):
            info["restricted_action"] = self.restricted_action
        if hasattr(self, "moderation_policy"):
            info["moderation_policy"] = self.moderation_policy
        if hasattr(self, "topic"):
            info["topic"] = self.topic

        return observation, rewards, termination, truncation, info

    def reset(
        self,
        return_info: bool | None = False,
        seed: int | None = None,
        options: dict | None = None,
    ):
        """Reset.

        Args:
            seed (Optional[int]): seed
            return_info (Optional[bool]): flag to return info as well as observation
            options (Optional[Dict]): options
        """
        # reset our custom attributes
        self.current_turn = 0
        self.total_rewards = {agent: 0.0 for agent in self.possible_agents}

        # reset the ChatArena environment
        self.initial_timestep = self._env.reset()

        # reset the PettingZoo wrapper
        self.agents = self.possible_agents[:]
        self.observations = {agent: {} for agent in self.agents}
        self._cumulative_rewards = {agent: 0.0 for agent in self.agents}
        self.rewards = self.initial_timestep.reward
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        # info keys: turn, new_messages, all_messages, obs_dict, player_name, all_messages_string, restricted_action, moderation_policy, topic
        self.infos = {agent: {} for agent in self.possible_agents}

        # get the first player
        self._agent_selector = self._env.agent_selector
        self.agent_selection = self._agent_selector.reset()

        # get the first observation (but don't return it, as AEC envs use last() for initial obs)
        self.observe(self.agent_selection)

        # render the environment (print the initial scenario text)
        if self.render_mode is not None:
            self.render()

    def step(self, action: str):
        """Steps.

        Steps the agent with an action.

        Args:
            action (str): action
        """
        if (
            self.truncations[self.agent_selection]
            or self.terminations[self.agent_selection]
        ):
            return self._was_dead_step(action)

        agent = self.agent_selection
        timestep = self._env.step(player_name=agent, action=action)

        observation, reward, termination, truncation, info = self._unravel_timestep(
            timestep
        )

        self.observations[agent] = observation
        self.rewards = reward
        self.terminations[agent] = termination
        self.truncations[agent] = truncation
        self.infos[agent] = info

        # If we receive a termination or truncation signal from either agent, the game is over
        if termination:
            self.terminations = {agent: True for agent in self.possible_agents}
        if truncation:
            self.truncations = {agent: True for agent in self.possible_agents}

        # Update total rewards for each agent (in one timestep both agents can get rewards/penalties)
        for agent in self.agents:
            self.total_rewards[agent] += self.rewards[agent]

        # Reset PettingZoo cumulative_rewards attribute (tracks accumulated rewards for an agent since its previous action)
        self._cumulative_rewards[agent] = 0

        if self.render_mode is not None:
            self.render()

        # Print final scores if the env has just terminated (debate moderator final message already shows scores)
        if termination and self.env_name != "debate":
            print(Fore.BLACK + f"TOTAL SCORES: {self.total_rewards}")

        # Get the next agent in PettingZoo, and iterate the underlying environment (used for reward calculations)
        self.agent_selection = self._agent_selector.next()

        # Adds current step rewards to _cumulative_rewards
        self._accumulate_rewards()
