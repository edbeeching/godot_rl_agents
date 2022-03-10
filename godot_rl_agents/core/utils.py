from ray import tune
from godot_rl_agents.wrappers.ray_wrapper import RayVectorGodotEnv
from godot_rl_agents.core.godot_env import GodotEnv


def register_env():
    tune.register_env(
        "godot",
        lambda c: RayVectorGodotEnv(
            env_path=c["env_path"],
            config=c,
            port=c.worker_index + GodotEnv.DEFAULT_PORT + 10,
            show_window=c["show_window"],
            framerate=c["framerate"],
            seed=c.worker_index + c["seed"],
            action_repeat=c["framerate"],
        ),
    )
