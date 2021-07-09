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

import gym
import socket
import time
import json
import numpy as np

from gym import spaces

MAJOR_VERSION = 0
MINOR_VERSION = 1


class GodotEnv(gym.Env):
    def __init__(self, port=10008):
        self.port = port
        self.connection = self._start_server()
        self._handshake()
        self._get_env_info()
        

    def step(self, action):
        print("Stepping")
        message = {
            "type": "action",
            "action": action.tolist(),
        }
        self._send_as_json(message)
        response = self._get_json_dict()

        return np.array(response["obs"][0]), response["reward"][0], response["done"][0], {}

    def reset(self):
        message = self._get_json_dict()
        obs = np.array(message["obs"][0])
        print(obs.shape, self.observation_space.shape)
        return obs

    def close(self):
        self.connection.close()

    def _start_server(self):
        # Either launch a an exported Godot project or connect to a playing godot game
        # connect to playing godot game

        print("waiting for remote GODOT connection")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ("localhost", self.port)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)
        connection, client_address = sock.accept()
        print("connection established")
        return connection

    def _handshake(self):
        message = {
            "type": "handshake",
            "major_version": "0",
            "minor_version": "1",
        }

        self._send_as_json(message)

    def _get_env_info(self):
        message = {"type": "env_info"}
        self._send_as_json(message)

        json_dict = self._get_json_dict()
        assert json_dict["type"] == "env_info"
        n_actions = json_dict["action_size"]
        if json_dict["action_type"] == "discrete":
            self.action_space = spaces.Discrete(n_actions)
        elif json_dict["action_type"] == "continuous":
            self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1, n_actions))
        
        self.observation_space = spaces.Box(low=-1.0, high=1.0,
                                        shape=(json_dict["obs_size"],), dtype=np.float32)

    def _send_as_json(self, dictionary):
        message_json = json.dumps(dictionary)
        self.send_string(message_json)

    def _get_json_dict(self):
        data = self.get_data()

        return json.loads(data)

    def _get_obs(self):

        return self.get_data()

    def get_data(self):
        data = self.connection.recv(4)
        if not data:
            time.sleep(0.001)
            return self.get_data()
        length = int.from_bytes(data, "little")
        string = self.connection.recv(length).decode()
        return string

    def send_string(self, string):

        message = len(string).to_bytes(4, "little") + bytes(string.encode())
        print("send message", message)
        self.connection.sendall(message)

    def _send_action(self, action):
        self.send_string(action)


if __name__ == "__main__":
    from stable_baselines3.common.env_checker import check_env
    env = GodotEnv()
    
    check_env(env)
    
    
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