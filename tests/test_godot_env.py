import pytest

from godot_rl.core.godot_env import GodotEnv


@pytest.mark.parametrize(
    "env_name,port,n_agents",
    [
        ("BallChase", 12008, 16),
        ("FPS", 12009, 8),
        ("JumperHard", 12010, 16),
        ("Racer", 12011, 8),
        ("FlyBy", 12012, 16),
    ],
)
def test_env_ij(env_name, port, n_agents):
    env_path = f"examples/godot_rl_{env_name}/bin/{env_name}.x86_64"
    env = GodotEnv(env_path=env_path, port=port)

    action_space = env.action_space
    n_envs = env.num_envs

    for j in range(2):
        obs, info = env.reset()
        assert len(obs) == n_envs
        for i in range(10):
            action = [action_space.sample() for _ in range(n_envs)]
            obs, reward, term, trunc, info = env.step(action, order_ij=True)

            assert len(obs) == n_envs
            assert len(reward) == n_envs
            assert len(term) == n_envs
            assert len(trunc) == n_envs
            assert len(info) == n_envs

            assert isinstance(
                reward[0], (float, int)
            ), f"The reward returned by 'step()' must be a float or int, and is {reward[0]} of type {type(reward[0])}"
            assert isinstance(term[0], bool), f"The 'done' signal {term[0]}  {type(term[0])} must be a boolean"
            assert isinstance(info[0], dict), "The 'info' returned by 'step()' must be a python dictionary"

    env.close()


@pytest.mark.parametrize(
    "env_name,port,n_agents",
    [
        ("BallChase", 13008, 16),
        ("FPS", 13009, 8),
        ("JumperHard", 13010, 16),
        ("Racer", 13011, 8),
        ("FlyBy", 13012, 16),
    ],
)
def test_env_ji(env_name, port, n_agents):
    env_path = f"examples/godot_rl_{env_name}/bin/{env_name}.x86_64"
    env = GodotEnv(env_path=env_path, port=port)

    action_space = env.action_space
    n_envs = env.num_envs
    assert n_envs == n_agents
    for j in range(2):
        obs, info = env.reset()
        assert len(obs) == n_envs
        for i in range(10):
            action = [action_space.sample() for _ in range(n_envs)]
            action = list(zip(*action))
            obs, reward, term, trunc, info = env.step(action)

            assert len(obs) == n_envs
            assert len(reward) == n_envs
            assert len(term) == n_envs
            assert len(trunc) == n_envs
            assert len(info) == n_envs

            assert isinstance(
                reward[0], (float, int)
            ), f"The reward returned by 'step()' must be a float or int, and is {reward[0]} of type {type(reward[0])}"
            assert isinstance(term[0], bool), f"The 'done' signal {term[0]}  {type(term[0])} must be a boolean"
            assert isinstance(info[0], dict), "The 'info' returned by 'step()' must be a python dictionary"

    env.close()
