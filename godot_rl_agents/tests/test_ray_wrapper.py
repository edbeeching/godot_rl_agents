import numpy as np

import ray
from ray import tune
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from ray.rllib.utils.annotations import override
from ray.rllib.utils.typing import MultiAgentDict, PolicyID, AgentID

from godot_rl_agents.core.godot_env import GodotEnv

# --fixed-fps 500 --disable-render-loop --no-window


class RayGodotEnv(MultiAgentEnv):
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
        super().__init__()

        print("config", config.worker_index)
        self._env = GodotEnv(
            env_path=env_path,
            port=port,
            seed=seed,
            show_window=show_window,
            framerate=framerate,
        )

    def step(self, action_dict):

        # convert actions dict to numpy array
        actions = []
        for k, v in action_dict.items():
            actions.append(v)
        actions = np.array(actions)

        # step & get obs, etc
        obs, reward, dones, info = self._env.step(actions)
        # return as dict

        dones = self._to_agent_dict(dones)
        for i, done in enumerate(dones):
            if done:
                self.dones.add(i)

        if len(self.dones) == len(dones):
            dones["__all__"] = True  # required by the Ray multienv wrapper
            self.dones = set()
        else:
            dones["__all__"] = False

        return (
            self._to_agent_dict(obs),
            self._to_agent_dict(reward),
            dones,
            self._to_agent_dict(info),
        )

    def reset(self):
        self.dones = set()
        obs = self._env.reset()
        return self._to_agent_dict(obs)

    def _to_agent_dict(self, array):
        result = {}

        for id, value in enumerate(array):
            result[f"agent_id_{id}"] = value
        return result

    @staticmethod
    def get_policy_configs_for_game(game_name, env_path):
        # create a dummy env and extract
        env = GodotEnv(env_path=env_path, port=9999, seed=0)
        obs_space = env.observation_space
        action_space = env.action_space
        policy_space = {game_name: (None, obs_space, action_space, {})}

        env.close()

        def policy_mapping_fn(agent_id):
            return game_name

        return policy_space, policy_mapping_fn


if __name__ == "__main__":
    ray.init()
    tune.register_env(
        "godot_ball_chase",
        lambda c: RayGodotEnv(
            env_path=c["filename"],
            seed=c["seed"],
            config=c,
            port=c.worker_index + 10008,
            show_window=True,
        ),
    )
    policy_space, policy_mapping_fn = RayGodotEnv.get_policy_configs_for_game(
        "godot_ball_chase",
        "envs/build/BallChase/ball_chase_20210823.x86_64",
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
        "multiagent": {
            "policies": policy_space,
            "policy_mapping_fn": policy_mapping_fn,
        },
        "model": {
            "fcnet_hiddens": [256, 256],
        },
        "framework": "torch",
        "no_done_at_end": True,
        "soft_horizon": True,
    }
    stop = {
        "training_iteration": 200,
        "timesteps_total": 20000,
        "episode_reward_mean": 5.0,
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
