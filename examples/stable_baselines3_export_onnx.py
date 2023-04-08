import argparse
import torch
from stable_baselines3 import PPO

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument(
    "--save_path",
    default="BallChase.zip",
    # default=None,
    type=str,
    help="Name of the saved model (assumes PPO)",
)


class OnnxableMultiInputPolicy(torch.nn.Module):
    def __init__(self, features_extractor, mlp_extractor, action_net, value_net):
        super().__init__()
        self.features_extractor = features_extractor
        self.mlp_extractor = mlp_extractor
        self.action_net = action_net
        self.value_net = value_net

    def forward(self, observation):
        # NOTE: You may have to process (normalize) observation in the correct
        #       way before using this. See `common.preprocessing.preprocess_obs`
        features = self.features_extractor(observation)
        action_hidden, value_hidden = self.mlp_extractor(features)
        return self.action_net(action_hidden), self.value_net(value_hidden)


args, extras = parser.parse_known_args()
# Example: model = PPO("MlpPolicy", "Pendulum-v1")
model = PPO.load(args.save_path, device="cpu")
onnxable_model = OnnxableMultiInputPolicy(
    model.policy.features_extractor, model.policy.mlp_extractor, model.policy.action_net, model.policy.value_net
)
dummy_input = dict(model.observation_space.sample())
for k, v in dummy_input.items():
    dummy_input[k] = torch.from_numpy(v)
torch.onnx.export(
    model.policy,
    dummy_input,
    "my_ppo_model.onnx",
    opset_version=9,
    input_names=["observation"],
)

##### Load and test with onnx

import onnx
import onnxruntime as ort
import numpy as np

onnx_path = "my_ppo_model.onnx"
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)

observation = model.observation_space.sample()
ort_sess = ort.InferenceSession(onnx_path)
action, value = ort_sess.run(None, {"input": observation})
