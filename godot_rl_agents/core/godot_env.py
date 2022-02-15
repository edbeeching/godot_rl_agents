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


class GodotEnv:
    MAJOR_VERSION = "0"
    MINOR_VERSION = "1"
    DEFAULT_PORT = 11008
    DEFAULT_TIMEOUT = 60

    def __init__(
        self,
        env_path=None,
        port=11008,
        show_window=False,
        seed=0,
        framerate=None,
        action_repeat=None,
    ):

        if env_path is None:
            port = GodotEnv.DEFAULT_PORT
        self.proc = None
        if env_path is not None:
            self.check_platform(env_path)
            self._launch_env(
                env_path, port, show_window, framerate, seed, action_repeat
            )
        else:
            print(
                "No game binary has been provided, please press PLAY in the Godot editor"
            )

        self.port = port
        self.connection = self._start_server()
        self.num_envs = None
        self._handshake()
        self._get_env_info()

        atexit.register(self._close)

    def check_platform(self, filename: str):

        if platform == "linux" or platform == "linux2":
            assert (
                pathlib.Path(filename).suffix == ".x86_64"
            ), f"incorrect file suffix for fileman {filename} suffix {pathlib.Path(filename).suffix }"
        elif platform == "darwin":
            assert 0, "mac is not supported, yet"
            # OS X
        elif platform == "win32":
            # Windows...
            assert (
                pathlib.Path(filename).suffix == ".exe"
            ), f"incorrect file suffix for fileman {filename} suffix {pathlib.Path(filename).suffix }"
        else:
            assert 0, f"unknown filetype {pathlib.Path(filename).suffix}"

        assert os.path.exists(filename)

    def from_numpy(self, action):
        result = []

        for a in action:
            d = {}
            for k, v in a.items():
                if isinstance(v, np.ndarray):
                    d[k] = v.tolist()
                else:
                    d[k] = int(v)
            result.append(d)

        return result

    def step(self, action):
        message = {
            "type": "action",
            "action": self.from_numpy(action),
        }
        self._send_as_json(message)
        response = self._get_json_dict()

        response["obs"] = self._process_obs(response["obs"])

        return (
            response["obs"],
            response["reward"],
            np.array(response["done"]).tolist(),
            [{}] * len(response["done"]),
        )

    def _process_obs(self, response_obs: dict):

        for k in response_obs[0].keys():
            if "2d" in k:
                for sub in response_obs:
                    sub[k] = self.decode_2d_obs_from_string(
                        sub[k], self.observation_space[k].shape
                    )

        return response_obs

    def reset(self):
        # may need to clear message buffer
        # there will be a the next obs to collect
        # _ = self._get_json_dict()
        # self._clear_socket()
        message = {
            "type": "reset",
        }
        self._send_as_json(message)
        response = self._get_json_dict()
        assert response["type"] == "reset"
        obs = np.array(response["obs"])
        return obs

    def call(self, method):
        message = {
            "type": "call",
            "method": method,
        }
        self._send_as_json(message)
        response = self._get_json_dict()

        return response["returns"]

    def close(self):
        message = {
            "type": "close",
        }
        self._send_as_json(message)
        print("close message sent")
        time.sleep(1.0)
        self.connection.close()
        try:
            atexit.unregister(self._close)
        except Exception as e:
            print("exception unregistering close method", e)

    def _close(self):
        print("exit was not clean, using atexit to close env")
        self.close()

    def _launch_env(
        self, env_path, port, show_window, framerate, seed, action_repeat
    ):
        # --fixed-fps {framerate}
        launch_cmd = f"{env_path} --port={port} --env_seed={seed}"

        if show_window == False:
            launch_cmd += " --disable-render-loop --no-window"
        if framerate is not None:
            launch_cmd += f" --fixed-fps {framerate}"
        if action_repeat is not None:
            launch_cmd += f" --action_repeat {action_repeat}"

        launch_cmd = launch_cmd.split(" ")
        self.proc = subprocess.Popen(
            launch_cmd,
            start_new_session=True,
            # shell=True,
        )

    def _start_server(self):
        # Either launch a an exported Godot project or connect to a playing godot game
        # connect to playing godot game

        print(f"waiting for remote GODOT connection on port {self.port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port, "localhost" was not working on windows VM, had to use the IP
        server_address = ("127.0.0.1", self.port)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)
        sock.settimeout(GodotEnv.DEFAULT_TIMEOUT)
        connection, client_address = sock.accept()
        # connection.settimeout(GodotEnv.DEFAULT_TIMEOUT)
        #        connection.setblocking(False) TODO
        print("connection established")
        return connection

    def _handshake(self):
        message = {
            "type": "handshake",
            "major_version": GodotEnv.MAJOR_VERSION,
            "minor_version": GodotEnv.MINOR_VERSION,
        }

        self._send_as_json(message)

    def _get_env_info(self):
        message = {"type": "env_info"}
        self._send_as_json(message)

        json_dict = self._get_json_dict()
        assert json_dict["type"] == "env_info"

        # actions can be "single" for a single action head
        # or "multi" for several outputeads
        action_spaces = {}
        print("action space", json_dict["action_space"])
        for k, v in json_dict["action_space"].items():
            if v["action_type"] == "discrete":
                action_spaces[k] = spaces.Discrete(v["size"])
            elif v["action_type"] == "continuous":
                action_spaces[k] = spaces.Box(
                    low=-1.0, high=1.0, shape=(v["size"],)
                )
            else:
                print(f"action space {v['action_type']} is not supported")
                assert 0, f"action space {v['action_type']} is not supported"
        self.action_space = spaces.Dict(action_spaces)

        observation_spaces = {}
        print("observation space", json_dict["observation_space"])
        for k, v in json_dict["observation_space"].items():
            if v["space"] == "box":
                observation_spaces[k] = spaces.Box(
                    low=-1.0,
                    high=1.0,
                    shape=v["size"],
                    dtype=np.float32,
                )
            elif v["space"] == "discrete":
                observation_spaces[k] = spaces.Discrete(v["size"])
            elif v["space"] == "repeated":
                assert "max_length" in v
                if v["subspace"] == "box":
                    subspace = observation_spaces[k] = spaces.Box(
                        low=-1.0,
                        high=1.0,
                        shape=v["size"],
                        dtype=np.float32,
                    )
                elif v["subspace"] == "discrete":
                    subspace = spaces.Discrete(v["size"])
                observation_spaces[k] = Repeated(subspace, v["max_length"])
            else:
                print(f"observation space {v['space']} is not supported")
                assert 0, f"observation space {v['space']} is not supported"
        self.observation_space = spaces.Dict(observation_spaces)

        self.num_envs = json_dict["n_agents"]

    @staticmethod
    def decode_2d_obs_from_string(
        hex_string,
        shape,
    ):
        return (
            np.frombuffer(bytes.fromhex(hex_string), dtype=np.float16)
            .reshape(shape)
            .astype(np.float32)[:, :, :3]
        )

    def _send_as_json(self, dictionary):
        message_json = json.dumps(dictionary)
        self._send_string(message_json)

    def _get_json_dict(self):
        data = self._get_data()

        return json.loads(data)

    def _get_obs(self):
        return self._get_data()

    def _clear_socket(self):

        self.connection.setblocking(False)
        try:
            while True:
                data = self.connection.recv(4)
                if not data:
                    break
        except BlockingIOError as e:
            # print("BlockingIOError expection on clear")
            pass
        self.connection.setblocking(True)

    def _get_data(self):
        try:
            data = self.connection.recv(4)
            if not data:
                time.sleep(0.000001)
                return self._get_data()
            length = int.from_bytes(data, "little")
            string = self.connection.recv(length).decode()
            return string
        except socket.timeout as e:
            print("env timed out", e)

        return None

    def _send_string(self, string):
        message = len(string).to_bytes(4, "little") + bytes(string.encode())
        self.connection.sendall(message)

    def _send_action(self, action):
        self._send_string(action)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    env = GodotEnv()
    print("observation space", env.observation_space)
    print("action space", env.action_space)
    obs = env.reset()

    for i in range(30):
        # env.reset()
        obs, reward, done, info = env.step([env.action_space.sample()])
        # print(obs, done)
        plt.imshow(obs[0]["camera_2d"][:, :, :3])
        plt.show()
        # print(obs)
    env.close()
