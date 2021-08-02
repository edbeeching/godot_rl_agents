import time
import socket
import json
import numpy as np
from gym import spaces


class GodotEnv:
    def __init__(self, port=10008, seed=0):
        self.port = port
        self.connection = self._start_server()
        self.num_envs = 9
        self._handshake()
        self._get_env_info()

    def step(self, action):
        message = {
            "type": "action",
            "action": action.tolist(),
        }
        self._send_as_json(message)
        response = self._get_json_dict()

        return (
            np.array(response["obs"]),
            response["reward"],
            np.array(response["done"]),
            [{}] * len(response["done"]),
        )

    def reset(self):
        message = self._get_json_dict()
        obs = np.array(message["obs"])
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
            self.action_space = spaces.Box(
                low=-1.0, high=1.0, shape=(n_actions,)
            )

        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(json_dict["obs_size"],), dtype=np.float32
        )

    def _send_as_json(self, dictionary):
        message_json = json.dumps(dictionary)
        self._send_string(message_json)

    def _get_json_dict(self):
        data = self._get_data()

        return json.loads(data)

    def _get_obs(self):

        return self._get_data()

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
