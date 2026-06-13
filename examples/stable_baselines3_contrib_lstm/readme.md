# StableBaselines3 contrib PPO-LSTM example

This example is based on the SB3 example but adjusted to use the sb3-contrib package instead. This allows for PPO-LSTM.

Github repository: https://github.com/Stable-Baselines-Team/stable-baselines3-contrib

Please note that you need to install sb3-contrib:

## Installation
```bash
pip install godot-rl sb3-contrib
```

## Basic Environment Usage

The SB3-contrib example works analogously as SB3. See following documentation for environment usage and arguments:

https://github.com/edbeeching/godot_rl_agents/blob/main/docs/ADV_CLEAN_RL.md

However, ONNX export is currently not supported.

In addition to the arguments in the SB3 example, the number of units of the LSTM layer can be set.

### Train an exported environment using a larger-than-default number of units in the LSTM layer:
```bash
python stable_baselines3_contrib_lstm_example.py --env_path=path_to_executable --lstm_hidden_size 64
```
