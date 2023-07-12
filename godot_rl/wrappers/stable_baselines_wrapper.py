import gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env.base_vec_env import VecEnv

from godot_rl.core.godot_env import GodotEnv
from godot_rl.core.utils import lod_to_dol


class StableBaselinesGodotEnv(VecEnv):
    def __init__(self, env_path=None, n_parallel=1, **kwargs):
        port = kwargs.pop("port", GodotEnv.DEFAULT_PORT)
        self.envs = [GodotEnv(env_path=env_path, convert_action_space=True, port=port+p, **kwargs) for p in range(n_parallel)]
        self.n_parallel = n_parallel
        self._check_valid_action_space()
        self.results = None

    def _check_valid_action_space(self):
        action_space = self.envs[0].action_space
        if isinstance(action_space, gym.spaces.Tuple):
            assert (
                len(action_space.spaces) == 1
            ), f"sb3 supports a single action space, this env constains multiple spaces {action_space}"

    def step(self, action):
        all_obs = []
        all_rewards = []
        all_term = []
        all_trunc = []
        all_info = []
        
        num_envs = self.envs[0].num_envs
        # Decouple sending actions from receiveing observations
        for i in range(self.n_parallel):
            self.envs[i].step_send(action[i*num_envs:(i+1)*num_envs])
            
        for i in range(self.n_parallel):
            obs, reward, term, trunc, info = self.envs[i].step_recv()
            all_obs.extend(obs)
            all_rewards.extend(reward)
            all_term.extend(term)
            all_trunc.extend(trunc)
            all_info.extend(info)
            
        obs = lod_to_dol(all_obs)
        return {k: np.array(v) for k, v in obs.items()}, np.array(all_rewards), np.array(all_term), all_info

    def reset(self):
        all_obs = []
        all_info = []
        for i in range(self.n_parallel):
            obs, info = self.envs[i].reset()
            all_obs.extend(obs)
            all_info.extend(info)
            
        obs = lod_to_dol(all_obs)
        obs = {k: np.array(v) for k, v in obs.items()}
        return obs

    def close(self):
        for env in self.envs:
            env.close()

    def env_is_wrapped(self, wrapper_class, indices = None):
        return [False] * (self.envs[0].num_envs * self.n_parallel)

    @property
    def observation_space(self):
        return self.envs[0].observation_space

    @property
    def action_space(self):
        # sb3 is not compatible with tuple/dict action spaces
        return self.envs[0].action_space

    @property
    def num_envs(self):
        return self.envs[0].num_envs * self.n_parallel

    def env_method(self):
        raise NotImplementedError()

    def get_attr(self):
        raise NotImplementedError()

    def seed(self):
        raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def step_async(self, actions: np.ndarray):
        # raise NotImplementedError()
        # only works for single instances
        self.results = self.step(actions)

    def step_wait(self):
        # raise NotImplementedError()
        # only works for single instances
        return self.results


def stable_baselines_training(args, extras, n_steps=200000, **kwargs):
    # TODO: Add cla etc for sb3
    env = StableBaselinesGodotEnv(env_path=args.env_path, show_window=args.viz, speedup=args.speedup, **kwargs)

    model = PPO(
        "MultiInputPolicy",
        env,
        ent_coef=0.0001,
        verbose=2,
        n_steps=32,
        tensorboard_log="logs/log",
    )
    model.learn(n_steps)

    print("closing env")
    env.close()
