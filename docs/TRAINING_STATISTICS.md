# Training statistics

Godot RL Agents uses [Tensorboard](https://www.tensorflow.org/tensorboard) to log training statistics. You can start Tensorboard by running the following command:

```bash
tensorboard --logdir ./logs/[RL_FRAMEWORK]
```

where `[RL_FRAMEWORK]` is one of `sb3`, `sf`, `cleanrl` or `rllib`, depending which RL framework you are using.

To view the training statistics visit [http://localhost:6006](http://localhost:6006) in your browser.

You can specify a different log directory and experiment name during traing with the `--experiment_dir` and `--experiment_name` option. e.g.

```bash
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 --experiment_name=MyExperiment_01 --experiment_dir=logs/MyDir
```
