import numpy as np
import ray
import ray.rllib.agents.ppo as ppo
from ray import tune
from ray.rllib.agents import impala
from ray.rllib.utils.annotations import override
from ray.rllib.utils.typing import AgentID, MultiAgentDict, PolicyID
from ray.tune.logger import pretty_print

from godot_rl.wrappers.ray_wrappers import RayVectorGodotEnv

if __name__ == "__main__":
    ray.init()
    tune.register_env(
        "godot",
        lambda c: RayVectorGodotEnv(
            env_path=c["filename"],
            config=c,
            port=c.worker_index + 12010,
            show_window=False,
            framerate=None,
        ),
    )
    config = {
        "env": "godot",
        "env_config": {
            "filename": "envs/test_envs/builds/test_env_identity/TestEnvIdentity.x86_64",
            # "filename": None
        },
        "num_workers": 4,
        "num_envs_per_worker": 16,
        "lr": 0.0003,
        "lambda": 0.95,
        "gamma": 0.99,
        "sgd_minibatch_size": 32,
        "train_batch_size": 256,
        "batch_mode": "truncate_episodes",
        # Use GPUs iff `RLLIB_NUM_GPUS` env var set to > 0.
        "num_gpus": 0,
        "num_sgd_iter": 16,
        "rollout_fragment_length": 8,
        "clip_param": 0.2,
        "entropy_coeff": 0.001,
        "model": {
            "fcnet_hiddens": [8, 8],
        },
        "framework": "torch",
        "no_done_at_end": True,
        "soft_horizon": True,
    }

    stop = {"training_iteration": 2}

    results = tune.run(
        "PPO",
        config=config,
        stop=stop,
        verbose=3,
        checkpoint_freq=5,
        checkpoint_at_end=True,
        restore=None,
    )
    print(results.get_best_trial("episode_reward_mean"))

    ray.shutdown()
