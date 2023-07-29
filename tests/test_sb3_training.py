import pytest

from godot_rl.core.godot_env import GodotEnv
from godot_rl.main import get_args

try:
    from godot_rl.wrappers.stable_baselines_wrapper import stable_baselines_training
except ImportError as e:

    def stable_baselines_training(args, extras, **kwargs):
        print("Import error when trying to use sb3, this is probably not installed try pip install godot-rl[sb3]")

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
@pytest.mark.parametrize(
    "n_parallel",[
        1,2,4
    ]
    
)
def test_sb3_training(env_name, port, n_parallel):
    args, extras = get_args()
    args.env = "gdrl"
    args.env_path = f"examples/godot_rl_{env_name}/bin/{env_name}.x86_64"
    args.experiment_name = f"test_{env_name}_{n_parallel}"
    starting_port = port + n_parallel

    stable_baselines_training(args, extras, n_steps=10, port=starting_port, n_parallel=n_parallel)
