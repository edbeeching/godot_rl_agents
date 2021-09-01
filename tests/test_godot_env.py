from godot_rl_agents.core.godot_env import GodotEnv
import pytest


@pytest.mark.parametrize(
    "env_path,port",
    [
        ("envs/build/BallChase/ball_chase.x86_64", 11008),
        ("envs/build/BallChase/jumper.x86_64", 11009),
    ],
)
def test_env(env_path, port):
    env = GodotEnv(env_path=env_path)

    action_space = env.action_space
    observation_space = env.observation_space
    n_envs = env.num_envs

    obs = env.reset()
    assert len(obs) == n_envs

    obs, reward, done, info = env.step()

    assert len(obs) == n_envs
    assert len(reward) == n_envs
    assert len(done) == n_envs
    assert len(info) == n_envs

    assert isinstance(
        reward[0], (float)
    ), "The reward returned by 'step()' must be a float"
    assert isinstance(done[0], (bool)), "The 'done' signal must be a boolean"
    assert isinstance(
        info[0], (dict)
    ), "The 'info' returned by 'step()' must be a python dictionary"

    # check n-envs
    # check reset returns an obs

    env.close()
