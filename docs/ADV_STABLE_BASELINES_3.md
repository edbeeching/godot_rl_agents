# StableBaselines3

Stable Baselines3 (SB3) is a set of reliable implementations of reinforcement learning algorithms in PyTorch. It is the next major version of Stable Baselines.

Github repository: https://github.com/DLR-RM/stable-baselines3

Paper: https://jmlr.org/papers/volume22/20-1364/20-1364.pdf

RL Baselines3 Zoo (training framework for SB3): https://github.com/DLR-RM/rl-baselines3-zoo

RL Baselines3 Zoo provides a collection of pre-trained agents, scripts for training, evaluating agents, tuning hyperparameters, plotting results and recording videos.

SB3 Contrib (experimental RL code, latest algorithms): https://github.com/Stable-Baselines-Team/stable-baselines3-contrib

Main Features
- Unified structure for all algorithms
- PEP8 compliant (unified code style)
- Documented functions and classes
- Tests, high code coverage and type hints
- Clean code 
- Tensorboard support


## Installation
```bash
pip install godot-rl[sb3]
```

## Basic Environment Usage
Usage instructions for envs **BallChase**, **FlyBy** and **JumperHard.**

### Download the env:

```bash
gdrl.env_from_hub -r edbeeching/godot_rl_<ENV_NAME>
chmod +x examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 # linux example
```

### Train a model from scratch:

```bash
gdrl --env=gdrl --env_path=examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 --experiment_name=Experiment_01 --viz
```

While the default options for sb3 work reasonably well. You may be interested in changing the hyperparameters.

We recommend taking the [sb3 example](https://github.com/edbeeching/godot_rl_agents/blob/main/examples/stable_baselines3_example.py) and modifying to match your needs. 

The example exposes more parameters for the user to configure, such as `--speedup` to run the environment faster than realtime and the `--n_parallel` to launch several instances of the game executable in order to accelerate training (not available for in-editor training). 

## SB3 Example script usage:
To use the example script, first move to the location where the downloaded script is in the console/terminal, and then try some of the example use cases below:

### Train a model in editor:
```bash
python stable_baselines3_example.py
```

### Train a model using an exported environment:
```bash
python stable_baselines3_example.py --env_path=path_to_executable
```
Note that the exported environment will not be rendered in order to accelerate training.
If you want to display it, add the `--viz` argument.

### Train an exported environment using 4 environment processes:
```bash
python stable_baselines3_example.py --env_path=path_to_executable --n_parallel=4
```

### Train an exported environment using 8 times speedup:
```bash
python stable_baselines3_example.py --env_path=path_to_executable --speedup=8
```

### Set an experiment directory and name:
You can optionally set an experiment directory and name to override the default. When saving checkpoints, you need to use a unique directory or name for each run (more about that below).
```bash
python stable_baselines3_example.py --experiment_dir="experiments" --experiment_name="experiment1"
```

### Train a model for 100_000 steps then save and export the model:
The exported .onnx model can be used by the Godot sync node to run inference from Godot directly, while the saved .zip model can be used to resume training later or run inference from the example script by adding `--inference`.
```bash
python stable_baselines3_example.py --timesteps=100_000 --onnx_export_path=model.onnx --save_model_path=model.zip
```
Note: If you interrupt/halt training using `ctrl + c`, it should save/export models before closing training (but only if you have included the corresponding arguments mentioned above). Using checkpoints (see below) is a safer way to keep progress.


### Resume training from a saved .zip model:
This will load the previously saved model.zip, and resume training for another 100 000 steps, so the saved model will have been trained for 200 000 steps in total.
Note that the console log will display the `total_timesteps` for the last training session only, so it will show `100000` instead of `200000`. 
```bash
python stable_baselines3_example.py --timesteps=100_000 --save_model_path=model_200_000_total_steps.zip --resume_model_path=model.zip
```

### Save periodic checkpoints:
You can save periodic checkpoints and later resume training from any checkpoint using the same CL argument as above, or run inference on any checkpoint just like with the saved model.
Note that you need to use a unique `experiment_name` or `experiment_dir` for each run so that checkpoints from one run won't overwrite checkpoints from another run.
Alternatively, you can remove the folder containing checkpoints from a previous run if you don't need them anymore.

E.g. train for a total of 2 000 000 steps with checkpoints saved at every 50 000 steps:

```bash
python stable_baselines3_example.py --experiment_name=experiment1 --timesteps=2_000_000 --save_checkpoint_frequency=50_000
```

Checkpoints will be saved to `logs\sb3\experiment1_checkpoints` in the above case, the location is affected by `--experiment_dir` and `--experiment_name`.

### Run inference on a saved model for 100_000 steps:
You can run inference on a model that was previously saved using either `--save_model_path` or `--save_checkpoint_frequency`.
```bash
python stable_baselines3_example.py --timesteps=100_000 --resume_model_path=model.zip --inference
```

### Use a linear learning rate schedule:
By default, the learning rate will be constant throughout training.
If you add `--linear_lr_schedule`, learning rate will decrease with the progress,
and reach 0 at `--timesteps` value.
```bash
python stable_baselines3_example.py --timesteps=1_000_000 --linear_lr_schedule
```
