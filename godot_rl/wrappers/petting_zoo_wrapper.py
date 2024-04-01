# PettingZoo wrapper for GDRL
# Multi-agent, where 1 agent corresponds to one AIController instance in Godot
# Based on https://pettingzoo.farama.org/content/environment_creation/#example-custom-parallel-environment
# https://github.com/Farama-Foundation/PettingZoo/?tab=License-1-ov-file#readme
# and adjusted to work with GodotRL and Rllib (made for and tested only with rllib for now)

import functools
from typing import Dict

import numpy as np
from pettingzoo import ParallelEnv

from godot_rl.core.godot_env import GodotEnv


def env(render_mode=None):
    """
    The env function often wraps the environment in wrappers by default.
    You can find full documentation for these methods
    elsewhere in the developer documentation.
    """
    # Not implemented
    return env


class GDRLPettingZooEnv(ParallelEnv):
    metadata = {"render_modes": ["human"], "name": "GDRLPettingZooEnv"}

    def __init__(self, port=GodotEnv.DEFAULT_PORT, show_window=True, seed=0, config: Dict = {}):
        """
        The init method takes in environment arguments and should define the following attributes:
        - possible_agents
        - render_mode

        Note: as of v1.18.1, the action_spaces and observation_spaces attributes are deprecated.
        Spaces should be defined in the action_space() and observation_space() methods.
        If these methods are not overridden, spaces will be inferred from self.observation_spaces/action_spaces, raising a warning.

        These attributes should not be changed after initialization.
        """
        # Initialize the Godot Env which we will wrap
        self.godot_env = GodotEnv(
            env_path=config.get("env_path"),
            show_window=config.get("show_window"),
            action_repeat=config.get("action_repeat"),
            speedup=config.get("speedup"),
            convert_action_space=False,
            seed=seed,
            port=port,
        )

        self.render_mode = None  # Controlled by the env

        self.possible_agents = [agent_idx for agent_idx in range(self.godot_env.num_envs)]
        self.agents = self.possible_agents[:]

        # The policy names here are set on each AIController in Godot editor,
        # used to map agents to policies for multi-policy training.
        self.agent_policy_names = self.godot_env.agent_policy_names

        # optional: a mapping between agent name and ID
        self.agent_name_mapping = dict(zip(self.possible_agents, list(range(len(self.possible_agents)))))

        self.observation_spaces = {
            agent: self.godot_env.observation_spaces[agent_idx] for agent_idx, agent in enumerate(self.agents)
        }

        self.action_spaces = {
            agent: self.godot_env.tuple_action_spaces[agent_idx] for agent_idx, agent in enumerate(self.agents)
        }

    # Observation space should be defined here.
    # lru_cache allows observation and action spaces to be memoized, reducing clock cycles required to get each agent's space.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self.observation_spaces[agent]

    # Action space should be defined here.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self.action_spaces[agent]

    def render(self):
        """
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and understand.
        """
        # Not implemented

    def close(self):
        """
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        """
        self.godot_env.close()

    def reset(self, seed=None, options=None):
        """
        Reset needs to initialize the `agents` attribute and must set up the
        environment so that render(), and step() can be called without issues.
        Returns the observations for each agent
        """
        godot_obs, godot_infos = self.godot_env.reset()

        observations = {agent: godot_obs[agent_idx] for agent_idx, agent in enumerate(self.agents)}
        infos = {agent: godot_infos[agent_idx] for agent_idx, agent in enumerate(self.agents)}

        return observations, infos

    def step(self, actions):
        """
        step(action) takes in an action for each agent and should return the
        - observations
        - rewards
        - terminations
        - truncations
        - infos
        dicts where each dict looks like {agent_1: item_1, agent_2: item_2}
        """

        # Once an agent (AIController) has done = true, it will not receive any more actions until all agents in the
        # Godot env have done = true. For agents that received no actions, we will set zeros instead for
        # compatibility.
        godot_actions = [
            actions[agent] if agent in actions else np.zeros_like(self.action_spaces[agent_idx].sample())
            for agent_idx, agent in enumerate(self.agents)
        ]

        godot_obs, godot_rewards, godot_dones, godot_truncations, godot_infos = self.godot_env.step(
            godot_actions, order_ij=True
        )
        observations = {agent: godot_obs[agent] for agent in actions}
        rewards = {agent: godot_rewards[agent] for agent in actions}

        terminations = {agent: godot_dones[agent] for agent in actions}

        # Truncations are not yet implemented in GDRL API
        truncations = {agent: False for agent in actions}

        # typically there won't be any information in the infos, but there must
        # still be an entry for each agent
        infos = {agent: godot_infos[agent] for agent in actions}

        return observations, rewards, terminations, truncations, infos
