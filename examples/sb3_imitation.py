import argparse
import json
import os
import pathlib
from math import log

import imitation.data
import numpy as np
from imitation.algorithms import bc
from imitation.algorithms.adversarial.gail import GAIL
from imitation.rewards.reward_nets import BasicRewardNet
from imitation.util import logger as imit_logger
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
    help="""One or more files with recorded expert demos, with a space in between, e.g. --demo_files demo1.json
    demo2.json""",
)
parser.add_argument(
    "--experiment_name",
    default=None,
    type=str,
    help="The name of the experiment, which will be displayed in tensorboard, logs will be stored in logs/["
    "experiment_name], if set. You should use a unique name for every experiment for the tensorboard log to "
    "display properly.",
)
parser.add_argument("--seed", type=int, default=0, help="seed of the experiment")
parser.add_argument(
    "--save_model_path",
    default=None,
    type=str,
    help="The path to use for saving the trained sb3 model after training is complete. Extension will be set to .zip",
)
parser.add_argument(
    "--onnx_export_path",
    default=None,
    type=str,
    help="The Godot binary to use, do not include for in editor training",
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
    "--bc_epochs",
    default=0,
    type=int,
    help="[Optional] How many epochs to train for using imitation learning with BC. Policy is trained with BC "
    "before GAIL or RL.",
)
parser.add_argument(
    "--gail_timesteps",
    default=0,
    type=int,
    help="[Optional] How many timesteps to train for using imitation learning with GAIL. If --bc_timesteps are set, "
    "GAIL training is done after pre-training the policy with BC.",
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

    for traj in data:
        trajectories.append(
            imitation.data.rollout.types.Trajectory(
                obs=np.array(traj[0]),
                acts=np.array(traj[1]),
                infos=None,
                terminal=True,
            )
        )
    print(
        f"Loaded trajectories from {file_path}, found {len(data)} recorded trajectories (GDRL plugin records 1 "
        f"episode as 1 trajectory)."
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

logger = None
if args.experiment_name:
    logger = imit_logger.configure(f"logs/{args.experiment_name}", format_strs=["tensorboard", "stdout"])

# The hyperparams are set for IL tutorial env where BC > GAIL training is used. Feel free to customize for
# your usage.
learner = PPO(
    env=env,
    policy="MlpPolicy",
    batch_size=256,
    ent_coef=0.007,
    learning_rate=0.0002,
    n_steps=64,
    target_kl=0.02,
    n_epochs=5,
    policy_kwargs=policy_kwargs,
    verbose=2,
    tensorboard_log=f"logs/{args.experiment_name}",
    # seed=args.seed // Not currently supported as stable_baselines_wrapper.py seed() method is not yet implemented.
)

try:
    if args.bc_epochs > 0:
        rng = np.random.default_rng(args.seed)
        bc_trainer = bc.BC(
            observation_space=env.observation_space,
            action_space=env.action_space,
            demonstrations=trajectories,
            rng=rng,
            policy=learner.policy,
            custom_logger=logger,
        )
        print("Starting Imitation Learning Training using BC:")
        bc_trainer.train(n_epochs=args.bc_epochs)

    if args.gail_timesteps > 0:
        print("Starting Imitation Learning Training using GAIL:")
        reward_net = BasicRewardNet(
            observation_space=env.observation_space,
            action_space=env.action_space,
        )

        gail_trainer = GAIL(
            demonstrations=trajectories,
            demo_batch_size=256,
            n_disc_updates_per_round=16,
            venv=env,
            gen_algo=learner,
            reward_net=reward_net,
            allow_variable_horizon=True,
            init_tensorboard=True,
            init_tensorboard_graph=True,
            custom_logger=logger,
        )
        gail_trainer.train(args.gail_timesteps)

    if args.rl_timesteps > 0:
        print("Starting RL Training:")
        learner.learn(args.rl_timesteps, progress_bar=True)

except KeyboardInterrupt:
    print(
        """Training interrupted by user. Will save if --save_model_path was
        used and/or export if --onnx_export_path was used."""
    )

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
    close_env()
    print(f"Mean reward after evaluation: {mean_reward}")

handle_onnx_export()
handle_model_save()
