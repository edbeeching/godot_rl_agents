
import numpy as np
import gym
from godot_rl.core.utils import lod_to_dol
from godot_rl.core.godot_env import GodotEnv


class CleanRLGodotEnv:
    def __init__(self, env_path=None, **kwargs):
        self.env = GodotEnv(env_path=env_path, **kwargs)
        self._check_valid_action_space()

    def _check_valid_action_space(self):
        action_space = self.env.action_space
        if isinstance(action_space, gym.spaces.Tuple):
            assert (
                len(action_space.spaces) == 1
            ), f"clearn rl supports a single action space, this env constains multiple spaces {action_space}"

    def step(self, action):
        obs, reward, term, trunc, info = self.env.step([action])
        obs = lod_to_dol(obs)
        return np.stack(obs["obs"]), reward, term, trunc, info

    def reset(self, seed):
        obs, info = self.env.reset(seed)
        obs = lod_to_dol(obs)
        return np.stack(obs["obs"]), info

    @property
    def single_observation_space(self):
        return self.env.observation_space["obs"]

    @property
    def single_action_space(self):
        return self.env.action_space[0]

    @property
    def num_envs(self):
        return self.env.num_envs