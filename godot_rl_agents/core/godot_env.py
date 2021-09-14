import os
import time
import pathlib

from sys import platform
import subprocess
import socket
import json
import numpy as np
from gym import spaces
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
    ):

        if env_path is None:
            port = GodotEnv.DEFAULT_PORT
        self.proc = None
        if env_path is not None:
            self.check_platform(env_path)
            self._launch_env(env_path, port, show_window, framerate)
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

        return (
            np.array(response["obs"]),
            response["reward"],
            np.array(response["done"]).tolist(),
            [{}] * len(response["done"]),
        )

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

    def _launch_env(self, env_path, port, show_window, framerate):
        # --fixed-fps {framerate}
        launch_cmd = f"{env_path} --port={port}"

        if show_window == False:
            launch_cmd += " --disable-render-loop --no-window"
        if framerate is not None:
            launch_cmd += f" --fixed-fps {framerate}"
        launch_cmd = launch_cmd.split(" ")
        print(launch_cmd)
        self.proc = subprocess.Popen(
            launch_cmd,
            # start_new_session=True,
            # shell=True,
        )

    def _start_server(self):
        # Either launch a an exported Godot project or connect to a playing godot game
        # connect to playing godot game

        print(f"waiting for remote GODOT connection on port {self.port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ("localhost", self.port)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)
        connection, client_address = sock.accept()
        connection.settimeout(GodotEnv.DEFAULT_TIMEOUT)
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
        self.action_space = spaces.Dict(action_spaces)
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(json_dict["obs_size"],), dtype=np.float32
        )

        self.num_envs = json_dict["n_agents"]

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
