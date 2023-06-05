"""Wrapper to convert a ChatArena environment into a PettingZoo compatible environment."""
from __future__ import annotations

import functools
from typing import Any, Dict, Optional

import pettingzoo
from gymnasium import spaces
from pettingzoo.utils.env import AgentID, ObsType

import chatarena
from chatarena.arena import Arena

import string

CHAR_SET = string.printable


class PettingZooCompatibilityV0(pettingzoo.AECEnv):
    """This compatibility wrapper converts a ChatArena environment into a PettingZoo environment.

    ChatArena (or Chat Arena) is a Multi-Agent Language Game Environments for LLMs. The goal is to develop communication and collaboration capabilities of AIs.
    """

    metadata = {
        "render_modes": ["human"],
        "name": "PettingZooCompatibilityV0",
        "is_parallelizable": False,
    }

    def __init__(
            self,
            env: chatarena.arena.Arena | None = None,
            arena_name: str | None = None,
            string_observation: bool | None = True,
            max_turns: int | None = 25,
            render_mode: str | None = None,
    ):
        """Wrapper to convert a ChatArena environment into a PettingZoo environment.

        Args:
            env (chatarena.arena.Arena): chatarena arena to wrap
            arena_name (Optional[str]): chatarena environment to load from file (e.g., "examples/chameleon.json")
            max_turns (Optional[int]): maximum number of turns before environment truncates
            render_mode (Optional[str]): rendering mode
        """
        super().__init__()

        if env is not None:
            self._env = env
        elif arena_name is not None:
            self._env = Arena.from_config(arena_name)
        else:
            raise ValueError("Arena not specified, please us env or arena_name arguments.")

        self._env.reset()  # this resets the underlying arena as well as each player

        self.possible_agents = list(self._env.name_to_player.keys())
        self.name_to_player_mapping = self._env.name_to_player

        self.string_observation = string_observation
        self.max_turns = max_turns
        self.render_mode = render_mode

        self.terminations = {}
        self.truncations = {}
        self.rewards = {}
        self.infos = {a: {} for a in self.possible_agents}

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent: AgentID):
        """observation_space.

        We get the observation space from the underlying environment.
        Args:
            agent (AgentID): agent
        """
        # TODO: finalize obs space (dicts with agent name may not be necessary)
        observation_space = spaces.Dict(
            {
                agent: spaces.Text(max_length=256, min_length=0, charset=CHAR_SET)
                for agent in self.possible_agents
            }
        )
        return observation_space

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent: AgentID):
        """action_space.

        Get the action space from the underlying environment.

        Args:
            agent (AgentID): agent

        Returns:
            space
        """
        # TODO: finalize action space (this enables agents to send messages to specific other players)
        action_space = spaces.Dict(
            {
                agent: spaces.Text(max_length=256, min_length=0, charset=CHAR_SET)
                for agent in self.possible_agents
            }
        )
        return action_space

    def render(self):
        """render.

        Print the current game state.
        """
        if not hasattr(self, "initial_timestep"):
            raise UserWarning(
                "You must reset the environment using reset() before calling render()."
            )

        self._env.environment.print()
        pass

    def observe(self, agent: AgentID) -> ObsType:
        """observe.

        Args:
            agent (AgentID): agent (e.g., "Player 1")

        Returns:
            observation
        """
        messages = self._env.environment.get_observation(agent)  # this will only return the messages this agent can see
        if len(messages) > 0:
            self.current_turn = messages[-1].turn
        else:
            self.current_turn = 0
        new_messages = [m for m in messages if
                        m.turn == self.current_turn]  # we only send the current timestep messages

        # string observation
        if self.string_observation == True:
            observation = ""
            for m in new_messages:
                observation += f"{m.agent_name}: {m.content}"

        # dict observation
        else:
            observation = {m.agent_name: m.content for m in new_messages}

        self.infos[agent]["obs_dict"] = {m.agent_name: m.content for m in new_messages}

        return observation

    def close(self):
        """close."""
        pass

    def _unravel_timestep(self, timestep: chatarena.arena.TimeStep):
        # get observation
        messages = timestep.observation
        if len(messages) > 0:
            self.current_turn = messages[-1].turn
        else:
            self.current_turn = 0
        new_messages = [m for m in messages if
                        m.turn == self.current_turn]  # we only send the current timestep messages

        # string observation
        if self.string_observation == True:
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
        truncation = self.current_turn > self.max_turns

        # get info
        player_idx = self.possible_agents.index(self.agent_selection)
        player_obj = self._env.players[player_idx]
        info = {"turn": self.current_turn, "global_prompt": player_obj.global_prompt,
                "agent_desc": player_obj.role_desc}

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
            options (Optional[Dict]): options
        """

        if seed is not None:
            print("WARNING: seeding is not supported for LLMs.")

        # reset the chat arena environment
        self.initial_timestep = self._env.reset()
        self.turn = 0

        # get the first player
        self.agent_selection = self._env.environment.get_next_player()

        observation, reward, termination, truncation, info = self._unravel_timestep(self.initial_timestep)

        agent = self.agent_selection
        self.rewards = reward
        self.terminations[agent] = termination
        self.truncations[agent] = truncation
        self.infos[agent] = info

        # all agents
        self.agents = self.possible_agents[:]

        # boilerplate stuff
        self._cumulative_rewards = {a: 0 for a in self.agents}
        self.rewards = self.initial_timestep.reward
        self.terminations = {a: False for a in self.agents}
        self.truncations = {a: False for a in self.agents}

    def step(self, action: str):
        """Steps.

        Steps the agent with an action.

        Args:
            action (str): action
        """
        if (
                self.terminations[self.agent_selection]
                or self.truncations[self.agent_selection]
        ):
            return self._was_dead_step(action)

        agent = self.agent_selection
        timestep = self._env.environment.step(player_name=agent, action=action)

        observation, reward, termination, truncation, info = self._unravel_timestep(timestep)

        self.rewards = reward
        self.terminations[agent] = termination
        self.truncations[agent] = truncation
        self.infos[agent] = info

        self._cumulative_rewards[agent] = 0

        self.agent_selection = self._env.environment.get_next_player()

        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()
