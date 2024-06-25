import os
import pathlib
from typing import List, Optional, Tuple

import numpy as np
import ray
import yaml
from ray import tune
from ray.rllib.env.vector_env import VectorEnv
from ray.rllib.utils.typing import EnvActionType, EnvInfoDict, EnvObsType

from godot_rl.core.godot_env import GodotEnv


class RayVectorGodotEnv(VectorEnv):
    def __init__(
        self,
        port=10008,
        seed=0,
        config=None,
    ) -> None:
        self._env = GodotEnv(
            env_path=config["env_path"],
            port=port,
            seed=seed,
            show_window=config["show_window"],
            action_repeat=config["action_repeat"],
            speedup=config["speedup"],
        )
        super().__init__(
            observation_space=self._env.observation_space,
            action_space=self._env.action_space,
            num_envs=self._env.num_envs,
        )

    def vector_reset(
        self, *, seeds: Optional[List[int]] = None, options: Optional[List[dict]] = None
    ) -> List[EnvObsType]:
        self.obs, info = self._env.reset()
        return self.obs, info

    def vector_step(
        self, actions: List[EnvActionType]
    ) -> Tuple[List[EnvObsType], List[float], List[bool], List[EnvInfoDict]]:
        actions = np.array(actions, dtype=np.dtype(object))
        self.obs, reward, term, trunc, info = self._env.step(actions, order_ij=True)
        return self.obs, reward, term, trunc, info

    def get_unwrapped(self):
        return [self._env]

    def reset_at(
        self,
        index: Optional[int] = None,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ) -> EnvObsType:
        # the env is reset automatically, no need to reset it
        return self.obs[index], {}


def register_env():
    tune.register_env(
        "godot",
        lambda c: RayVectorGodotEnv(
            config=c,
            port=c.worker_index + GodotEnv.DEFAULT_PORT + 10,
            seed=c.worker_index + c["seed"],
        ),
    )


# Refactored section: Commented onnx section was removed as it was re-implemented in rllib_example.py


def rllib_training(args, extras):
    with open(args.config_file) as f:
        exp = yaml.safe_load(f)
    register_env()

    exp["config"]["env_config"]["env_path"] = args.env_path
    exp["config"]["env_config"]["seed"] = args.seed

    if args.env_path is not None:
        run_name = exp["algorithm"] + "/" + pathlib.Path(args.env_path).stem
    else:
        run_name = exp["algorithm"] + "/editor"
    print("run_name", run_name)

    if args.num_gpus is not None:
        exp["config"]["num_gpus"] = args.num_gpus

    if args.env_path is None:
        print("SETTING WORKERS TO 1")
        exp["config"]["num_workers"] = 1

    checkpoint_freq = 10

    exp["config"]["env_config"]["show_window"] = args.viz
    exp["config"]["env_config"]["speedup"] = args.speedup

    if args.eval or args.export:
        checkpoint_freq = 0
        exp["config"]["env_config"]["show_window"] = True
        exp["config"]["env_config"]["framerate"] = None
        exp["config"]["lr"] = 0.0
        exp["config"]["num_sgd_iter"] = 1
        exp["config"]["num_workers"] = 1
        exp["config"]["train_batch_size"] = 8192
        exp["config"]["sgd_minibatch_size"] = 128

        exp["config"]["explore"] = False
        exp["stop"]["training_iteration"] = 999999

    print(exp)

    ray.init(num_gpus=exp["config"]["num_gpus"] or 1)

    if not args.export:
        tune.run(
            exp["algorithm"],
            name=run_name,
            config=exp["config"],
            stop=exp["stop"],
            verbose=3,
            checkpoint_freq=checkpoint_freq,
            checkpoint_at_end=not args.eval,
            restore=args.restore,
            storage_path=os.path.abspath(args.experiment_dir) or os.path.abspath("logs/rllib"),
            trial_name_creator=lambda trial: (
                f"{args.experiment_name}" if args.experiment_name else f"{trial.trainable_name}_{trial.trial_id}"
            ),
        )
    if args.export:
        raise NotImplementedError("Use examples/rllib_example.py to export to onnx.")
        # rllib_export(args.restore)

    ray.shutdown()
