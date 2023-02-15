import pathlib
from typing import Callable, List, Optional, Tuple

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
        env_path=None,
        port=10008,
        seed=0,
        show_window=False,
        framerate=None,
        action_repeat=None,
        timeout_wait=60,
        config=None,
    ) -> None:

        self._env = GodotEnv(
            env_path=env_path,
            port=port,
            seed=seed,
            show_window=show_window,
            framerate=framerate,
            action_repeat=action_repeat,
        )
        super().__init__(
            observation_space=self._env.observation_space,
            action_space=self._env.action_space,
            num_envs=self._env.num_envs,
        )

    def vector_reset(self) -> List[EnvObsType]:
        obs, info = self._env.reset()
        return obs

    def vector_step(
        self, actions: List[EnvActionType]
    ) -> Tuple[List[EnvObsType], List[float], List[bool], List[EnvInfoDict]]:
        actions = np.array(actions)
        self.obs, reward, term, trunc, info = self._env.step(actions, order_ij=True)
        return self.obs, reward, term, info

    def get_unwrapped(self):
        return [self._env]

    def reset_at(self, index: Optional[int]) -> EnvObsType:
        # the env is reset automatically, no need to reset it
        return self.obs[index]


def register_env():
    tune.register_env(
        "godot",
        lambda c: RayVectorGodotEnv(
            env_path=c["env_path"],
            config=c,
            port=c.worker_index + GodotEnv.DEFAULT_PORT + 10,
            show_window=c["show_window"],
            framerate=c["framerate"],
            seed=c.worker_index + c["seed"],
            action_repeat=c["framerate"],
        ),
    )


def rllib_export(model_path):
	 #get path from the config file and remove the file name
        path = model_path #full path with file name 
        path = path.split("/") #split the path into a list
        path = path[:-1] #remove the file name from the list
		#duplicate the path for the export
        export_path = path.copy()
        export_path.append("onnx")
        export_path = "/".join(export_path) #join the list into a string
        #duplicate the last element of the list
        path.append(path[-1])
        #change format from checkpoint_000500 to checkpoint-500
        temp = path[-1].split("_")
        temp = temp[-1]
        #parse the number
        temp = int(temp)
        #back to string
        temp = str(temp)
        #join the string with the new format
        path[-1] = "checkpoint-" + temp
        path = "/".join(path) #join the list into a string
        #best_checkpoint = results.get_best_checkpoint(results.trials[0], mode="max")
        #print(f".. best checkpoint was: {best_checkpoint}")

		#From here on, the relevant part to exporting the model
        new_trainer = PPOTrainer(config=exp["config"])
        new_trainer.restore(path)
        #policy = new_trainer.get_policy()
        new_trainer.export_policy_model(export_dir=export_path, onnx = 9) #This works for version 1.11.X
		#Running  with: gdrl --env_path envs/builds/JumperHard/jumper_hard.exe --export --restore envs/checkpoints/jumper_hard/checkpoint_000500/checkpoint-500
        #model = policy.model
        #export the model to onnx using torch.onnx.export
        #dummy_input = torch.randn(1, 3, 84, 84)
        #input is dictionary with key "obs" and value is a tensor of shape [...,8]
        #tensor = torch.randn([1, 2, 4, 6, 8, 10, 12, 14])
        #dummy_input = {"obs":  tensor}
        #torch.onnx.export(model, dummy_input, "model.onnx", verbose=True,
        #dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}})


def rllib_training(args, extras):
    ray.init()

    with open(args.config_file) as f:
        exp = yaml.safe_load(f)
    register_env()

    exp["config"]["env_config"]["env_path"] = args.env_path
    if args.env_path is not None:
        run_name = exp["algorithm"] + "/" + pathlib.Path(args.env_path).stem
    else:
        run_name = exp["algorithm"] + "/editor"
    print("run_name", run_name)

    if args.env_path is None:
        print("SETTING WORKERS TO 1")
        exp["config"]["num_workers"] = 1

    checkpoint_freq = 10
    checkpoint_at_end = True
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
    if not args.export:
        results = tune.run(
        exp["algorithm"],
        name=run_name,
        config=exp["config"],
        stop=exp["stop"],
        verbose=3,
        checkpoint_freq=checkpoint_freq,
        checkpoint_at_end=not args.eval,
        restore=args.restore,
    )
    if args.export:
        rllib_export(args.restore)

    ray.shutdown()

  
