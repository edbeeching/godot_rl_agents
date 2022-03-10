import argparse

from godot_rl_agents.wrappers.ray_wrapper import rllib_training
from godot_rl_agents.wrappers.stable_baselines_wrapper import stable_baselines_training


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument

    parser.add_argument(
        "--trainer",
        default="rllib",
        type=str,
        help="Which trainer framework to use (rllib or stable-baselines)",
    )
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


def main():
    args = get_args()
    if args.trainer == "rllib":
        training_function = rllib_training
    elif args.trainer == "stable-baselines":
        training_function = stable_baselines_training
    else:
        raise NotImplementedError

    training_function(args)


if __name__ == "__main__":
    main()
