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

• Download the env:

```bash
gdrl.env_from_hub -r edbeeching/godot_rl_<ENV_NAME>
chmod +x examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 # linux example
```

• Train a model from scratch:

```bash
gdrl --env=gdrl --env_path=examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 --viz
```

While the default options for sb3 work reasonably well. You may be interested in changing the hyperparameters.

We recommend taking the [sb3 example](https://github.com/edbeeching/godot_rl_agents/blob/main/examples/stable_baselines3_example.py) and modifying to match your needs.
```python
import argparse

from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv
from stable_baselines3 import PPO

# To download the env source and binary:
# 1.  gdrl.env_from_hub -r edbeeching/godot_rl_BallChase
# 2.  chmod +x examples/godot_rl_BallChase/bin/BallChase.x86_64


parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument(
    "--env_path",
    # default="envs/example_envs/builds/JumperHard/jumper_hard.x86_64",
    default=None,
    type=str,
    help="The Godot binary to use, do not include for in editor training",
)

parser.add_argument("--speedup", default=1, type=int, help="whether to speed up the physics in the env")

args, extras = parser.parse_known_args()


env = StableBaselinesGodotEnv(env_path=args.env_path, show_window=True, speedup=args.speedup, convert_action_space=True)

model = PPO("MultiInputPolicy", env, ent_coef=0.0001, verbose=2, n_steps=32, tensorboard_log="logs/log")
model.learn(200000)

print("closing env")
env.close()


```