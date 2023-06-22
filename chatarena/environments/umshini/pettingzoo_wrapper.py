"""Wrapper to convert a ChatArena environment into a PettingZoo compatible environment."""
# pyright: reportGeneralTypeIssues=false, reportUnboundVariable=false, reportOptionalMemberAccess=false
from __future__ import annotations

import functools
import string
import re

import numpy as np
import pygame
from chatarena.environments import Environment
from chatarena.environments.base import TimeStep
from gymnasium import spaces
from gymnasium.utils import EzPickle
from pettingzoo import AECEnv
from pettingzoo.utils.env import AgentID, ObsType

from chatarena.environments.umshini.debate import create_debate_env
from chatarena.environments.umshini.symmetric_content_moderation import (
    create_content_moderation_env,
)
from chatarena.environments.umshini.symmetric_deception import create_deception_env

CHAR_SET = string.printable


class PettingZooCompatibilityV0(AECEnv, EzPickle):
    """This compatibility wrapper converts a ChatArena environment into a PettingZoo environment.

    Unique arguments for umshini environments: env_name topic, moderation_policy, restricted_action, player_names, round_length
    """

    metadata = {
        "render_modes": ["human", "rgb_array", "text"],
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
        )
        super().__init__()

        if env is None and env_name is None:
            raise TypeError(
                "ChatArena Environment or environment name must be specified"
            )
        elif env is not None:
            # TODO: test that human rendering works with this
            self._env = env
            if hasattr(env, "topic"):
                self.topic = topic
                self.max_turns = round_length
            elif hasattr(env, "moderation_policy"):
                self.moderation_policy = env.moderation_policy
                self.max_turns = round_length * 2
            elif hasattr(env, "restricted_action"):
                self.restricted_action = env.restricted_action
                self.max_turns = round_length * 2
        elif env_name is not None:
            if env_name == "debate":
                assert topic is not None, "topic must be specified for debate env"
                self._env = create_debate_env(
                    topic=topic, player_names=player_names, round_length=round_length
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
                )
                self.restricted_action = restricted_action
                self.max_turns = round_length * 2
            else:
                raise TypeError(
                    f"Environment not found: {env_name}. Options: debate, content_moderation, deception"
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

        if self.render_mode in ["human", "rgb_array"]:
            pygame.init()
            self.screen_width = 1024
            self.screen_height = 1024

            if self.render_mode == "human":
                self.screen = pygame.display.set_mode(
                    (self.screen_width, self.screen_height)
                )
                self.clock = pygame.time.Clock()
            elif self.render_mode == "rgb_array":
                self.screen = pygame.Surface((self.screen_width, self.screen_height))

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
        """observation_space.

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
        """action_space.

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
        """render.

        Print the current game state.
        """
        if not hasattr(self, "initial_timestep"):
            raise UserWarning(
                "You must reset the environment using reset() before calling render()."
            )

        if self.render_mode in ["human", "rgb_array"] :
            self.screen.fill("black")
            font = pygame.font.Font(None, 32)  # default font
            self.line_spacing = 10
            self.border_padding = 10

            obs_list = []

            # --- Iterate through messages and print sequentially, scrolling ---
            all_messages = self.infos[self.agent_selection]["all_messages"]
            surfs = []
            heights = []
            color_map = dict(zip(self.all_agents, ["white", "green", "yellow"]))
            # For all messages besides the most recent, print at once
            for message in all_messages[:-1]:
                text = f"[{message.agent_name}->{message.visible_to} @ {message.turn}]: {message.content}"
                text_surf = font.render(
                    text,
                    True,
                    color_map[message.agent_name],
                    None,  # or (0, 0, 0, 0) for example
                    self.screen_width,
                )
                surfs.append(text_surf)
                heights.append(text_surf.get_height() + self.line_spacing)

            # TODO: after I added this, it seemed to cut the moderation off at the end, but may be a coincidence
            # --- Render this frame ---
            # Pad rendering from the edges of the screen
            for i, surf in enumerate(surfs):
                self.screen.blit(
                    surf, (self.border_padding, self.border_padding + sum(heights[:i]))
                )

            if self.render_mode == "human":
                self.clock.tick(5 * self.metadata["render_fps"])
                pygame.display.update()

            elif self.render_mode == "rgb_array":
                # Get observation from pygame surface for rgb_array
                observation = np.array(pygame.surfarray.pixels3d(self.screen))
                obs_list.append(np.transpose(observation, axes=(1, 0, 2)))


            # --- Loop over the most recent message and print iteratively ---
            if len(all_messages) > 1:
                message = all_messages[-1]
                text = f"[{message.agent_name}->{message.visible_to} @ {message.turn}]:"
                text_surf = font.render(
                    text,
                    True,
                    color_map[message.agent_name],
                    None,  # or (0, 0, 0, 0) for example
                    self.screen_width,
                )
                surfs.append(text_surf)
                heights.append(text_surf.get_height() + self.line_spacing)

                # Split words by spaces and iteratively print
                words = re.sub(' ', ' \t', message.content).split('\t')
                for char in words:
                    text += char

                    text_surf = font.render(
                        text,
                        True,
                        color_map[message.agent_name],
                        None,  # or (0, 0, 0, 0) for example
                        self.screen_width,
                    )

                    # TODO: if we fix the below bug, this isn't necessary
                    if len(surfs) > 1:
                        surfs[-1] = text_surf
                        heights[-1] = text_surf.get_height() + self.line_spacing
                    else:
                        surfs = [text_surf]
                        heights = [text_surf.get_height() + self.line_spacing]

                    # TODO: this seems to happen too many times, leaving the surfs list empty sometimes
                    # Removes the top messages if needed, to ensure text never goes off-screen
                    # Accounts for height of each message plus top and bottom padding
                    while sum(heights) + self.border_padding * 2 > self.screen_height:
                        surfs.pop(0)
                        heights.pop(0)
                        self.screen.fill("black") # remove the previous messages

                    # --- Render this frame ---
                    # Pad rendering from the edges of the screen
                    for i, surf in enumerate(surfs):
                        self.screen.blit(
                            surf, (self.border_padding, self.border_padding + sum(heights[:i]))
                        )

                    if self.render_mode == "human":
                        self.clock.tick(5 * self.metadata["render_fps"])
                        pygame.display.update()

                    elif self.render_mode == "rgb_array":
                        # Get observation from pygame surface for rgb_array
                        observation = np.array(pygame.surfarray.pixels3d(self.screen))
                        obs_list.append(np.transpose(observation, axes=(1, 0, 2)))

            return obs_list

        elif self.render_mode == "text":
            new_messages = self.infos[self.agent_selection].get("new_messages")
            if new_messages is None:
                raise Exception("New messages not found")
            else:
                print("new message!")
                for message in new_messages:
                    print(
                        f"[{message.agent_name}->{message.visible_to}]: {message.content}\n"
                    )


    def observe(self, agent: AgentID) -> ObsType:
        """observe.

        Args:
            agent (AgentID): agent (e.g., "Player 1")

        Returns:
            observation
        """
        # When PettingZoo agents die, they are removed from the info dict (as well as obs, cumulative rewards, termination, truncation)
        if agent not in self.agents:
            return None
        # Observations and infos are calculated in step(), but need to be calculated before the first step() call
        elif type(agent) != str:
            raise TypeError("AgentID must be a string")
        elif self.observations[agent] != {}:
            return self.observations[agent]
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
            if self.string_observation is True:
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

            # info: generate string of full chat log
            if self.string_observation is True:
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
        """close."""
        if self.screen is not None:
            pygame.quit()
            self.screen = None

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
        if self.string_observation is True:
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
        if self.string_observation is True:
            all_messages_string = ""
            for m in messages:
                all_messages_string += f"[{m.agent_name}->all]: {m.content}\n"
            info["all_messages_string"] = all_messages_string

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
        """reset.

        Args:
            seed (Optional[int]): seed
            return_info (Optional[bool]): flag to return info as well as observation
            options (Optional[Dict]): options
        """
        if seed is not None:
            print("WARNING: seeding is not supported for LLMs.")

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
        self.infos = {
            agent: {}
            for agent in self.possible_agents
        }

        # get the first player
        self._agent_selector = self._env.agent_selector
        self.agent_selection = self._agent_selector.reset()

        # get the first observation
        observation = self.observe(self.agent_selection)
        info = self.infos[self.agent_selection]

        # render the environment (print the initial scenario text, or render with pygame)
        if self.render_mode is not None:
            self.render()

        return observation, info

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
        # add moderator messages to info so they are rendered
        # some environments (e.g., debate) have the moderator announce the winner as the last message
        if termination or truncation:
            if info["all_messages"][-1].agent_name == "Moderator":
                info["new_messages"].append(info["all_messages"][-2])

        # account for the moderator interjecting statements such as "roles are being swapped"
        # first turn we already render the moderator's message, so we don't need to add the message here
        if info["turn"] > 1:
            if len(info["all_messages"]) > 1 and info["all_messages"][-2].agent_name == "Moderator":
                info["new_messages"].append(info["all_messages"][-2])

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
        self.total_rewards[agent] += self._cumulative_rewards[agent]

        # Reset PettingZoo cumulative_rewards attribute (tracks accumulated rewards for an agent since its previous action)
        self._cumulative_rewards[agent] = 0

        if self.render_mode == "human":
            self.render()

        # Get the next agent in PettingZoo, and iterate the underlying environment (used for reward calculations)
        self.agent_selection = self._agent_selector.next()

        # Adds current step rewards to _cumulative_rewards
        self._accumulate_rewards()
