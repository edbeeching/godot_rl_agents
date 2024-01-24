""" Optuna example that optimizes the hyperparameters of
a reinforcement learning agent using PPO implementation from Stable-Baselines3
on a Gymnasium environment.

Taken from: https://github.com/optuna/optuna-examples/blob/main/rl/sb3_simple.py

This is a simplified version of what can be found in https://github.com/DLR-RM/rl-baselines3-zoo.

You can run this example as follows:
    $ python examples/stable_baselines3_hp_tuning.py --env_path=<path/to/your/env> --speedup=8 --n_parallel=1

Feel free to copy this script and update, add or remove the hp values to your liking.
"""

try:
    import optuna
    from optuna.pruners import MedianPruner
    from optuna.samplers import TPESampler
except ImportError as e:
    print(e)
    print("You need to install optuna to use the hyperparameter tuning script. Try: pip install optuna")
    exit()

import argparse
from typing import Any, Dict

import gymnasium as gym
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor

from godot_rl.core.godot_env import GodotEnv
from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument(
    "--env_path", default=None, type=str, help="The Godot binary to use, do not include for in editor training"
)
parser.add_argument("--speedup", default=8, type=int, help="whether to speed up the physics in the env")
parser.add_argument(
    "--n_parallel",
    default=1,
    type=int,
    help="How many instances of the environment executable to launch - requires --env_path to be set if > 1.",
)

args, extras = parser.parse_known_args()

# Create a temporal environment to get the number of agents per environment dynamically
env = StableBaselinesGodotEnv(env_path=args.env_path, speedup=args.speedup)
n_agents = env.num_envs
env.close()

N_TRIALS = 20
N_STARTUP_TRIALS = 5
N_EVALUATIONS = 1
N_TIMESTEPS = 10240
EVAL_FREQ = max(int((N_TIMESTEPS // N_EVALUATIONS) // (n_agents * args.n_parallel)), 1)
N_EVAL_EPISODES = 3
STOP_TRIAL_TIMEOUT = 60 * 60 * 2  # 2 hours

DEFAULT_HYPERPARAMS = {
    "ent_coef": 0.005,
}


def sample_ppo_params(trial: optuna.Trial) -> Dict[str, Any]:
    """Sampler for PPO hyperparameters."""
    learning_rate = trial.suggest_loguniform("learning_rate", 0.0003, 0.003)
    n_steps = trial.suggest_categorical("n_steps", [32, 64, 128, 256, 512, 1024, 2048])
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128, 256, 512, 1024, 2048])
    n_epochs = trial.suggest_categorical("n_epochs", [2, 4, 8, 16])

    return {
        "learning_rate": learning_rate,
        "n_steps": n_steps,
        "batch_size": batch_size,
        "n_epochs": n_epochs,
    }


class TrialEvalCallback(EvalCallback):
    """Callback used for evaluating and reporting a trial."""

    def __init__(
        self,
        eval_env: gym.Env,
        trial: optuna.Trial,
        n_eval_episodes: int = 5,
        eval_freq: int = 10000,
        deterministic: bool = True,
        verbose: int = 0,
    ):
        super().__init__(
            eval_env=eval_env,
            n_eval_episodes=n_eval_episodes,
            eval_freq=eval_freq,
            deterministic=deterministic,
            verbose=verbose,
        )
        self.trial = trial
        self.eval_idx = 0
        self.is_pruned = False

    def _on_step(self) -> bool:
        if self.eval_freq > 0 and self.n_calls % self.eval_freq == 0:
            super()._on_step()
            self.eval_idx += 1
            self.trial.report(self.last_mean_reward, self.eval_idx)
            # Prune trial if need.
            if self.trial.should_prune():
                self.is_pruned = True
                return False
        return True


def objective(trial: optuna.Trial) -> float:
    kwargs = DEFAULT_HYPERPARAMS.copy()
    # Sample hyperparameters.
    kwargs.update(sample_ppo_params(trial))
    print("args:", kwargs)
    # Create the RL model.
    training_port = GodotEnv.DEFAULT_PORT + 1
    model = PPO(
        "MultiInputPolicy",
        VecMonitor(
            StableBaselinesGodotEnv(
                env_path=args.env_path, speedup=args.speedup, n_parallel=args.n_parallel, port=training_port
            )
        ),
        tensorboard_log="logs/optuna",
        **kwargs,
    )
    # Create env used for evaluation.
    eval_env = VecMonitor(StableBaselinesGodotEnv(env_path=args.env_path, speedup=args.speedup))

    # Create the callback that will periodically evaluate and report the performance.
    eval_callback = TrialEvalCallback(
        eval_env, trial, n_eval_episodes=N_EVAL_EPISODES, eval_freq=EVAL_FREQ, deterministic=True
    )

    nan_encountered = False
    try:
        model.learn(N_TIMESTEPS, callback=eval_callback)
    except AssertionError as e:
        # Sometimes, random hyperparams can generate NaN.
        print(e)
        nan_encountered = True
    finally:
        # Free memory.
        print("Freeing memory...")
        model.env.close()
        eval_env.close()

    # Tell the optimizer that the trial failed.
    if nan_encountered:
        # return 0
        return float("nan")

    if eval_callback.is_pruned:
        raise optuna.exceptions.TrialPruned()

    return eval_callback.last_mean_reward


if __name__ == "__main__":
    # Set pytorch num threads to 1 for faster training.
    torch.set_num_threads(1)

    sampler = TPESampler(n_startup_trials=N_STARTUP_TRIALS)
    # Do not prune before 1/3 of the max budget is used.
    pruner = MedianPruner(n_startup_trials=N_STARTUP_TRIALS, n_warmup_steps=N_EVALUATIONS // 3)

    study = optuna.create_study(sampler=sampler, pruner=pruner, direction="maximize")
    try:
        study.optimize(objective, n_trials=N_TRIALS, timeout=STOP_TRIAL_TIMEOUT)
    except KeyboardInterrupt:
        pass

    print("Number of finished trials: ", len(study.trials))

    print("Best trial:")
    trial = study.best_trial

    print("  Value: ", trial.value)

    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))

    print("  User attrs:")
    for key, value in trial.user_attrs.items():
        print("    {}: {}".format(key, value))
