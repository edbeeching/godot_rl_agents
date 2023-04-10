from stable_baselines3 import PPO
import pytest
from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv
from godot_rl.wrappers.onnx.stable_baselines_export import export_ppo_model_as_onnx, verify_onnx_export


@pytest.mark.parametrize(
    "env_name,port",
    [
        ("BallChase", 12008),
        ("FPS", 12009),
        ("JumperHard", 12010),
        ("Racer", 12011),
        ("FlyBy", 12012),
    ],
)
def test_pytorch_vs_onnx(env_name, port):
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
    export_ppo_model_as_onnx(ppo, f"{env_name}.onnx")
    verify_onnx_export(ppo, f"{env_name}.onnx")

    # onnx_path = "ball_chase.onnx"
    # model = PPO.load("BallChase.zip", device="cpu")
    # # Load the ONNX model and create an inference session
    # onnx_model = onnx.load(onnx_path)
    # onnx.checker.check_model(onnx_model)
    # ort_sess = ort.InferenceSession(onnx_path)

    # # Perform tests
    # for _ in range(num_tests):
    #     # Sample an observation
    #     obs = dict(model.observation_space.sample())
    #     obs_tensor = {k: torch.from_numpy(v).unsqueeze(0) for k, v in obs.items()}
    #     obs_array = [v for v in obs.values()]

    #     # Get the output of the PyTorch model
    #     with torch.no_grad():
    #         actions, values, log_prob = model.policy(obs_tensor, deterministic=True)
    #         actions = actions.detach().numpy()
    #         values = values.detach().numpy()

    #     # Get the output of the ONNX model
    #     onnx_act, onnx_value = ort_sess.run(None, {"observation": obs_array})

    #     # Compare the outputs
    #     assert np.allclose(actions, onnx_act, atol=1e-5), "Mismatch in action output"
    #     assert np.allclose(values, onnx_value, atol=1e-5), "Mismatch in value output"
