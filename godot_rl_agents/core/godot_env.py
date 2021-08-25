import time
import subprocess
import socket
import json
import numpy as np
from gym import spaces


class GodotEnv:
    MAJOR_VERSION = 0
    MINOR_VERSION = 1

    def __init__(
        self,
        env_path=None,
        port=10008,
        show_window=False,
        seed=0,
        framerate=60,
    ):
        self.proc = None
        if env_path is not None:
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

    def step(self, action):
        message = {
            "type": "action",
            "action": action.tolist(),
        }
        self._send_as_json(message)
        response = self._get_json_dict()

        # print(np.array(response["done"]))

        return (
            np.array(response["obs"]),
            response["reward"],
            np.array(response["done"]),
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

    def _launch_env(self, env_path, port, show_window, framerate):
        # --fixed-fps {framerate}
        launch_cmd = f"{env_path} --port={port}"
        if show_window == False:
            launch_cmd += " --disable-render-loop --no-window"
        launch_cmd = launch_cmd.split(" ")
        self.proc = subprocess.Popen(
            launch_cmd,
            start_new_session=True,
        )

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
        #        connection.setblocking(False) TODO
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
            self.action_space = spaces.Box(
                low=-1.0, high=1.0, shape=(n_actions,)
            )

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
        data = self.connection.recv(4)
        if not data:
            time.sleep(0.000001)
            return self._get_data()
        length = int.from_bytes(data, "little")
        string = self.connection.recv(length).decode()
        return string

    def _send_string(self, string):
        message = len(string).to_bytes(4, "little") + bytes(string.encode())
        self.connection.sendall(message)

    def _send_action(self, action):
        self._send_string(action)
