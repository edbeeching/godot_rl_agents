import numpy as np
import argparse
import ray
from ray import tune
from ray.rllib.utils.annotations import override
from ray.rllib.utils.typing import MultiAgentDict, PolicyID, AgentID


from ray.rllib.agents import impala

from ray.tune.logger import pretty_print
import ray.rllib.agents.ppo as ppo
from godot_rl_agents.wrappers.ray_wrappers import RayVectorGodotEnv
import yaml
from godot_rl_agents.core.utils import register_env


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
        default=0,
        type=int,
        help="whether to eval the model. 0 for train, 1 for eval",
    )

    return parser.parse_args()


if __name__ == "__main__":
    ray.init()
    args = get_args()
    with open(args.config_file) as f:
        exp = yaml.safe_load(f)
    register_env()
    print(exp)
    exp["config"]["env_config"]["env_path"] = args.env_path
    checkpoint_freq = 10

    if args.eval:
        checkpoint_freq = 0
        exp["config"]["env_config"]["show_window"] = True
        exp["config"]["env_config"]["framerate"] = None
        exp["config"]["lr"] = 0.0
        exp["config"]["num_sgd_iter"] = 1
        exp["config"]["num_workers"] = 1
        exp["stop"]["training_iteration"] = 999999

    results = tune.run(
        exp["algorithm"],
        config=exp["config"],
        stop=exp["stop"],
        verbose=3,
        checkpoint_freq=checkpoint_freq,
        checkpoint_at_end=True,
        restore=args.restore,
    )
    ray.shutdown()
