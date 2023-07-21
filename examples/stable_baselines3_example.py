import argparse
import os
import pathlib

from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv
from godot_rl.wrappers.onnx.stable_baselines_export import export_ppo_model_as_onnx
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor

# To download the env source and binary:
# 1.  gdrl.env_from_hub -r edbeeching/godot_rl_BallChase
# 2.  chmod +x examples/godot_rl_BallChase/bin/BallChase.x86_64


parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument(
    "--env_path",
    default=None,
    type=str,
    help="The Godot binary to use, do not include for in editor training",
)
parser.add_argument(
    "--experiment_dir",
    default="logs/sb3",
    type=str,
    help="The name of the experiment directory, in which the tensorboard logs are getting stored",
)
parser.add_argument(
    "--experiment_name",
    default="Experiment",
    type=str,
    help="The name of the experiment, which will be displayed in tensorboard",
)
parser.add_argument(
    "--resume_model_path",
    default=None,
    type=str,
    help="The path to a model file previously saved using --save_model_path or a checkpoint saved using "
         "--save_checkpoints_frequency. Use this to resume training from a saved model.",
)
parser.add_argument(
    "--save_model_path",
    default=None,
    type=str,
    help="The path to use for saving the trained sb3 model after training is complete. Saved model can be used later "
         "to resume training. Extension will be set to .zip",
)
parser.add_argument(
    "--onnx_export_path",
    default=None,
    type=str,
    help="The Godot binary to use, do not include for in editor training",
)
parser.add_argument(
    "--timesteps",
    default=1_000_000,
    type=int,
    help="The number of environment steps to train for, default is 1_000_000. If resuming from a saved model, "
         "it will continue training for this amount of steps from the saved state without counting previously trained "
         "steps",
)
parser.add_argument("--speedup", default=1, type=int, help="Whether to speed up the physics in the env")
parser.add_argument("--n_parallel", default=1, type=int, help="How many instances of the environment executable to "
                                                              "launch - requires --env_path to be set if > 1.")
args, extras = parser.parse_known_args()

env = StableBaselinesGodotEnv(env_path=args.env_path, show_window=True, n_parallel=args.n_parallel, speedup=args.speedup)
env = VecMonitor(env)

if args.resume_model_path is None:
    model = PPO("MultiInputPolicy", env, ent_coef=0.0001, verbose=2, n_steps=32, tensorboard_log=args.experiment_dir)
else:
    path_zip = pathlib.Path(args.resume_model_path)
    print("Loading model: " + os.path.abspath(path_zip))
    model = PPO.load(path_zip, env=env)

model.learn(args.timesteps, tb_log_name=args.experiment_name)

print("closing env")
env.close()

# Enforce the extension of onnx and zip when saving model to avoid potential conflicts in case of same name
# and extension used for both
if args.onnx_export_path is not None:
    path_onnx = pathlib.Path(args.onnx_export_path).with_suffix(".onnx")
    print("Exporting onnx to: " + os.path.abspath(path_onnx))
    export_ppo_model_as_onnx(model, str(path_onnx))

if args.save_model_path is not None:
    path_zip = pathlib.Path(args.save_model_path).with_suffix(".zip")
    print("Saving model to: " + os.path.abspath(path_zip))
    model.save(path_zip)
