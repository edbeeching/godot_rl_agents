import pytest

from godot_rl.main import get_args
from godot_rl.core.utils import cant_import


@pytest.mark.skipif(cant_import("stable_baselines3"), reason="stable_baselines3 is not available")
def test_sb3_training():
    from godot_rl.wrappers.stable_baselines_wrapper import stable_baselines_training
    args, extras = get_args()
    args.env = "gdrl"
    args.env_path = "examples/godot_rl_JumperHard/bin/JumperHard.x86_64"

    stable_baselines_training(args, extras, n_steps=10000)
