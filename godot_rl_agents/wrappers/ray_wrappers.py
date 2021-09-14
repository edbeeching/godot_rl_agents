from typing import Callable, List, Optional, Tuple

import numpy as np

from ray.rllib.env.vector_env import VectorEnv
from ray.rllib.utils.typing import (
    EnvActionType,
    EnvConfigDict,
    EnvInfoDict,
    EnvObsType,
    EnvType,
    PartialTrainerConfigDict,
)
from godot_rl_agents.core.godot_env import GodotEnv


class RayVectorGodotEnv(VectorEnv):
    def __init__(
        self,
        env_path=None,
        port=10008,
        seed=0,
        show_window=False,
        framerate=None,
        timeout_wait=60,
        config=None,
    ) -> None:

        self._env = GodotEnv(
            env_path=env_path,
            port=port,
            seed=seed,
            show_window=show_window,
            framerate=framerate,
        )
        super().__init__(
            observation_space=self._env.observation_space,
            action_space=self._env.action_space,
            num_envs=self._env.num_envs,
        )

    def vector_reset(self) -> List[EnvObsType]:
        return self._env.reset()

    def vector_step(
        self, actions: List[EnvActionType]
    ) -> Tuple[List[EnvObsType], List[float], List[bool], List[EnvInfoDict]]:
        actions = np.array(actions)
        self.obs, reward, done, info = self._env.step(actions)
        return self.obs, reward, done, info

    def get_unwrapped(self):
        return [self._env]

    def reset_at(self, index: Optional[int]) -> EnvObsType:
        # obs = self.vector_reset()

        return self.obs[index]
