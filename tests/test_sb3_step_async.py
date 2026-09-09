import gymnasium as gym
import numpy as np
import pytest

from godot_rl.core.utils import can_import

# The sb3 wrapper imports stable_baselines3, which the rllib CI job uninstalls, so it is
# imported inside the helper below and the whole module is skipped when ray is present.
pytestmark = pytest.mark.skipif(can_import("ray"), reason="rllib and sb3 are not compatable")


class FakeGodotEnv:
    """Stand in for GodotEnv that records the order of the send and receive calls."""

    def __init__(self, index, num_envs, calls, terminate=False):
        self.index = index
        self.num_envs = num_envs
        self.calls = calls
        self.sent_actions = None
        self.terminate = terminate
        self.observation_space = gym.spaces.Dict({"obs": gym.spaces.Box(-np.inf, np.inf, shape=(2,))})
        self.action_space = gym.spaces.Box(-1.0, 1.0, shape=(1,))

    def step_send(self, action):
        self.calls.append(("send", self.index))
        self.sent_actions = action

    def step_recv(self):
        self.calls.append(("recv", self.index))
        obs = [{"obs": np.full(2, float(self.index))} for _ in range(self.num_envs)]
        reward = [float(self.index)] * self.num_envs
        term = [self.terminate] * self.num_envs
        trunc = [False] * self.num_envs
        info = [{} for _ in range(self.num_envs)]
        return obs, reward, term, trunc, info


def make_env(n_parallel=3, num_envs=2):
    from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv

    # Bypass __init__ so no Godot game is launched
    env = object.__new__(StableBaselinesGodotEnv)
    calls = []
    env.envs = [FakeGodotEnv(i, num_envs, calls) for i in range(n_parallel)]
    env.n_parallel = n_parallel
    return env, calls


def test_step_async_only_sends():
    env, calls = make_env()
    env.step_async(np.zeros((6, 1)))
    assert calls == [("send", 0), ("send", 1), ("send", 2)]


def test_step_wait_collects_after_step_async():
    env, calls = make_env()
    env.step_async(np.zeros((6, 1)))
    env.step_wait()
    assert [kind for kind, _ in calls] == ["send"] * 3 + ["recv"] * 3


def test_step_still_sends_everything_before_the_first_receive():
    env, calls = make_env()
    env.step(np.zeros((6, 1)))
    assert [kind for kind, _ in calls] == ["send"] * 3 + ["recv"] * 3


def test_actions_are_split_across_environments():
    env, _ = make_env(n_parallel=3, num_envs=2)
    env.step_async(np.arange(6).reshape(6, 1))
    assert env.envs[0].sent_actions.tolist() == [[0], [1]]
    assert env.envs[1].sent_actions.tolist() == [[2], [3]]
    assert env.envs[2].sent_actions.tolist() == [[4], [5]]


def test_results_keep_the_environment_order():
    env, _ = make_env(n_parallel=3, num_envs=2)
    obs, rewards, dones, infos = env.step(np.zeros((6, 1)))
    assert rewards.tolist() == [0.0, 0.0, 1.0, 1.0, 2.0, 2.0]
    assert obs["obs"].shape == (6, 2)
    assert dones.tolist() == [False] * 6
    assert len(infos) == 6


def test_step_and_the_async_pair_agree():
    env_a, _ = make_env()
    env_b, _ = make_env()
    actions = np.arange(6).reshape(6, 1)

    obs_a, rewards_a, dones_a, _ = env_a.step(actions)
    env_b.step_async(actions)
    obs_b, rewards_b, dones_b, _ = env_b.step_wait()

    assert np.array_equal(obs_a["obs"], obs_b["obs"])
    assert np.array_equal(rewards_a, rewards_b)
    assert np.array_equal(dones_a, dones_b)


def test_the_single_obs_subclass_is_still_applied_through_the_async_pair():
    # SBGSingleObsEnv only overrode step(), which used to sit on the async path because
    # step_async called self.step(). sb3 drives a vec env through step_async/step_wait, so
    # the subclass has to sit on that pair or its projection is silently skipped.
    from stable_baselines3.common.vec_env.vec_monitor import VecMonitor

    from godot_rl.wrappers.sbg_single_obs_wrapper import SBGSingleObsEnv

    calls = []
    env = object.__new__(SBGSingleObsEnv)
    env.obs_key = "obs"
    env.envs = [FakeGodotEnv(i, 2, calls, terminate=True) for i in range(2)]
    env.n_parallel = 2

    obs, _, dones, infos = VecMonitor(env).step(np.zeros((4, 1)))

    # The observation must match observation_space, which is the Box behind obs_key
    assert isinstance(obs, np.ndarray), f"expected the projected array, got {type(obs)}"
    assert obs.shape == (4, 2)
    # Terminal obs info is needed for imitation learning
    assert all(dones)
    assert all("terminal_observation" in info for info in infos)
