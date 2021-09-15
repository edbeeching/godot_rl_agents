import numpy as np

import ray
from ray import tune
from ray.rllib.utils.annotations import override
from ray.rllib.utils.typing import MultiAgentDict, PolicyID, AgentID


from ray.rllib.agents import impala

from ray.tune.logger import pretty_print
import ray.rllib.agents.ppo as ppo
from godot_rl_agents.core.utils import register_env


if __name__ == "__main__":
    ray.init()
    register_env()

    config = {
        "env": "godot",
        "env_config": {
            "filename": "envs/example_envs/builds/JumperHard/jumper_hard.x86_64",
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
        "num_sgd_iter": 16,
        "rollout_fragment_length": 32,
        "clip_param": 0.2,
        "entropy_coeff": 0.001,
        "model": {
            "fcnet_hiddens": [256, 256],
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
    # trainer = ppo.PPOTrainer(config=config, env="godot")

    # # Can optionally call trainer.restore(path) to load a checkpoint.

    # for i in range(100):
    #     # Perform one iteration of training the policy with PPO
    #     result = trainer.train()
    #     print(pretty_print(result))

    #     if i % 10 == 0:
    #         checkpoint = trainer.save()
    #         print("checkpoint saved at", checkpoint)

    # checkpoint = "/home/edward/ray_results/PPO/PPO_godot_658a8_00000_0_2021-08-30_20-23-39/checkpoint_000200/checkpoint-200"
    # print(config)
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

    # trainer = ppo.PPOTrainer(config=config, env="godot")
    # trainer.load_checkpoint(results.get_last_checkpoint())
    # print(trainer.get_policy().get_weights())

    ray.shutdown()
