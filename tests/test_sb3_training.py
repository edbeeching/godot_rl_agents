import pytest

from godot_rl.core.godot_env import GodotEnv
from godot_rl.main import get_args

try:
    from godot_rl.wrappers.stable_baselines_wrapper import stable_baselines_training
except ImportError as e:

    def stable_baselines_training(args, extras):
        print("Import error when trying to use sb3, this is probably not installed try pip install godot-rl[sb3]")


def test_sb3_training():
    args, extras = get_args()
    args.env = "gdrl"
    args.env_path = "examples/godot_rl_JumperHard/bin/JumperHard.x86_64"

    stable_baselines_training(args, extras, n_steps=10000)
