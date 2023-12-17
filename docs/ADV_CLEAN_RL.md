# CleanRL

CleanRL is a Deep Reinforcement Learning library that provides high-quality single-file implementation with research-friendly features. The implementation is clean and simple, yet we can scale it to run thousands of experiments using AWS Batch. The highlight features of CleanRL are:

- 📜 Single-file implementation
- Every detail about an algorithm variant is put into a single standalone file.
- For example, our ppo_atari.py only has 340 lines of code but contains all implementation details on how PPO works with Atari games, so it is a great reference implementation to read for folks who do not wish to read an entire modular library.
- 📊 Benchmarked Implementation (7+ algorithms and 34+ games at https://benchmark.cleanrl.dev)
- 📈 Tensorboard Logging
- 🪛 Local Reproducibility via Seeding
- 🎮 Videos of Gameplay Capturing
- 🧫 Experiment Management with [Weights and Biases](https://wandb.ai/site)
- 💸 Cloud Integration with docker and AWS
 

You can read more about CleanRL in their [technical paper](https://arxiv.org/abs/2111.08819) and [documentation](https://docs.cleanrl.dev/).

# Installation
```bash
pip install godot-rl[cleanrl]
```

While the default options for cleanrl work reasonably well. You may be interested in changing the hyperparameters.
We recommend taking the [cleanrl example](https://github.com/edbeeching/godot_rl_agents/blob/main/examples/clean_rl_example.py) and modifying to match your needs.

## CleanRL Example script usage:
To use the example script, first move to the location where the downloaded script is in the console/terminal, and then try some of the example use cases below:

### Train a model in editor:
```bash
python clean_rl_example.py
```

### Train a model using an exported environment:
```bash
python clean_rl_example.py --env_path=path_to_executable
```
Note that the exported environment will not be rendered in order to accelerate training.
If you want to display it, add the `--viz` argument.

### Train an exported environment using 4 environment processes:
```bash
python clean_rl_example.py --env_path=path_to_executable --n_parallel=4
```

### Train an exported environment using 8 times speedup:
```bash
python clean_rl_example.py --env_path=path_to_executable --speedup=8
```

### Set an experiment directory and name:
```bash
python clean_rl_example.py --experiment_dir="experiments" --experiment_name="experiment1"
```

### Train a model for 100_000 steps then export the model to onnx (can be used for inference in Godot, including in exported games - tested on only some platforms for now):
```bash
python clean_rl_example.py --total-timesteps=100_000 --onnx_export_path=model.onnx
```

There are many other command line arguments defined in the [cleanrl example](https://github.com/edbeeching/godot_rl_agents/blob/main/examples/clean_rl_example.py) file.
