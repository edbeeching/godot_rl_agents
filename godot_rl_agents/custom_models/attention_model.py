import logging

import gym
import numpy as np
from gym.spaces import Box, Discrete, MultiDiscrete
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork as TorchFCNet
from ray.rllib.models.torch.misc import (AppendBiasLayer, SlimFC,
                                         normc_initializer)
from ray.rllib.models.torch.modules import (GRUGate,
                                            RelativeMultiHeadAttention,
                                            SkipConnection)
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.policy.sample_batch import SampleBatch
from ray.rllib.policy.view_requirement import ViewRequirement
from ray.rllib.utils.annotations import override
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.typing import Dict, List, ModelConfigDict, TensorType

torch, nn = try_import_torch()
logger = logging.getLogger(__name__)


# defines the attention model used in the bullet hell environment
# first a feed forward to test that observations are being handled correctly


class MyAttentionModel(TorchModelV2, nn.Module):
    """Generic fully connected network."""

    def __init__(
        self,
        obs_space: gym.spaces.Space,
        action_space: gym.spaces.Space,
        num_outputs: int,
        model_config: ModelConfigDict,
        name: str,
    ):

        TorchModelV2.__init__(self, obs_space, action_space, num_outputs, model_config, name)

        nn.Module.__init__(self)
        # simple baseline, fc all inputs and sum then value and policy head

        # if isinstance(action_space, Discrete):
        #     self.action_dim = action_space.n
        # elif isinstance(action_space, MultiDiscrete):
        #     self.action_dim = np.product(action_space.nvec)
        # elif action_space.shape is not None:
        #     self.action_dim = int(np.product(action_space.shape))
        # else:
        #     self.action_dim = int(len(action_space))
        # print("action space", action_space, self.action_dim, num_outputs)
        prev_layer_size = 3  # int(np.product(obs_space.shape))
        # obs_space["obs"]["max_length"] = 1
        self.model = TorchFCNet(obs_space, action_space, num_outputs, model_config, name)
        print(self.model)

        print(obs_space, prev_layer_size, self.num_outputs)
        self._logits_branch = SlimFC(
            in_size=prev_layer_size,
            out_size=self.num_outputs,
            activation_fn=None,
            initializer=torch.nn.init.xavier_uniform_,
        )
        self._value_branch = SlimFC(
            in_size=prev_layer_size,
            out_size=1,
            activation_fn=None,
            initializer=torch.nn.init.xavier_uniform_,
        )
        # torch.set_printoptions(profile="full")

    @override(TorchModelV2)
    def forward(
        self,
        input_dict: Dict[str, TensorType],
        state: List[TensorType],
        seq_lens: TensorType,
    ) -> (TensorType, List[TensorType]):

        observations = input_dict[SampleBatch.OBS]
        # print("unbatch", input_dict["obs"]["obs"].unbatch_all()[0])
        # print(input_dict["obs"])
        self._debug_batch_size = len(input_dict["obs"]["obs"].unbatch_all())
        if not input_dict["obs"]["obs"].unbatch_all()[0]:
            return (
                np.zeros((self._debug_batch_size, 4)),
                [],
            )

        results = []
        for obs in input_dict["obs"]["obs"].unbatch_all():
            batch = torch.cat(obs)
            out = self.model({"obs": batch})
            print(out.size())

        return np.zeros((self._debug_batch_size, 4)), state

    @override(TorchModelV2)
    def value_function(self) -> TensorType:
        return torch.zeros(self._debug_batch_size)
