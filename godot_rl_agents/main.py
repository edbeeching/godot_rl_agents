"""
This is the main entrypoint to the Godot RL Agents interface

Example usage is best found in the documentation: 
https://github.com/edbeeching/godot_rl_agents/blob/main/docs/EXAMPLE_ENVIRONMENTS.md

Hyperparameters and training algorithm can be defined in a .yaml file, see ppo_test.yaml as an example.


Interactive Training:
With the Godot editor open, type gdrl in the terminal to launch training and 
then press PLAY in the Godot editor. Training can be stopped with CTRL+C or
by pressing STOP in the editor.


Training with an exported executable:

gdrl --env_path path/to/exported/executable ---config_path path/to/yaml/file


"""

import argparse

try:
    from godot_rl.wrappers.ray_wrapper import rllib_training
except ImportError as e:
    def rllib_training(args, extras):
        print("Import error when trying to use rllib, this is probably not installed try pip install ray[rllib]")

try:
    from godot_rl.wrappers.stable_baselines_wrapper import \
        stable_baselines_training
except ImportError as e:
    def stable_baselines_training(args, extras):
        print(
            "Import error when trying to use sb3, this is probably not installed try pip install stable-baselines3"
        )
try:
    from godot_rl.wrappers.sample_factory_wrapper import \
        sample_factory_training, sample_factory_enjoy
except ImportError as e:

    def sample_factory_training(args, extras):
        print(
            "Import error when trying to use sample-factory, this is probably not installed try pip install sample-factory"
        )


def get_args():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--trainer",
        default="sb3",
        choices=["sb3", "sf", "rllib"],
        type=str,
        help="Which trainer framework to use (rllib or stable-baselines)",
    )
    parser.add_argument(
        "--env_path",
        # default="envs/example_envs/builds/JumperHard/jumper_hard.x86_64",
        default=None,
        type=str,
        help="The Godot binary to use, do not include for in editor training",
    )
    parser.add_argument(
        "--config_file",
        default="ppo_test.yaml",
        type=str,
        help="The yaml config file used to specify parameters for training (used for rllib)",
    )
    parser.add_argument(
        "--restore",
        default=None,
        type=str,
        help="the location of a checkpoint to restore from",
    )
    parser.add_argument(
        "--eval",
        default=False,
        action="store_true",
        help="whether to eval the model",
    )
    parser.add_argument(
        "--speedup",
        default=1,
        type=int,
        help="whether to speed up the physics in the env",
    )

    return parser.parse_known_args()


def main():
    args, extras = get_args()
    if args.trainer == "rllib":
        training_function = rllib_training
    elif args.trainer == "sb3":
        training_function = stable_baselines_training
    elif args.trainer == "sf":
        if args.eval:
            training_function = sample_factory_enjoy
        else:
            training_function = sample_factory_training
    else:
        raise NotImplementedError

    training_function(args, extras)


if __name__ == "__main__":
    main()
