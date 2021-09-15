from ray import tune
from godot_rl_agents.wrappers.ray_wrappers import RayVectorGodotEnv


def register_env():
    tune.register_env(
        "godot",
        lambda c: RayVectorGodotEnv(
            env_path=c["env_path"],
            config=c,
            port=c.worker_index + 12011,  # TODO change to default port
            show_window=True,
            framerate=None,
        ),
    )
