import numpy as np

from godot_rl_agents.core.godot_env import GodotEnv


if __name__ == "__main__":

    env = GodotEnv(env_path=None, port=10008)
    print("observation space", env.observation_space)
    print("action space", env.action_space)
    print("RESET ENV 1")
    obs = env.reset()
    for i in range(10):
        print("sending action")
        _ = env.step(np.random.uniform(-1.0, 1.0, size=(env.num_envs, 2)))
    print("RESET ENV 2")
    obs = env.reset()
    obs = env.reset()
    print("RESET ENV 2 DONE")
    for i in range(10):
        print("sending action")
        _ = env.step(np.random.uniform(-1.0, 1.0, size=(env.num_envs, 2)))
    print("RESET ENV 2")
    obs = env.reset()
    print("RESET ENV 2 DONE")
    for i in range(10):
        print("sending action")
        _ = env.step(np.random.uniform(-1.0, 1.0, size=(env.num_envs, 2)))

    env.close()
