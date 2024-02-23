import os

import pytest

from godot_rl.core.utils import can_import


@pytest.mark.skipif(can_import("ray"), reason="rllib and sb3 are not compatable")
@pytest.mark.parametrize(
    "env_name,port",
    [
        ("BallChase", 12008),
        ("FPS", 12009),
        ("JumperHard", 12010),
        ("Racer", 12011),
        ("FlyBy", 12012),
        ("3DCarParking", 12013),
        ("AirHockey", 12014),
        ("ItemSortingCart", 12015),
        ("Ships", 12016),
        ("DownFall", 12017),
    ],
)
def test_pytorch_vs_onnx(env_name, port):
    from stable_baselines3 import PPO

    from godot_rl.wrappers.onnx.stable_baselines_export import export_ppo_model_as_onnx, verify_onnx_export
    from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv

    env_path = f"examples/godot_rl_{env_name}/bin/{env_name}.x86_64"
    env = StableBaselinesGodotEnv(env_path, port=port)

    ppo = PPO(
        "MultiInputPolicy",
        env,
        ent_coef=0.0001,
        verbose=2,
        n_steps=32,
        tensorboard_log="logs/log",
    )

    export_ppo_model_as_onnx(ppo, f"{env_name}_tmp.onnx")
    verify_onnx_export(ppo, f"{env_name}_tmp.onnx")
    os.remove(f"{env_name}_tmp.onnx")
