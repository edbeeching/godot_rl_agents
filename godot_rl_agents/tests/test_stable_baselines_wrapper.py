#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 14:16:23 2021

@author: edward

Communication is with messages of json strings

e.g

HANDSHAKING
message = {
    "type"  : "handshake",
    "message":{
        "major_version": "0"
        "minor_version": "1"
        }
}

message = {
    "type" : "env_info"
    "message": {
        "observation_space" : "shape ...",
        "action_space": "shape ...",
        "action_type":" continuous / discrete",
        "n_agents": n_agents       
        }
    }


ACTIONS
OBSERVATIONS

"""


from stable_baselines3 import PPO
from stable_baselines3.common.vec_env.base_vec_env import VecEnv

from godot_rl_agents.core.godot_env import GodotEnv


class StableBaselinesGodotEnv(VecEnv):
    def __init__(self, port=10008, seed=0):
        self.env = GodotEnv(port=port, seed=seed)

    def step(self, action):
        return self.env.step(action)

    def reset(self):
        return self.env.reset()

    def close(self):
        self.env.close()

    def env_is_wrapped(self):
        return [False] * self.env.num_envs

    @property
    def observation_space(self):
        return self.env.observation_space

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def num_envs(self):
        return self.env.num_envs

    def env_method(self):
        raise NotImplementedError()

    def get_attr(self):
        raise NotImplementedError()

    def seed(self):
        raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def step_async(self):
        raise NotImplementedError()

    def step_wait(self):
        raise NotImplementedError()


if __name__ == "__main__":
    from stable_baselines3.common.env_checker import check_env

    env = StableBaselinesGodotEnv()

    #    check_env(env)

    # obs_buff = []
    # reward_buff = []
    # done_buff = []
    # action_buff = []

    # obs = env.reset()
    # obs_buff.append(obs)
    # for i in range(50):
    #     print(i)
    #     action = np.random.uniform(-1.0, 1.0, size=(9, 2))
    #     obs, reward, done, info = env.step(action)
    #     obs_buff.append(obs)
    #     reward_buff.append(reward)
    #     done_buff.append(done)
    #     action_buff.append(action)

    model = PPO(
        "MlpPolicy",
        env,
        ent_coef=0.0001,
        verbose=2,
        n_steps=32,
        tensorboard_log="logs/log",
    )
    model.learn(20000)
    print("closing env")
    env.close()

#     obs = env.reset()

#     print("obs", obs)

#     while True:
#         action = np.random.uniform(-1.0, 1.0, size=(2,2))
#         obs, reward, done = env.step(action)
#         print(obs, reward, done)

#     # action = 1
#     # obs = env.step(action)
#     # for i in range(200):
#     #     print(env.step(i))
#     #     time.sleep(0.05)
# os = spaces.Box(low=-1.0, high=1.0,shape=(1,4), dtype=np.float32)
