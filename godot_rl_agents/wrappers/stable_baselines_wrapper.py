from stable_baselines3 import PPO
from stable_baselines3.common.vec_env.base_vec_env import VecEnv

from godot_rl_agents.core.godot_env import GodotEnv


class StableBaselinesGodotEnv(VecEnv):
    def __init__(self, port=10008, seed=0):
        self.env = GodotEnv(port=port, seed=seed)

    def step(self, action):
        return self.env.step(action)

    def reset(self):
        return self.env.reset()

    def close(self):
        self.env.close()

    def env_is_wrapped(self):
        return [False] * self.env.num_envs

    @property
    def observation_space(self):
        return self.env.observation_space

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def num_envs(self):
        return self.env.num_envs

    def env_method(self):
        raise NotImplementedError()

    def get_attr(self):
        raise NotImplementedError()

    def seed(self):
        raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def step_async(self):
        raise NotImplementedError()

    def step_wait(self):
        raise NotImplementedError()


def stable_baselines_training(args):
    print(
        "Stable-baselines3 is currently unsupported due to issue: https://github.com/DLR-RM/stable-baselines3/issues/731"
    )
    raise NotImplementedError


if __name__ == "__main__":

    env = StableBaselinesGodotEnv()

    model = PPO(
        "MlpPolicy",
        env,
        ent_coef=0.0001,
        verbose=2,
        n_steps=32,
        tensorboard_log="logs/log",
    )
    model.learn(20000)
    print("closing env")
    env.close()
