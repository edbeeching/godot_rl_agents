import numpy as np
from gymnasium import spaces

from godot_rl.core.godot_env import GodotEnv


def _env_with_obs_space(obs_space: spaces.Dict) -> GodotEnv:
    # Only _process_obs is exercised, so no Godot process or socket is needed.
    env = GodotEnv.__new__(GodotEnv)
    env.observation_spaces = [obs_space]
    env.observation_space = obs_space
    return env


def test_float_obs_hex_string_is_decoded_exactly():
    values = np.random.default_rng(0).uniform(-1.0, 1.0, size=(3, 69)).astype(np.float32)
    env = _env_with_obs_space(spaces.Dict({"obs": spaces.Box(low=-1.0, high=1.0, shape=(69,))}))

    response_obs = [{"obs": row.astype("<f4").tobytes().hex()} for row in values]
    processed = env._process_obs(response_obs)

    assert len(processed) == 3
    for row, sub in zip(values, processed):
        assert sub["obs"].dtype == np.float32
        assert sub["obs"].shape == (69,)
        np.testing.assert_array_equal(sub["obs"], row)


def test_list_obs_is_left_untouched():
    env = _env_with_obs_space(spaces.Dict({"obs": spaces.Box(low=-1.0, high=1.0, shape=(3,))}))
    response_obs = [{"obs": [0.1, 0.2, 0.3]}]

    assert env._process_obs(response_obs) == [{"obs": [0.1, 0.2, 0.3]}]


def test_mixed_keys_decode_independently():
    image = np.arange(12, dtype=np.uint8).reshape(2, 2, 3)
    vector = np.array([0.5, -0.25], dtype=np.float32)
    env = _env_with_obs_space(
        spaces.Dict(
            {
                "camera_2d": spaces.Box(low=0, high=255, shape=(2, 2, 3), dtype=np.uint8),
                "obs": spaces.Box(low=-1.0, high=1.0, shape=(2,)),
                "plain": spaces.Box(low=-1.0, high=1.0, shape=(1,)),
            }
        )
    )
    response_obs = [{"camera_2d": image.tobytes().hex(), "obs": vector.astype("<f4").tobytes().hex(), "plain": [0.75]}]
    sub = env._process_obs(response_obs)[0]

    np.testing.assert_array_equal(sub["camera_2d"], image)
    np.testing.assert_array_equal(sub["obs"], vector)
    assert sub["plain"] == [0.75]
