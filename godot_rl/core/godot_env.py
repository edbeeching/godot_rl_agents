import atexit
import json
import os
import pathlib
import socket
import subprocess
import time
from collections import OrderedDict
from sys import platform
from typing import Optional

import numpy as np
from gymnasium import spaces

from godot_rl.core.utils import ActionSpaceProcessor, convert_macos_path


class GodotEnv:
    MAJOR_VERSION = "0"  # Versioning for the environment
    MINOR_VERSION = "7"
    DEFAULT_PORT = 11008  # Default port for communication with Godot Game
    DEFAULT_TIMEOUT = 60  # Default socket timeout TODO

    def __init__(
        self,
        env_path: str = None,
        port: int = DEFAULT_PORT,
        show_window: bool = False,
        seed: int = 0,
        framerate: Optional[int] = None,
        action_repeat: Optional[int] = None,
        speedup: Optional[int] = None,
        convert_action_space: bool = False,
    ):
        """
        Initialize a new instance of GodotEnv

        Args:
            env_path (str): path to the godot binary environment.
            port (int): Port number for communication.
            show_window (bool): flag to display Godot game window.
            seed (int): seed to initialize the environment.
            framerate (int): the framerate to run the Godot game at.
            action_repeat (int): the number of frames to repeat an action for.
            speedup (int): the factor to speedup game time by.
            convert_action_space (bool): flag to convert action space.
        """

        self.proc = None
        if env_path is not None and env_path != "debug":
            env_path = self._set_platform_suffix(env_path)

            self.check_platform(env_path)
            self._launch_env(env_path, port, show_window, framerate, seed, action_repeat, speedup)
        else:
            print("No game binary has been provided, please press PLAY in the Godot editor")

        self.port = port
        self.connection = self._start_server()
        self.num_envs = None
        self._handshake()

        # Action and observation spaces for each in-game agent/env/AIController (used only for multi-agent case with Rllib for now)
        self.action_spaces = []
        self.observation_spaces = []

        self._get_env_info()

        # Single-agent observation space
        self.observation_space = self.observation_spaces[0]

        # sf2 requires a tuple action space
        # Multiple agents' action space(s)
        self.tuple_action_spaces = [
            spaces.Tuple([v for _, v in action_space.items()]) for action_space in self.action_spaces
        ]
        # Single agent action space processor using the action space(s) of the first agent
        self.action_space_processor = ActionSpaceProcessor(self.tuple_action_spaces[0], convert_action_space)

        # For multi-policy envs: The name of each agent's policy set in the env itself (any training_mode
        # AIController instance is treated as an agent)
        self.agent_policy_names

        atexit.register(self._close)

    def _set_platform_suffix(self, env_path: str) -> str:
        """
        Set the platform suffix for the given environment path based on the platform.

        Args:
            env_path (str): The environment path.

        Returns:
            str: The environment path with the platform suffix.
        """
        suffixes = {
            "linux": ".x86_64",
            "linux2": ".x86_64",
            "darwin": ".app",
            "win32": ".exe",
        }
        suffix = suffixes[platform]
        return str(pathlib.Path(env_path).with_suffix(suffix))

    def check_platform(self, filename: str):
        """
        Check the platform and assert the file type

        Args:
            filename (str): Path of the file to check.

        Raises:
            AssertionError: If the file type does not match with the platform or file does not exist.
        """
        if platform == "linux" or platform == "linux2":
            # Linux
            assert (
                pathlib.Path(filename).suffix == ".x86_64"
            ), f"Incorrect file suffix for {filename=} {pathlib.Path(filename).suffix=}. Please provide a .x86_64 file"
        elif platform == "darwin":
            # OSX
            assert (
                pathlib.Path(filename).suffix == ".app"
            ), f"Incorrect file suffix for {filename=} {pathlib.Path(filename).suffix=}. Please provide a .app file"
        elif platform == "win32":
            # Windows...
            assert (
                pathlib.Path(filename).suffix == ".exe"
            ), f"Incorrect file suffix for {filename=} {pathlib.Path(filename).suffix=}. Please provide a .exe file"
        else:
            assert 0, f"unknown filetype {pathlib.Path(filename).suffix}"

        assert os.path.exists(filename)

    def from_numpy(self, action, order_ij=False):
        """
        Handles dict to tuple actions

        Args:
            action: The action to be converted.
            order_ij (bool): Order flag.

        Returns:
            list: The converted action.
        """
        result = []

        for agent_idx in range(self.num_envs):
            env_action = {}
            for j, k in enumerate(self.action_spaces[agent_idx].keys()):
                if order_ij is True:
                    v = action[agent_idx][j]
                else:
                    v = action[j][agent_idx]

                if isinstance(v, np.ndarray):
                    env_action[k] = v.tolist()
                else:
                    env_action[k] = int(v)  # cannot serialize int32

            result.append(env_action)
        return result

    def step(self, action, order_ij=False):
        """
        Perform one step in the environment.

        Args:
            action: Action to be taken.
            order_ij (bool): Order flag.

        Returns:
            tuple: Tuple containing observation, reward, done flag, termination flag, and info.
        """
        self.step_send(action, order_ij=order_ij)
        return self.step_recv()

    def step_send(self, action, order_ij=False):
        """
        Send the action to the Godot environment.

        Args:
            action: Action to be sent.
            order_ij (bool): Order flag.
        """
        action = self.action_space_processor.to_original_dist(action)

        message = {
            "type": "action",
            "action": self.from_numpy(action, order_ij=order_ij),
        }
        self._send_as_json(message)

    def step_recv(self):
        """
        Receive the step response from the Godot environment.

        Returns:
            tuple: Tuple containing observation, reward, done flag, termination flag, and info.
        """
        response = self._get_json_dict()
        response["obs"] = self._process_obs(response["obs"])

        return (
            response["obs"],
            response["reward"],
            np.array(response["done"]).tolist(),
            np.array(response["done"]).tolist(),  # TODO update API to term, trunc
            [{}] * len(response["done"]),
        )

    def _process_obs(self, response_obs: dict):
        """
        Process observation data.

        Args:
            response_obs (dict): The response observation to be processed.

        Returns:
            dict: The processed observation data.
        """
        for k in response_obs[0].keys():
            if "2d" in k:
                for sub in response_obs:
                    sub[k] = self._decode_2d_obs_from_string(sub[k], self.observation_space[k].shape)

        return response_obs

    def reset(self, seed=None):
        """
        Reset the Godot environment.

        Returns:
            dict: The initial observation data.
        """
        message = {
            "type": "reset",
        }
        self._send_as_json(message)
        response = self._get_json_dict()
        response["obs"] = self._process_obs(response["obs"])
        assert response["type"] == "reset"
        obs = response["obs"]
        return obs, [{}] * self.num_envs

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

    @property
    def action_space(self):
        """
        Returns a single action space.
        """
        return self.action_space_processor.action_space

    def _close(self):
        print("exit was not clean, using atexit to close env")
        self.close()

    def _launch_env(self, env_path, port, show_window, framerate, seed, action_repeat, speedup):
        # --fixed-fps {framerate}
        path = convert_macos_path(env_path) if platform == "darwin" else env_path

        launch_cmd = f"{path} --port={port} --env_seed={seed}"

        if show_window is False:
            launch_cmd += " --disable-render-loop --headless"
        if framerate is not None:
            launch_cmd += f" --fixed-fps {framerate}"
        if action_repeat is not None:
            launch_cmd += f" --action_repeat={action_repeat}"
        if speedup is not None:
            launch_cmd += f" --speedup={speedup}"

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
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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

        # Number of AIController instances in a single Godot env/process
        self.num_envs = json_dict["n_agents"]

        # actions can be "single" for a single action head
        # or "multi" for several outputeads

        print("action space", json_dict["action_space"])
        # Compatibility with previous versions of Godot plugin:
        # A single action space will be received as a dict in previous versions,
        # A list of dicts will be received from the newer version, defining the action_space for each agent (AIController)
        if isinstance(json_dict["action_space"], dict):
            json_dict["action_space"] = [json_dict["action_space"]] * self.num_envs

        for agent_action_space in json_dict["action_space"]:
            tmp_action_spaces = OrderedDict()
            for k, v in agent_action_space.items():
                if v["action_type"] == "discrete":
                    tmp_action_spaces[k] = spaces.Discrete(v["size"])
                elif v["action_type"] == "continuous":
                    tmp_action_spaces[k] = spaces.Box(low=-1.0, high=1.0, shape=(v["size"],))
                else:
                    print(f"action space {v['action_type']} is not supported")
                    assert 0, f"action space {v['action_type']} is not supported"
            self.action_spaces.append(spaces.Dict(tmp_action_spaces))

        print("observation space", json_dict["observation_space"])
        # Compatibility with older versions of Godot plugin:
        # A single observation space will be received as a dict in previous versions,
        # A list of dicts will be received from newer version, defining the observation_space for each agent (AIController)
        if isinstance(json_dict["observation_space"], dict):
            json_dict["observation_space"] = [json_dict["observation_space"]] * self.num_envs

        for agent_obs_space in json_dict["observation_space"]:
            observation_spaces = {}
            for k, v in agent_obs_space.items():
                if v["space"] == "box":
                    if "2d" in k:
                        observation_spaces[k] = spaces.Box(
                            low=0,
                            high=255,
                            shape=v["size"],
                            dtype=np.uint8,
                        )
                    else:
                        observation_spaces[k] = spaces.Box(
                            low=-1.0,
                            high=1.0,
                            shape=v["size"],
                            dtype=np.float32,
                        )
                elif v["space"] == "discrete":
                    observation_spaces[k] = spaces.Discrete(v["size"])
                else:
                    print(f"observation space {v['space']} is not supported")
                    assert 0, f"observation space {v['space']} is not supported"
            self.observation_spaces.append(spaces.Dict(observation_spaces))

        # Gets policy names defined in AIControllers in Godot. If an older version of the plugin is used and no policy
        # names are sent, "shared_policy" will be set for compatibility.
        self.agent_policy_names = json_dict.get("agent_policy_names", ["shared_policy"] * self.num_envs)

    @staticmethod
    def _decode_2d_obs_from_string(
        hex_string,
        shape,
    ):
        return np.frombuffer(bytes.fromhex(hex_string), dtype=np.uint8).reshape(shape)

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
        except BlockingIOError:
            pass
        self.connection.setblocking(True)

    def _get_data(self):
        try:
            # Receive the size (in bytes) of the remaining data to receive
            string_size_bytes: bytearray = bytearray()
            received_length: int = 0

            # The first 4 bytes contain the length of the remaining data
            length: int = 4

            while received_length < length:
                data = self.connection.recv(length - received_length)
                received_length += len(data)
                string_size_bytes.extend(data)

            length = int.from_bytes(string_size_bytes, "little")

            # Receive the rest of the data
            string_bytes: bytearray = bytearray()
            received_length = 0

            while received_length < length:
                data = self.connection.recv(length - received_length)
                received_length += len(data)
                string_bytes.extend(data)

            string: str = string_bytes.decode()

            return string
        except socket.timeout as e:
            print("env timed out", e)
        return None

    def _send_string(self, string):
        message = len(string).to_bytes(4, "little") + bytes(string.encode())
        self.connection.sendall(message)

    def _send_action(self, action):
        self._send_string(action)


def interactive():
    env = GodotEnv()
    print("observation space", env.observation_space)
    print("action space", env.action_space)

    obs = env.reset()
    for i in range(1000):
        action = [env.action_space.sample() for _ in range(env.num_envs)]
        action = list(zip(*action))

        obs, reward, term, trunc, info = env.step(action)
    env.close()


if __name__ == "__main__":
    interactive()
