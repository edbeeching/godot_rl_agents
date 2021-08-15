import numpy as np

from ray.rllib.env.multi_agent_env import MultiAgentEnv
from ray.rllib.utils.annotations import override
from ray.rllib.utils.typing import MultiAgentDict, PolicyID, AgentID

from godot_rl_agents.core.godot_env import GodotEnv

# --fixed-fps 500 --disable-render-loop --no-window


class RayGodotEnv(MultiAgentEnv):
    def __init__(
        self,
        env_path="envs/build/BallChase/ball_chase_20210807.x86_64",
        port=10008,
        seed=0,
        show_window=False,
        framerate=60,
        timeout_wait=60,
    ) -> None:
        super().__init__()

        self._env = GodotEnv(env_path=env_path, port=port, seed=seed)

    def step(self, action_dict):

        # convert actions dict to numpy array
        actions = []
        for k, v in action_dict.items():
            actions.append(v)
        actions = np.array(actions)

        # step & get obs, etc
        obs, reward, done, info = self._env.step(actions)
        # return as dict

        return (
            self._to_agent_dict(obs),
            self._to_agent_dict(reward),
            self._to_agent_dict(done),
            self._to_agent_dict(info),
        )

    def reset(self):
        obs = self._env.reset()
        return self._to_agent_dict(obs)

    def _to_agent_dict(self, array):
        result = {}

        for id, value in enumerate(array):
            result[f"agent_id_{id}"] = value
        return result

    @staticmethod
    def get_policy_configs_for_game(game_name, env_path):
        # create a dummy env and extract
        env = GodotEnv(env_path=env_path, port=9999, seed=0)
        obs_space = env.observation_space
        action_space = env.action_space
        policy_space = {game_name: (None, obs_space, action_space, {})}

        env.close()

        def policy_mapping_fn(agent_id):
            return game_name

        return policy_space, policy_mapping_fn


if __name__ == "__main__":
    policy_space, policy_mapping_fn = RayGodotEnv.get_policy_configs_for_game(
        "godot_ball_chase", "envs/build/BallChase/ball_chase_20210815.x86_64"
    )

    print(policy_space)
