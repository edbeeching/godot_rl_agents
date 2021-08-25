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
from godot_rl_agents.core.godot_env import GodotEnv


class RayVectorGodotEnv(VectorEnv):
    def __init__(
        self,
        env_path=None,
        port=10010,
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
        "godot_ball_chase",
        lambda c: RayVectorGodotEnv(
            env_path=c["filename"],
            seed=c["seed"],
            config=c,
            port=c.worker_index + 10008,
            show_window=True,
        ),
    )
    config = {
        "env": "godot_ball_chase",
        "env_config": {
            "filename": "envs/build/BallChase/ball_chase_20210823.x86_64",
            "seed": None,
        },
        # For running in editor, force to use just one Worker (we only have
        # one Unity running)!
        "num_workers": 4,
        "num_envs_per_worker": 13,
        # "remote_worker_envs": True,
        # Other settings.
        "lr": 0.0003,
        "lambda": 0.95,
        "gamma": 0.99,
        "sgd_minibatch_size": 32,
        "train_batch_size": 256,
        "batch_mode": "truncate_episodes",
        # Use GPUs iff `RLLIB_NUM_GPUS` env var set to > 0.
        "num_gpus": 1,
        "num_sgd_iter": 16,
        "rollout_fragment_length": 4,
        "clip_param": 0.2,
        # Multi-agent setup for the particular env.
        # "multiagent": {
        #     "policies": policy_space,
        #     "policy_mapping_fn": policy_mapping_fn,
        # },
        "model": {
            "fcnet_hiddens": [256, 256],
        },
        "framework": "torch",
        "no_done_at_end": True,
        "soft_horizon": True,
    }
    stop = {
        "training_iteration": 200,
        "timesteps_total": 100000,
        "episode_reward_mean": 50.0,
    }
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
