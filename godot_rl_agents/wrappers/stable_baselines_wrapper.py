from stable_baselines3 import PPO
from stable_baselines3.common.vec_env.base_vec_env import VecEnv

from godot_rl_agents.core.godot_env import GodotEnv
import numpy as np

class StableBaselinesGodotEnv(VecEnv):
    def __init__(self, env_path=None, port=10008, seed=0, show_window=False):
        self.env = GodotEnv(env_path=env_path, port=port, seed=seed, show_window=show_window, framerate=5)
        self.num_agents = self.env.n_agents

        self._action_key = None
        self._convert_action_space()
        self._convert_observation_space()

    def _convert_action_space(self):
        assert len(self.env.action_space) == 1, "only single action spaces are supported by stable_baselines"
        self._action_key = list(self.env.action_space.spaces.keys())[0]

    def _convert_observation_space(self):
        obs_space = self.env.observation_space["camera_2d"]
        obs_space.shape = (obs_space.shape[2], obs_space.shape[0], obs_space.shape[1])
        self._observation_space = obs_space

    def step(self, action):
        action = {
            self._action_key: action
        }
        action = self.dol_to_lod(action)  
        obs, reward, done, info = self.env.step(action)
        #return self.lod_to_dol(obs), reward, np.array(done), info 
        return self.to_numpy(obs), np.array(reward), np.array(done), info 


    @staticmethod
    def lod_to_dol(lod):
        return {k: [dic[k] for dic in lod] for k in lod[0]}

    @staticmethod
    def dol_to_lod(dol):
        return [dict(zip(dol,t)) for t in zip(*dol.values())] 

    @staticmethod
    def to_numpy(lod):
        
        for d in lod:
            for k,v in d.items():
                d[k] = np.array(v).transpose(1,2,0)

        return lod

    def reset(self):
        obs = self.env.reset()
        #return self.lod_to_dol(obs) 
        return self.to_numpy(obs)

    def close(self):
        self.env.close()

    def env_is_wrapped(self):
        return [False] * self.env.n_agents

    @property
    def observation_space(self):
        return self._observation_space

    @property
    def action_space(self):
        return self.env.action_space[self._action_key]

    @property
    def num_envs(self):
        return self.env.n_agents

    def env_method(self):
        raise NotImplementedError()

    def get_attr(self):
        raise NotImplementedError()

    def seed(self, value):
        # this is done when the env is initialized
        return
        #raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def step_async(self):
        raise NotImplementedError()

    def step_wait(self):
        raise NotImplementedError()

    def reward_range(self):
        return (-np.inf, np.inf)


def stable_baselines_training(args):
    print(
        "Stable-baselines3 is currently unsupported due to issue: https://github.com/DLR-RM/stable-baselines3/issues/731"
    )
    raise NotImplementedError


if __name__ == "__main__":

    env = StableBaselinesGodotEnv()

    print(env.action_space)
    print(env.observation_space)
    # obs = env.reset()

    # model = PPO(
    #     "MultiInputPolicy",
    #     env,
    #     ent_coef=0.0001,
    #     verbose=2,
    #     n_steps=32,
    #     tensorboard_log="logs/log",
    # )
    # model.learn(20000)
    # print("closing env")
    # env.close()
