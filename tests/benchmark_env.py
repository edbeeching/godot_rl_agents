"""
script to benchmark an environments performance

we perform 10,000 actions and calculate the interactions per second in a variety of configurations
"""


import time
from godot_rl_agents.core.godot_env import GodotEnv


if __name__ == "__main__":
    show_window = False
    framerates = [
        1,
        2,
        5,
        10,
        15,
        20,
        30,
        60,
        120,
        240,
        480,
    ]  # these values are counter intuitive, lower = higher simulation speed
    ports = list(range(12008, 12008 + len(framerates)))
    N_STEPS = 100
    env_path = "envs/example_envs/builds/BallChase/ball_chase.x86_64"

    for framerate, port in zip(framerates, ports):

        env = GodotEnv(
            env_path=env_path, port=port, framerate=framerate, show_window=True
        )
        obs = env.reset()
        n_envs = env.num_envs
        action_space = env.action_space
        start = time.time()
        for i in range(N_STEPS):

            actions = [action_space.sample() for _ in range(n_envs)]
            _ = env.step(actions)

        total_steps = N_STEPS * n_envs

        ips = total_steps / (time.time() - start)

        print(
            f"Average IPS of {ips} in {total_steps} steps in {time.time() - start} seconds  at framerate of {framerate}"
        )

        env.close()
