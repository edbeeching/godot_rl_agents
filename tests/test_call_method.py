import time

from godot_rl.core.godot_env import GodotEnv

if __name__ == "__main__":
    show_window = False
    N_STEPS = 100
    env_path = "envs/example_envs/builds/BallChase/ball_chase.x86_64"

    results = {}

    env = GodotEnv()

    obs = env.reset()
    obs, reward, done, info = env.step([env.action_space.sample() for _ in range(env.num_envs)])

    returns = env.call("remote_callable")

    print(returns)
