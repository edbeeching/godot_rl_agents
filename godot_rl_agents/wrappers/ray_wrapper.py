from typing import Callable, List, Optional, Tuple


import numpy as np

from ray.rllib.env.vector_env import VectorEnv
from ray.rllib.utils.typing import (
    EnvActionType,
    EnvInfoDict,
    EnvObsType,
)
from godot_rl_agents.core.godot_env import GodotEnv
import pathlib
import ray
from ray import tune

import yaml


class RayVectorGodotEnv(VectorEnv):
    def __init__(
        self,
        env_path=None,
        port=10008,
        seed=0,
        show_window=False,
        framerate=None,
        action_repeat=None,
        timeout_wait=60,
        config=None,
    ) -> None:

        self._env = GodotEnv(
            env_path=env_path,
            port=port,
            seed=seed,
            show_window=show_window,
            framerate=framerate,
            action_repeat=action_repeat,
        )
        super().__init__(
            observation_space=self._env.observation_space,
            action_space=self._env.action_space,
            num_envs=self._env.n_agents,
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
        # the env is reset automatically, no need to reset it
        return self.obs[index]


from godot_rl_agents.core.utils import register_env


def rllib_training(args):
    ray.init()

    with open(args.config_file) as f:
        exp = yaml.safe_load(f)
    register_env()

    exp["config"]["env_config"]["env_path"] = args.env_path
    if args.env_path is not None:
        run_name = exp["algorithm"] + "/" + pathlib.Path(args.env_path).stem
    else:
        run_name = exp["algorithm"] + "/editor"
    print("run_name", run_name)

    if args.env_path is None:
        print("SETTING WORKERS TO 1")
        exp["config"]["num_workers"] = 1

    checkpoint_freq = 10
    checkpoint_at_end = True
    if args.eval:
        checkpoint_freq = 0
        exp["config"]["env_config"]["show_window"] = True
        exp["config"]["env_config"]["framerate"] = None
        exp["config"]["lr"] = 0.0
        exp["config"]["num_sgd_iter"] = 1
        exp["config"]["num_workers"] = 1
        exp["config"]["train_batch_size"] = 8192
        exp["config"]["sgd_minibatch_size"] = 128

        exp["config"]["explore"] = False
        exp["stop"]["training_iteration"] = 999999

    print(exp)

    results = tune.run(
        exp["algorithm"],
        name=run_name,
        config=exp["config"],
        stop=exp["stop"],
        verbose=3,
        checkpoint_freq=checkpoint_freq,
        checkpoint_at_end=not args.eval,
        restore=args.restore,
    )
    ray.shutdown()
