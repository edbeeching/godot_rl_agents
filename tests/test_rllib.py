import pytest

from godot_rl.core.utils import cant_import


@pytest.mark.skipif(cant_import("ray"), reason="ray[rllib] is not available")
def test_rllib_training():
    from godot_rl.main import get_args
    from godot_rl.wrappers.ray_wrapper import rllib_training

    args, extras = get_args()
    args.config_file = "tests/fixtures/test_rllib.yaml"
    args.env_path = "examples/godot_rl_JumperHard/bin/JumperHard.x86_64"

    rllib_training(args, extras)
