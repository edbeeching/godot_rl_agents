from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env.base_vec_env import VecEnv
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor

from godot_rl.core.godot_env import GodotEnv
from godot_rl.core.utils import can_import, lod_to_dol


class StableBaselinesGodotEnv(VecEnv):
    def __init__(
        self,
        env_path: Optional[str] = None,
        n_parallel: int = 1,
        seed: int = 0,
        **kwargs,
    ) -> None:
        # If we are doing editor training, n_parallel must be 1
        if env_path is None and n_parallel > 1:
            raise ValueError("You must provide the path to a exported game executable if n_parallel > 1")

        # Define the default port
        port = kwargs.pop("port", GodotEnv.DEFAULT_PORT)

        # Create a list of GodotEnv instances
        self.envs = [
            GodotEnv(
                env_path=env_path,
                convert_action_space=True,
                port=port + p,
                seed=seed + p,
                **kwargs,
            )
            for p in range(n_parallel)
        ]

        # Store the number of parallel environments
        self.n_parallel = n_parallel

        # Check the action space for validity
        self._check_valid_action_space()

        # Initialize the results holder
        self.results = None

    def _check_valid_action_space(self) -> None:
        # Check if the action space is a tuple space with multiple spaces
        action_space = self.envs[0].action_space
        if isinstance(action_space, gym.spaces.Tuple):
            assert (
                len(action_space.spaces) == 1
            ), f"sb3 supports a single action space, this env contains multiple spaces {action_space}"

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
            self.envs[i].step_send(action[i * num_envs : (i + 1) * num_envs])

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
        return (
            {k: np.array(v) for k, v in obs.items()},
            np.array(all_rewards, dtype=np.float32),
            np.array(all_term),
            all_info,
        )

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
        return {k: np.array(v) for k, v in obs.items()}

    def close(self) -> None:
        # Close each environment
        for env in self.envs:
            env.close()

    @property
    def observation_space(self) -> gym.Space:
        return self.envs[0].observation_space

    @property
    def action_space(self) -> gym.Space:
        # sb3 is not compatible with tuple/dict action spaces
        return self.envs[0].action_space

    @property
    def num_envs(self) -> int:
        return self.envs[0].num_envs * self.n_parallel

    def env_is_wrapped(self, wrapper_class: type, indices: Optional[List[int]] = None) -> List[bool]:
        # Return a list indicating that no environments are wrapped
        return [False] * (self.envs[0].num_envs * self.n_parallel)

    # Placeholder methods that should be implemented for a full VecEnv implementation
    def env_method(self):
        raise NotImplementedError()

    def get_attr(self, attr_name: str, indices=None) -> List[Any]:
        if attr_name == "render_mode":
            return [None for _ in range(self.num_envs)]
        raise AttributeError("get attr not fully implemented in godot-rl StableBaselinesWrapper")

    def seed(self, seed=None):
        raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def step_async(self, actions: np.ndarray) -> None:
        # Execute the step function asynchronously, not actually implemented in this setting
        self.results = self.step(actions)

    def step_wait(
        self,
    ) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        # Wait for the results from the asynchronous step
        return self.results


def stable_baselines_training(args, extras, n_steps: int = 200000, **kwargs) -> None:
    if can_import("ray"):
        print("WARNING, stable baselines and ray[rllib] are not compatible")
    # Initialize the custom environment
    env = StableBaselinesGodotEnv(env_path=args.env_path, show_window=args.viz, speedup=args.speedup, **kwargs)
    env = VecMonitor(env)

    # Initialize the PPO model
    model = PPO(
        "MultiInputPolicy",
        env,
        ent_coef=0.0001,
        verbose=2,
        n_steps=32,
        tensorboard_log=args.experiment_dir or "logs/sb3",
    )

    # Train the model
    model.learn(n_steps, tb_log_name=args.experiment_name)

    print("closing env")
    env.close()
