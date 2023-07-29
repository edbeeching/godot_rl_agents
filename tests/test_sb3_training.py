import pytest

from godot_rl.main import get_args
from godot_rl.core.utils import can_import

@pytest.mark.skipif(can_import("ray"), reason="rllib and sb3 are not compatable")
@pytest.mark.parametrize(
    "env_name,port",
    [
        ("BallChase", 12000),
        ("FPS", 12100),
        ("JumperHard", 12200),
        ("Racer", 12300),
        ("FlyBy", 12400),
    ],
)
@pytest.mark.parametrize("n_parallel",[1,2,4])
def test_sb3_training(env_name, port, n_parallel):
    from godot_rl.wrappers.stable_baselines_wrapper import stable_baselines_training
    args, extras = get_args()
    args.env = "gdrl"
    args.env_path = f"examples/godot_rl_{env_name}/bin/{env_name}.x86_64"
    args.experiment_name = f"test_{env_name}_{n_parallel}"
    starting_port = port + n_parallel

    stable_baselines_training(args, extras, n_steps=10, port=starting_port, n_parallel=n_parallel)
