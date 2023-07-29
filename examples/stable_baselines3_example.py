import argparse
import os
import pathlib

from stable_baselines3.common.callbacks import CheckpointCallback
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
    help="The name of the experiment directory, in which the tensorboard logs and checkpoints (if enabled) are "
         "getting stored."
)
parser.add_argument(
    "--experiment_name",
    default="experiment",
    type=str,
    help="The name of the experiment, which will be displayed in tensorboard and "
         "for checkpoint directory and name (if enabled).",
)
parser.add_argument(
    "--resume_model_path",
    default=None,
    type=str,
    help="The path to a model file previously saved using --save_model_path or a checkpoint saved using "
         "--save_checkpoints_frequency. Use this to resume training or infer from a saved model.",
)
parser.add_argument(
    "--save_model_path",
    default=None,
    type=str,
    help="The path to use for saving the trained sb3 model after training is complete. Saved model can be used later "
         "to resume training. Extension will be set to .zip",
)
parser.add_argument(
    "--save_checkpoint_frequency",
    default=None,
    type=int,
    help=("If set, will save checkpoints every 'frequency' environment steps. "
          "Requires a unique --experiment_name or --experiment_dir for each run. "
          "Does not need --save_model_path to be set. "),
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
parser.add_argument(
    "--inference",
    default=False,
    action="store_true",
    help="Instead of training, it will run inference on a loaded model for --timesteps steps. "
         "Requires --resume_model_path to be set."
)
parser.add_argument(
    "--viz",
    action="store_true",
    help="If set, the window(s) with the Godot environment(s) will be displayed, otherwise "
         "training will run without rendering the game. Does not apply to in-editor training.",
    default=False
)
parser.add_argument("--speedup", default=1, type=int, help="Whether to speed up the physics in the env")
parser.add_argument("--n_parallel", default=1, type=int, help="How many instances of the environment executable to "
                                                              "launch - requires --env_path to be set if > 1.")
args, extras = parser.parse_known_args()

path_checkpoint = os.path.join(args.experiment_dir, args.experiment_name + "_checkpoints")
abs_path_checkpoint = os.path.abspath(path_checkpoint)

# Prevent overwriting existing checkpoints when starting a new experiment if checkpoint saving is enabled
if args.save_checkpoint_frequency is not None and os.path.isdir(path_checkpoint):
    raise RuntimeError(abs_path_checkpoint + " folder already exists. "
                                             "Use a different --experiment_dir, or --experiment_name,"
                                             "or if previous checkpoints are not needed anymore, "
                                             "remove the folder containing the checkpoints. ")

if args.inference and args.resume_model_path is None:
    raise parser.error("Using --inference requires --resume_model_path to be set.")

if args.env_path is None and args.viz:
    print("Info: Using --viz without --env_path set has no effect, in-editor training will always render.")

env = StableBaselinesGodotEnv(env_path=args.env_path, show_window=args.viz, n_parallel=args.n_parallel,
                              speedup=args.speedup)
env = VecMonitor(env)

if args.resume_model_path is None:
    model = PPO("MultiInputPolicy", env, ent_coef=0.0001, verbose=2, n_steps=32, tensorboard_log=args.experiment_dir)
else:
    path_zip = pathlib.Path(args.resume_model_path)
    print("Loading model: " + os.path.abspath(path_zip))
    model = PPO.load(path_zip, env=env, tensorboard_log=args.experiment_dir)

if args.inference:
    obs = env.reset()
    for i in range(args.timesteps):
        action, _state = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
else:
    if args.save_checkpoint_frequency is None:
        model.learn(args.timesteps, tb_log_name=args.experiment_name)
    else:
        print("Checkpoint saving enabled. Checkpoints will be saved to: " + abs_path_checkpoint)
        checkpoint_callback = CheckpointCallback(
            save_freq=(args.save_checkpoint_frequency // env.num_envs),
            save_path=path_checkpoint,
            name_prefix=args.experiment_name
        )
        model.learn(args.timesteps, callback=checkpoint_callback, tb_log_name=args.experiment_name)

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
