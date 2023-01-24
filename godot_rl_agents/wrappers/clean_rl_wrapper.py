
import numpy as np
import gym
from godot_rl.core.utils import lod_to_dol
from godot_rl.core.godot_env import GodotEnv


class CleanRLGodotEnv:
    def __init__(self, env_path=None, convert_action_space=False, **kwargs):
        # convert_action_space: combine multiple continue action spaces into one larger space 
        self._env = GodotEnv(env_path=env_path,convert_action_space=convert_action_space, **kwargs)
        

    def _check_valid_action_space(self):
        action_space = self._env.action_space
        if isinstance(action_space, gym.spaces.Tuple):
            assert (
                len(action_space.spaces) == 1
            ), f"clearn rl supports a single action space, this env constains multiple spaces {action_space}"

    @staticmethod
    def action_preprocessor(action):
        return action

    def step(self, action):
        action = self.action_preprocessor(action)
        obs, reward, term, trunc, info = self._env.step(action)
        obs = lod_to_dol(obs)
        return np.stack(obs["obs"]), reward, term, trunc, info

    def reset(self, seed):
        obs, info = self._env.reset(seed)
        obs = lod_to_dol(obs)
        return np.stack(obs["obs"]), info

    @property
    def single_observation_space(self):
        return self._env.observation_space["obs"]

    @property
    def single_action_space(self):
        return self._env.action_space
        

    @property
    def num_envs(self):
        return self._env.num_envs