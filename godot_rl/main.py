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
    error_message = str(e)

    def rllib_training(args, extras):
        print("Import error importing rllib. If you have not installed the package, try: pip install godot-rl[rllib]")
        print("Otherwise try fixing the error.", error_message)


try:
    from godot_rl.wrappers.stable_baselines_wrapper import stable_baselines_training
except ImportError as e:
    error_message = str(e)

    def stable_baselines_training(args, extras):
        print("Import error importing sb3. If you have not installed the package, try: pip install godot-rl[sb3]")
        print("Otherwise try fixing the error.", error_message)


try:
    from godot_rl.wrappers.sample_factory_wrapper import sample_factory_enjoy, sample_factory_training
except ImportError as e:
    error_message = str(e)

    def sample_factory_training(args, extras):
        print(
            "Import error importing sample-factory If you have not installed the package, try: pip install godot-rl[sf]"
        )
        print("Otherwise try fixing the error.", error_message)


def get_args():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--trainer", default="sb3", choices=["sb3", "sf", "rllib"], type=str, help="framework to use (rllib, sf, sb3)"
    )
    parser.add_argument("--env_path", default=None, type=str, help="Godot binary to use")
    parser.add_argument(
        "--config_file", default="ppo_test.yaml", type=str, help="The yaml config file [only for rllib]"
    )
    parser.add_argument("--restore", default=None, type=str, help="the location of a checkpoint to restore from")
    parser.add_argument("--eval", default=False, action="store_true", help="whether to eval the model")
    parser.add_argument("--speedup", default=1, type=int, help="whether to speed up the physics in the env")
    parser.add_argument("--export", default=False, action="store_true", help="wheter to export the model")
    parser.add_argument("--num_gpus", default=None, type=int, help="Number of GPUs to use [only for rllib]")
    parser.add_argument(
        "--experiment_dir",
        default=None,
        type=str,
        help="The name of the the experiment directory, in which the tensorboard logs are getting stored",
    )
    parser.add_argument(
        "--experiment_name",
        default="experiment",
        type=str,
        help="The name of the the experiment, which will be displayed in tensborboard",
    )
    parser.add_argument("--viz", default=False, action="store_true", help="Whether to visualize one process")
    parser.add_argument("--seed", default=0, type=int, help="seed of the experiment")

    args, extras = parser.parse_known_args()
    if args.experiment_dir is None:
        args.experiment_dir = f"logs/{args.trainer}"

    if args.trainer == "sf" and args.env_path is None:
        print("WARNING: the sample-factory intergration is not designed to run in interactive mode, export you game")

    return args, extras


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
