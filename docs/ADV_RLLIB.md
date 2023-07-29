# Advanced usage with rllib

[RLlib](https://docs.ray.io/en/latest/rllib/index.html) is an open-source library for reinforcement learning (RL), offering support for production-level, highly distributed RL workloads while maintaining unified and simple APIs for a large variety of industry applications. Whether you would like to train your agents in a multi-agent setup, purely from offline (historic) datasets, or using externally connected simulators, RLlib offers a simple solution for each of your decision making needs.

## Installation

```bash
# remove sb3 installation with pip uninstall godot-rl[sb3]
pip install godot-rl[rllib]
```

## Basic Environment Usage
Usage instructions for envs **BallChase**, **FlyBy** and **JumperHard.**

• Download the env:

```bash
gdrl.env_from_hub -r edbeeching/godot_rl_<ENV_NAME>
chmod +x examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 # linux example
```

• Train a model from scratch:

```
gdrl --trainer=rllib --env=gdrl --env_path=examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 --speedup=8 --viz
```

By default rllib will use the hyperparameters in the **ppo_test.yaml** file on the github repo. You can either modify this file, or create your own one.

Rllib contains many features and RL algorithms, it can be used to create highly complex agent behaviors. We recommend taking the time to read their [docs](https://docs.ray.io/en/latest/rllib/index.html) to learn more.
