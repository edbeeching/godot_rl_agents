from typing import Any, Optional

import gymnasium as gym
import numpy as np
from numpy import ndarray

from godot_rl.core.godot_env import GodotEnv
from godot_rl.core.utils import lod_to_dol


class CleanRLGodotEnv:
    def __init__(self, env_path: Optional[str] = None, n_parallel: int = 1, seed: int = 0, **kwargs: object) -> None:
        # If we are doing editor training, n_parallel must be 1
        if env_path is None and n_parallel > 1:
            raise ValueError("You must provide the path to a exported game executable if n_parallel > 1")

        # Define the default port
        port = kwargs.pop("port", GodotEnv.DEFAULT_PORT)

        # Create a list of GodotEnv instances
        self.envs = [
            GodotEnv(env_path=env_path, convert_action_space=True, port=port + p, seed=seed + p, **kwargs)
            for p in range(n_parallel)
        ]

        # Store the number of parallel environments
        self.n_parallel = n_parallel

    def _check_valid_action_space(self) -> None:
        # Check if the action space is a tuple space with multiple spaces
        action_space = self.envs[0].action_space
        if isinstance(action_space, gym.spaces.Tuple):
            assert (
                len(action_space.spaces) == 1
            ), f"sb3 supports a single action space, this env contains multiple spaces {action_space}"

    def step(self, action: np.ndarray) -> tuple[ndarray, list[Any], list[Any], list[Any], list[Any]]:
        # Initialize lists for collecting results
        all_obs = []
        all_rewards = []
        all_term = []
        all_trunc = []
        all_info = []

        # Get the number of environments
        num_envs = self.envs[0].num_envs

        # Send actions to each environment
        for i in range(self.n_parallel):
            self.envs[i].step_send(action[i * num_envs : (i + 1) * num_envs])

        # Receive results from each environment
        for i in range(self.n_parallel):
            obs, reward, term, trunc, info = self.envs[i].step_recv()
            all_obs.extend(obs)
            all_rewards.extend(reward)
            all_term.extend(term)
            all_trunc.extend(trunc)
            all_info.extend(info)

        # Convert list of dictionaries to dictionary of lists
        obs = lod_to_dol(all_obs)

        # Return results
        return np.stack(obs["obs"]), all_rewards, all_term, all_trunc, all_info

    def reset(self, seed) -> tuple[ndarray, list[Any]]:
        # Initialize lists for collecting results
        all_obs = []
        all_info = []

        # Reset each environment
        for i in range(self.n_parallel):
            obs, info = self.envs[i].reset()
            all_obs.extend(obs)
            all_info.extend(info)

        # Convert list of dictionaries to dictionary of lists
        obs = lod_to_dol(all_obs)
        return np.stack(obs["obs"]), all_info

    @property
    def single_observation_space(self):
        return self.envs[0].observation_space["obs"]

    @property
    def single_action_space(self):
        return self.envs[0].action_space

    @property
    def num_envs(self) -> int:
        return self.envs[0].num_envs * self.n_parallel

    def close(self) -> None:
        # Close each environment
        for env in self.envs:
            env.close()
