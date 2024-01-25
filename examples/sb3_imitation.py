import argparse
import json
import os
import pathlib
from math import log

import imitation.data
import numpy as np
from imitation.algorithms.adversarial.gail import GAIL
from imitation.rewards.reward_nets import BasicRewardNet
from imitation.util.networks import RunningNorm
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor

from godot_rl.wrappers.onnx.stable_baselines_export import export_ppo_model_as_onnx
from godot_rl.wrappers.sbg_single_obs_wrapper import SBGSingleObsEnv

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument(
    "--env_path",
    default=None,
    type=str,
    help="The Godot binary to use, do not include for in editor training",
)
parser.add_argument(
    "--demo_files",
    nargs="+",
    type=str,
    help="""One or more files with recoded expert demos, with a space in between, e.g. "demo1.json", demo2.json""",
)
parser.add_argument("--seed", type=int, default=0, help="seed of the experiment")
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
    "--inference",
    default=False,
    action="store_true",
    help="Instead of training, it will run inference on a loaded model for --timesteps steps. "
    "Requires --resume_model_path to be set.",
)
parser.add_argument(
    "--viz",
    action="store_true",
    help="If set, the simulation will be displayed in a window during training. Otherwise "
    "training will run without rendering the simulation. This setting does not apply to in-editor training.",
    default=False,
)
parser.add_argument(
    "--run_eval_after_training",
    action="store_true",
    help="Evaluate policy in an env after training in a single env. Will always visualize.",
    default=False,
)
parser.add_argument("--speedup", default=1, type=int, help="Whether to speed up the physics in the env")
parser.add_argument(
    "--n_parallel",
    default=1,
    type=int,
    help="How many instances of the environment executable to " "launch - requires --env_path to be set if > 1.",
)
parser.add_argument(
    "--il_timesteps",
    default=100_000,
    type=int,
    help="How many timesteps to train for using imitation learning.",
)
parser.add_argument(
    "--rl_timesteps",
    default=0,
    type=int,
    help="[Optional] Additional timesteps to train for using RL after IL.",
)
parser.add_argument(
    "--eval_episode_count",
    default=0,
    type=int,
    help="[Optional] How many episodes to evaluate for after training.",
)


args, extras = parser.parse_known_args()


def handle_onnx_export():
    # Enforce the extension of onnx and zip when saving model to avoid potential conflicts in case of same name
    # and extension used for both
    if args.onnx_export_path is not None:
        path_onnx = pathlib.Path(args.onnx_export_path).with_suffix(".onnx")
        print("Exporting onnx to: " + os.path.abspath(path_onnx))
        export_ppo_model_as_onnx(learner, str(path_onnx), use_obs_array=True)


def handle_model_save():
    if args.save_model_path is not None:
        zip_save_path = pathlib.Path(args.save_model_path).with_suffix(".zip")
        print("Saving model to: " + os.path.abspath(zip_save_path))
        learner.save(zip_save_path)


def close_env():
    try:
        print("closing env")
        env.close()
    except Exception as e:
        print("Exception while closing env: ", e)


trajectories = []

for file_path in args.demo_files:
    with open(file_path, "r") as file:
        data = json.load(file)

    for i in range(0, len(data)):
        trajectories.append(
            imitation.data.rollout.types.Trajectory(
                obs=np.array(data[i][0]),
                acts=np.array(data[i][1]),
                infos=None,
                terminal=True,
            )
        )


env = SBGSingleObsEnv(
    env_path=args.env_path,
    show_window=args.viz,
    seed=args.seed,
    n_parallel=args.n_parallel,
    speedup=args.speedup,
    obs_key="obs",
)

env = VecMonitor(env)


policy_kwargs = dict(log_std_init=log(1.0))

learner = PPO(
    batch_size=64,
    env=env,
    policy="MlpPolicy",
    learning_rate=0.0003,
    clip_range=0.3,
    n_epochs=20,
    n_steps=64,
    ent_coef=0.0001,
    target_kl=0.025,
    policy_kwargs=policy_kwargs,
)

reward_net = BasicRewardNet(
    observation_space=env.observation_space,
    action_space=env.action_space,
    normalize_input_layer=RunningNorm,
)

gail_trainer = GAIL(
    demonstrations=trajectories,
    demo_batch_size=64,
    gen_replay_buffer_capacity=64,
    n_disc_updates_per_round=24,
    venv=env,
    gen_algo=learner,
    reward_net=reward_net,
    allow_variable_horizon=True,
)

print("Starting Imitation Learning Training using GAIL:")
gail_trainer.train(args.il_timesteps)

if args.rl_timesteps:
    print("Starting RL Training:")
    learner.learn(args.rl_timesteps, progress_bar=True)

close_env()

if args.eval_episode_count:
    print("Evaluating:")
    env = SBGSingleObsEnv(
        env_path=args.env_path,
        show_window=True,
        seed=args.seed,
        n_parallel=1,
        speedup=args.speedup,
    )
    env = VecMonitor(env)
    mean_reward, _ = evaluate_policy(learner, env, n_eval_episodes=args.eval_episode_count)
    print(f"Mean reward after evaluation: {mean_reward}")

close_env()
handle_onnx_export()
handle_model_save()
