import numpy as np
import argparse
import pathlib
import ray
from ray import tune
from ray.rllib.utils.annotations import override
from ray.rllib.utils.typing import MultiAgentDict, PolicyID, AgentID
from ray.rllib.models import ModelCatalog

from ray.rllib.agents import impala

from ray.tune.logger import pretty_print
import ray.rllib.agents.ppo as ppo
from godot_rl_agents.wrappers.ray_wrappers import RayVectorGodotEnv
import yaml
from godot_rl_agents.core.utils import register_env
import ray.rllib.agents.ppo as ppo
import numpy as np
import gym
from gym.spaces import Discrete, MultiDiscrete
from typing import Dict, List, Union

from ray.rllib.models.modelv2 import ModelV2
from ray.rllib.models.torch.misc import SlimFC
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.policy.rnn_sequencing import add_time_dimension
from ray.rllib.policy.sample_batch import SampleBatch
from ray.rllib.policy.view_requirement import ViewRequirement
from ray.rllib.utils.annotations import override, DeveloperAPI
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.typing import ModelConfigDict, TensorType
from ray.rllib.models.torch.recurrent_net import RecurrentNetwork as TorchRNN
from ray.rllib.models.preprocessors import get_preprocessor
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork


def get_args(parser_creator=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--env_path",
        # default="envs/example_envs/builds/JumperHard/jumper_hard.x86_64",
        default=None,
        type=str,
        help="The Godot binary to use, do no include for in editor training",
    )

    parser.add_argument(
        "-f",
        "--config_file",
        default="ppo_test.yaml",
        type=str,
        help="The yaml config file used to specify parameters for training",
    )

    parser.add_argument(
        "-c",
        "--restore",
        default=None,
        type=str,
        help="the location of a checkpoint to restore from",
    )
    parser.add_argument(
        "-e",
        "--eval",
        default=False,
        action="store_true",
        help="whether to eval the model",
    )

    return parser.parse_args()


import logging
import numpy as np
import gym

from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.models.torch.misc import (
    SlimFC,
    AppendBiasLayer,
    normc_initializer,
)
from ray.rllib.utils.annotations import override
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.typing import Dict, TensorType, List, ModelConfigDict

torch, nn = try_import_torch()
logger = logging.getLogger(__name__)

from godot_rl_agents.custom_models.attention_model import (
    MyAttentionModel,
)


class MyTorchRNNModel(TorchRNN, nn.Module):
    def __init__(
        self,
        obs_space,
        action_space,
        num_outputs,
        model_config,
        name,
        fc_size=64,
        lstm_state_size=256,
    ):
        nn.Module.__init__(self)
        super().__init__(
            obs_space, action_space, num_outputs, model_config, name
        )

        self.obs_size = get_preprocessor(obs_space)(obs_space).size
        self.fc_size = fc_size
        self.lstm_state_size = model_config["lstm_cell_size"]

        # Build the Module from fc + LSTM + 2xfc (action + value outs).
        self.fc = FullyConnectedNetwork(
            action_space=action_space,
            obs_space=obs_space,
            num_outputs=self.lstm_state_size,
            model_config=model_config,
            name="fc",
        )
        # self.lstm = nn.LSTM(
        #     self.fc_size, self.lstm_state_size, batch_first=True
        # )
        self.gru = nn.GRU(self.fc_size, self.lstm_state_size, batch_first=True)
        self.action_branch = nn.Linear(self.lstm_state_size, num_outputs)
        self.value_branch = nn.Linear(self.lstm_state_size, 1)
        # Holds the current "base" output (before logits layer).
        self._features = None

    @override(ModelV2)
    def get_initial_state(self):
        # TODO: (sven): Get rid of `get_initial_state` once Trajectory
        #  View API is supported across all of RLlib.
        # Place hidden states on same device as model.
        # h = [
        #     self.fc1.weight.new(1, self.lstm_state_size).zero_().squeeze(0),
        #     self.fc1.weight.new(1, self.lstm_state_size).zero_().squeeze(0),
        # ]

        h = (
            self.gru.weight_ih_l0.new(1, self.lstm_state_size)
            .zero_()
            .squeeze(0)
        )
        return [h]

    @override(ModelV2)
    def value_function(self):
        assert self._features is not None, "must call forward() first"
        return torch.reshape(self.value_branch(self._features), [-1])

    @override(ModelV2)
    def forward(
        self,
        input_dict: Dict[str, TensorType],
        state: List[TensorType],
        seq_lens: TensorType,
    ) -> (TensorType, List[TensorType]):
        """Adds time dimension to batch before sending inputs to forward_rnn().

        You should implement forward_rnn() in your subclass."""
        flat_inputs = input_dict["obs_flat"].float()
        if isinstance(seq_lens, np.ndarray):
            seq_lens = torch.Tensor(seq_lens).int()
        max_seq_len = flat_inputs.shape[0] // seq_lens.shape[0]
        self.time_major = self.model_config.get("_time_major", False)
        inputs = add_time_dimension(
            flat_inputs,
            max_seq_len=max_seq_len,
            framework="torch",
            time_major=self.time_major,
        )
        output, new_state = self.forward_rnn(inputs, state, seq_lens)
        output = torch.reshape(output, [-1, self.num_outputs])
        return output, new_state

    @override(TorchRNN)
    def forward_rnn(self, inputs, state, seq_lens):
        """Feeds `inputs` (B x T x ..) through the Gru Unit.
        Returns the resulting outputs as a sequence (B x T x ...).
        Values are stored in self._cur_value in simple (B) shape (where B
        contains both the B and T dims!).
        Returns:
            NN Outputs (B x T x ...) as sequence.
            The state batches as a List of two items (c- and h-states).
        """
        print("forward rnn")
        x, state = nn.functional.relu(self.fc(inputs, state, seq_lens))
        print("state", state[0].size())
        self._features, h = self.gru(x, torch.unsqueeze(state[0], 0))
        action_out = self.action_branch(self._features)
        return action_out, [torch.squeeze(h, 0)]


def main():
    ray.init()
    args = get_args()
    with open(args.config_file) as f:
        exp = yaml.safe_load(f)
    register_env()
    ModelCatalog.register_custom_model("my_torch_model", MyAttentionModel)

    exp["config"]["env_config"]["env_path"] = args.env_path
    if args.env_path is not None:
        run_name = exp["algorithm"] + "/" + pathlib.Path(args.env_path).stem
    else:
        run_name = exp["algorithm"] + "/editor"
    print("run_name", run_name)

    if args.env_path is None:
        print("SETTING WORKERS TO 1")
        exp["config"]["num_workers"] = 1

    checkpoint_freq = 10
    checkpoint_at_end = True
    if args.eval:
        checkpoint_freq = 0
        exp["config"]["env_config"]["show_window"] = True
        exp["config"]["env_config"]["framerate"] = None
        exp["config"]["lr"] = 0.0
        exp["config"]["num_sgd_iter"] = 1
        exp["config"]["num_workers"] = 1
        exp["config"]["train_batch_size"] = 8192
        exp["config"]["sgd_minibatch_size"] = 128

        exp["config"]["explore"] = False
        exp["stop"]["training_iteration"] = 999999

    exp["config"]["model"]["custom_model"] = "my_torch_model"

    print(exp)

    trainer = ppo.PPOTrainer(exp["config"], env="godot")
    print(trainer.get_policy)

    for i in range(1):
        result = trainer.train()
        print(pretty_print(result))

    trainer.cleanup()

    ray.shutdown()


if __name__ == "__main__":
    main()
