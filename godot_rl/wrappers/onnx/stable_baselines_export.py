import torch
from stable_baselines3 import PPO


class OnnxableMultiInputPolicy(torch.nn.Module):
    def __init__(self, obs_keys, features_extractor, mlp_extractor, action_net, value_net):
        super().__init__()
        self.obs_keys = obs_keys
        self.features_extractor = features_extractor
        self.mlp_extractor = mlp_extractor
        self.action_net = action_net
        self.value_net = value_net

    def forward(self, obs, state_ins):
        obs_dict = {k: v for k, v in zip(self.obs_keys, obs)}
        # NOTE: You may have to process (normalize) observation in the correct
        #       way before using this. See `common.preprocessing.preprocess_obs`
        features = self.features_extractor(obs_dict)
        action_hidden, value_hidden = self.mlp_extractor(features)
        return self.action_net(action_hidden), state_ins


def export_ppo_model_as_onnx(ppo: PPO, onnx_model_path: str):
    ppo_policy = ppo.policy.to("cpu")
    onnxable_model = OnnxableMultiInputPolicy(
        ["obs"],
        ppo_policy.features_extractor,
        ppo_policy.mlp_extractor,
        ppo_policy.action_net,
        ppo_policy.value_net,
    )
    dummy_input = dict(ppo.observation_space.sample())
    for k, v in dummy_input.items():
        dummy_input[k] = torch.from_numpy(v).unsqueeze(0)

    dummy_input = [v for v in dummy_input.values()]
    torch.onnx.export(
        onnxable_model,
        args=(dummy_input, torch.zeros(1).float()),
        f=onnx_model_path,
        opset_version=9,
        input_names=["obs", "state_ins"],
        output_names=["output", "state_outs"],
        dynamic_axes={
            "obs": {0: "batch_size"},
            "state_ins": {0: "batch_size"},  # variable length axes
            "output": {0: "batch_size"},
            "state_outs": {0: "batch_size"},
        },
    )
    verify_onnx_export(ppo, onnx_model_path)


def verify_onnx_export(ppo: PPO, onnx_model_path: str, num_tests=10):
    import numpy as np
    import onnx
    import onnxruntime as ort

    onnx_model = onnx.load(onnx_model_path)
    onnx.checker.check_model(onnx_model)

    sb3_model = ppo.policy.to("cpu")
    ort_sess = ort.InferenceSession(onnx_model_path, providers=["CPUExecutionProvider"])

    for i in range(num_tests):
        obs = dict(ppo.observation_space.sample())

        obs2 = {}
        for k, v in obs.items():
            obs2[k] = torch.from_numpy(v).unsqueeze(0)

        with torch.no_grad():
            action_sb3, _, _ = sb3_model(obs2, deterministic=True)

        obs = [v for v in obs.values()]
        action_onnx, state_outs = ort_sess.run(None, {"obs": obs, "state_ins": np.array([0.0], dtype=np.float32)})
        assert np.allclose(action_sb3, action_onnx, atol=1e-5), "Mismatch in action output"
        assert np.allclose(state_outs, np.array([0.0]), atol=1e-5), "Mismatch in state_outs output"
