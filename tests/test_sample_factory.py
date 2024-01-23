import pytest

from godot_rl.core.utils import cant_import


@pytest.mark.skipif(cant_import("sample_factory"), reason="sample_factory is not available")
def test_sample_factory_training():
    from examples.sample_factory_example import get_args
    from godot_rl.wrappers.sample_factory_wrapper import sample_factory_training

    args, extras = get_args()
    args.env_path = "examples/godot_rl_JumperHard/bin/JumperHard.x86_64"
    extras = []
    extras.append("--env=gdrl")
    extras.append("--train_for_env_steps=1000")
    extras.append("--device=cpu")

    sample_factory_training(args, extras)
