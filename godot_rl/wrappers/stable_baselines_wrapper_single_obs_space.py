from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
from godot_rl.core.godot_env import GodotEnv
from godot_rl.core.utils import can_import, lod_to_dol
from stable_baselines3 import PPO
from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv
from stable_baselines3.common.vec_env.base_vec_env import VecEnv
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor

# A variant of the wrapper that only supports a single obs space from the dictionary ("obs")
# this allows some basic support for using envs that have a single obs space with policies other than MultiInputPolicy

class StableBaselinesGodotEnvSingleObsSpace(StableBaselinesGodotEnv):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def step(self, action: np.ndarray) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray, List[Dict[str, Any]]]:
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
            self.envs[i].step_send(action[i * num_envs:(i + 1) * num_envs])

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
        return np.stack(obs["obs"]), np.array(all_rewards), np.array(all_term), all_info

    def reset(self) -> Dict[str, np.ndarray]:
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
        return np.stack(obs["obs"])

    @property
    def observation_space(self) -> gym.Space:
            return self.envs[0].observation_space["obs"]
