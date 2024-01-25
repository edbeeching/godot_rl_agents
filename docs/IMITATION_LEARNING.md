# Imitation Learning

For imitation learning, we use the imitation library: https://github.com/HumanCompatibleAI/imitation

From the docs:
> Imitation provides clean implementations of imitation and reward learning algorithms, under a unified and user-friendly API. Currently, we have implementations of Behavioral Cloning, DAgger (with synthetic examples), density-based reward modeling, Maximum Causal Entropy Inverse Reinforcement Learning, Adversarial Inverse Reinforcement Learning, Generative Adversarial Imitation Learning, and Deep RL from Human Preferences.

### Installation:
In the conda env or Python venv where you have Godot-RL installed, use:
`pip install imitation`.

Then you can use it by using and or modifying [this example](/examples/sb3_imitation.py).

### Tutorial
For a quick tutorial on how to use Imitation Learning, we'll modify one of the example environments to use imitation learning. This tutorial assumes you have Godot, Godot RL Agents, Imitation, and Blender installed, and have completed the quick-start guide from the readme of this repository and potentially the [custom env tutorial](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md) as well.

#### Download all of the examples from here: https://github.com/edbeeching/godot_rl_agents_examples/tree/main (either clone or click on `Code` > `Download ZIP`)
