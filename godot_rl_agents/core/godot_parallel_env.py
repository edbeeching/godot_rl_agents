from typing import overload
from godot_rl_agents.core.godot_env import GodotEnv
import os
import time
import pathlib

from sys import platform
import subprocess
import socket
import json
from urllib import response
import numpy as np
from gym import spaces
from ray.rllib.utils.spaces.repeated import Repeated
import atexit


class GodotParallelEnv(GodotEnv):
    def __init__(
        self,
        env_path=None,
        parallel_envs=2,
        #agents_per_env=16,
        dual_step=False,
        starting_port=11008,
        show_window=True,
        seed=0,
        framerate=None,
        action_repeat=None,
    ):
        self.parallel_envs = parallel_envs
        #self.agents_per_env = agents_per_env
        self.dual_step = dual_step

        if env_path is None:
            assert 0, "Godot parallel env only works with compiled executables"

        self.check_platform(env_path)
        self._launch_envs(env_path, starting_port, show_window, framerate, seed, action_repeat)


    def _launch_envs(self, env_path, starting_port, show_window, framerate, seed, action_repeat):
        self._conns = []

        for port in range(starting_port, starting_port+self.parallel_envs):
            proc = self._launch_env(env_path, port, show_window, framerate, seed, action_repeat)
            conn = self._start_server(port)

            self._conns.append(conn)

        for conn in self._conns:
            self._handshake(conn)
        
            # TODO: refactor on godot side
            self._get_env_info(conn) # we repeat this as the godot side expects to receive this message
            
        atexit.register(self._close)

    
    def reset(self):
        message = {
                    "type": "reset",
                }

        results = []
        for conn in self._conns:
            self._send_as_json(message, conn)
            response = self._get_json_dict(conn)
            response["obs"] = self._process_obs(response["obs"])
            assert response["type"] == "reset"
            results.extend(response["obs"])

        return results

    def step(self, actions):
        # split the actions across the envs
        # send all batches of actions
        # receive all batches of responses
        for i, conn in enumerate(self._conns):
            sub_actions = actions[i*self.n_agents:(i+1)*self.n_agents]
            message = {
                "type": "action",
                "action": self.from_numpy(sub_actions),
            }
            self._send_as_json(message, conn)
            
        obs = []
        reward = []
        done = []
        info = []

        for conn in self._conns:
            response = self._get_json_dict(conn)
            response["obs"] = self._process_obs(response["obs"])
            obs.extend(response["obs"])
            reward.extend(response["reward"])
            done.extend(np.array(response["done"]).tolist())
            info.extend([{}] * len(response["done"]))

        return (
            obs,
            reward,
            done, 
            info
        )    
        



    def close(self):
        message = {
            "type": "close",
        }
        for conn in self._conns:
            GodotEnv._send_as_json(message, conn)
            print("close message sent")
            time.sleep(0.1)
            conn.close()
        try:
            atexit.unregister(self._close)
        except Exception as e:
            print("exception unregistering close method", e)



def benchmark(env_path, parallel_envs, action_repeat, framerate, steps):


    env = GodotParallelEnv(env_path=env_path, 
                            parallel_envs=parallel_envs,
                            action_repeat=action_repeat, 
                            framerate=1, 
                            show_window=False)
    start = time.time()
    obs = env.reset()
    total_agents = env.n_agents * env.parallel_envs
    actions = [env.action_space.sample() for _ in range(total_agents)]
    for i in range(steps):
        obs, reward, done, info = env.step(actions)

    diff = time.time() - start
    env.close()
    time.sleep(1)

    n_interactions = steps*total_agents
    interactions_per_second = n_interactions / diff

    return interactions_per_second


if __name__ == "__main__":

    env_string = "envs/builds/VirtualCamera/virtual_camera_opt_{}.x86_64"
    env_names = [ 
        
        # "64_32_render", #
        # "64_128_render", #
        # "64_128_no_render",#
        # "16_32_no_render",#
        # "16_64_no_render",#
        # "16_128_no_render",#
        "32_32_render",#
        "32_64_render",#
        "32_128_render",#
        # "32_32_render", #
        # "32_64_render", #
        # "32_128_render", #
        # "32_128_no_render", #
        ]

    results  = {}

    for name in env_names:
        env_path = f"envs/builds/VirtualCamera/virtual_camera_opt_{name}.x86_64"

        for processes in [4, 12, 24]:
            test_name = f"{name}_{processes}"
            print("running", test_name)
            result = benchmark(env_path, processes, 1, None, 50)
            results[test_name] = result
            

    print(results)
    
