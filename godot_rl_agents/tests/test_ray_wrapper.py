import numpy as np

import ray
from ray import tune
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from ray.rllib.utils.annotations import override
from ray.rllib.utils.typing import MultiAgentDict, PolicyID, AgentID
from ray.rllib.env.vector_env import VectorEnv
from typing import Callable, List, Optional, Tuple

from ray.rllib.utils.typing import (
    EnvActionType,
    EnvConfigDict,
    EnvInfoDict,
    EnvObsType,
    EnvType,
    PartialTrainerConfigDict,
)
from ray.rllib.agents import impala

from godot_rl_agents.core.godot_env import GodotEnv


class RayVectorGodotEnv(VectorEnv):
    def __init__(
        self,
        env_path=None,
        port=10008,
        seed=0,
        show_window=False,
        framerate=60,
        timeout_wait=60,
        config=None,
    ) -> None:
        #

        print("config", config.worker_index)
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


if __name__ == "__main__":
    ray.init()
    tune.register_env(
        "jumper",
        lambda c: RayVectorGodotEnv(
            env_path=c["filename"],
            config=c,
            port=c.worker_index + 12010,
            show_window=True,
            framerate=30,
        ),
    )
    config = {
        "env": "jumper",
        "env_config": {
            "filename": "envs/build/Jumper/jumper.x86_64",
            # "filename": None,
            "seed": None,
        },
        # For running in editor, force to use just one Worker (we only have
        # one Unity running)!
        "num_workers": 4,
        "num_envs_per_worker": 16,
        # "remote_worker_envs": True,
        # Other settings.
        "lr": 0.0003,
        "lambda": 0.95,
        "gamma": 0.99,
        "sgd_minibatch_size": 128,
        "train_batch_size": 1024,
        "batch_mode": "truncate_episodes",
        # Use GPUs iff `RLLIB_NUM_GPUS` env var set to > 0.
        "num_gpus": 0,
        "num_sgd_iter": 8,
        "rollout_fragment_length": 32,
        "clip_param": 0.2,
        "entropy_coeff": 0.001,
        "model": {
            "fcnet_hiddens": [64, 64],
        },
        "framework": "torch",
        "no_done_at_end": True,
        "soft_horizon": True,
    }

    stop = {
        "training_iteration": 200,
        "timesteps_total": 1000000,
        "episode_reward_mean": 400.0,
    }
    print(config)
    # Run the experiment.
    results = tune.run(
        "PPO",
        config=config,
        stop=stop,
        verbose=3,
        checkpoint_freq=5,
        checkpoint_at_end=True,
        restore=None,
    )

    ray.shutdown()
