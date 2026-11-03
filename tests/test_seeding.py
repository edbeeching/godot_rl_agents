import numpy as np
import pytest

from godot_rl.core.godot_env import GodotEnv
from godot_rl.core.utils import can_import

# The sb3 wrapper imports stable_baselines3, which the rllib CI job uninstalls, so it is
# imported inside the helper below and the tests that need it are skipped when ray is present.
needs_sb3 = pytest.mark.skipif(can_import("ray"), reason="rllib and sb3 are not compatable")


def make_godot_env():
    # Bypass __init__ so no game is launched, and record what would go on the socket
    env = object.__new__(GodotEnv)
    env.num_envs = 1
    env.sent = []
    env._send_as_json = env.sent.append
    env._get_json_dict = lambda: {"type": "reset", "obs": [{"obs": [0.0]}]}
    env._process_obs = lambda obs: obs
    return env


def test_reset_without_a_seed_is_unchanged():
    env = make_godot_env()
    env.reset()
    assert env.sent == [{"type": "reset"}]


def test_reset_forwards_the_seed():
    env = make_godot_env()
    env.reset(seed=42)
    assert env.sent == [{"type": "reset", "seed": 42}]


def test_numpy_seeds_are_converted_to_int():
    # json.dumps cannot serialize numpy integers
    env = make_godot_env()
    env.reset(seed=np.int64(7))
    assert type(env.sent[0]["seed"]) is int
    assert env.sent[0]["seed"] == 7


class FakeGodotEnv:
    def __init__(self, num_envs):
        self.num_envs = num_envs
        self.reset_seed = "not reset yet"

    def reset(self, seed=None):
        self.reset_seed = seed
        return [{"obs": np.zeros(2)} for _ in range(self.num_envs)], [{}] * self.num_envs


def make_vec_env(n_parallel=3, num_envs=1):
    from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv

    env = object.__new__(StableBaselinesGodotEnv)
    env.envs = [FakeGodotEnv(num_envs) for _ in range(n_parallel)]
    env.n_parallel = n_parallel
    env._seeds = [None] * n_parallel
    return env


@needs_sb3
def test_seed_returns_one_seed_per_parallel_game():
    env = make_vec_env(3)
    assert env.seed(10) == [10, 11, 12]


@needs_sb3
def test_latched_seeds_reach_the_games_on_the_next_reset():
    env = make_vec_env(3)
    env.seed(10)
    env.reset()
    assert [e.reset_seed for e in env.envs] == [10, 11, 12]


@needs_sb3
def test_a_seed_applies_to_a_single_reset():
    env = make_vec_env(2)
    env.seed(5)
    env.reset()
    env.reset()
    assert [e.reset_seed for e in env.envs] == [None, None]


@needs_sb3
def test_reset_without_seeding_sends_no_seed():
    env = make_vec_env(2)
    env.reset()
    assert [e.reset_seed for e in env.envs] == [None, None]


@needs_sb3
def test_seed_none_clears_the_latch():
    env = make_vec_env(2)
    env.seed(5)
    assert env.seed(None) == [None, None]
    env.reset()
    assert [e.reset_seed for e in env.envs] == [None, None]
