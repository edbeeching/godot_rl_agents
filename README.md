# Godot RL Agents

Feel free to join our [Discord](https://discord.gg/HMMD2J8SxY) for help and discussions about Godot RL Agents.

Godot RL Agents is a fully Open Source package that allows video game creators, AI researchers and hobbyists the opportunity to learn complex behaviors for their Non Player Characters or agents.
This repository provides:

- An interface between games created in the [Godot Engine](https://godotengine.org/) and Machine Learning algorithms running in Python
- Wrappers for four well known rl frameworks: [StableBaselines3](https://stable-baselines3.readthedocs.io/en/master/), [Sample Factory](https://www.samplefactory.dev/), [Ray RLLib](https://docs.ray.io/en/latest/rllib-algorithms.html) and [CleanRL](https://github.com/vwxyzjn/cleanrl).
- Support for memory-based agents, with LSTM or attention based interfaces
- Support for 2D and 3D games
- A suite of AI sensors to augment your agent's capacity to observe the game world
- Godot and Godot RL Agents are completely free and open source under the very permissive MIT license. No strings attached, no royalties, nothing.

You can find out more about Godot RL agents in our AAAI-2022 Workshop [paper](https://arxiv.org/abs/2112.03636).

[https://user-images.githubusercontent.com/7275864/140730165-dbfddb61-cc90-47c7-86b3-88086d376641.mp4](https://user-images.githubusercontent.com/7275864/140730165-dbfddb61-cc90-47c7-86b3-88086d376641.mp4)

## Quickstart Guide

This quickstart guide will get you up and running using the Godot RL Agents library with the StableBaselines3 backend, as this supports Windows, Mac and Linux. We suggest starting here and then trying out our Advanced tutorials when learning more complex agent behaviors.
There is also a [video tutorial](https://www.youtube.com/watch?v=f8arMv_rtUU) which shows how to install the library and create a custom env.
### Installation and first training

Install the Godot RL Agents library. If you are new to Python or not using a virtual environment, it's highly recommended to create one using [venv](https://docs.python.org/3/library/venv.html) or [Conda](https://www.machinelearningplus.com/deployment/conda-create-environment-and-everything-you-need-to-know-to-manage-conda-virtual-environment/) to isolate your project dependencies.

Once you have set up your virtual environment, proceed with the installation:

```bash
pip install godot-rl
```

Download one, or more of [examples](https://github.com/edbeeching/godot_rl_agents_examples), such as BallChase, JumperHard, FlyBy.

```bash
gdrl.env_from_hub -r edbeeching/godot_rl_JumperHard
```

You may need to add run permissions on the game executable.

```bash
chmod +x examples/godot_rl_JumperHard/bin/JumperHard.x86_64
```

Train and visualize

```bash
gdrl --env=gdrl --env_path=examples/godot_rl_JumperHard/bin/JumperHard.x86_64 --experiment_name=Experiment_01 --viz
```

### In editor interactive training

You can also train an agent in the Godot editor, without the need to export the game executable.

1. Download the Godot 4 Game Engine from [https://godotengine.org/](https://godotengine.org/)
2. Open the engine and import the JumperHard example in `examples/godot_rl_JumperHard`
3. Start in editor training with: `gdrl`

### Creating a custom environment

There is a dedicated tutorial on creating custom environments [here](docs/CUSTOM_ENV.md). We recommend following this tutorial before trying to create your own environment.

If you face any issues getting started, please reach out on our [Discord](https://discord.gg/HMMD2J8SxY) or raise a GitHub issue.

### Exporting and loading your trained agent in onnx format:

The latest version of the library provides experimental support for onnx models with the Stable Baselines 3, rllib, and CleanRL training frameworks.

1. First run train you agent using the [sb3 example](https://github.com/edbeeching/godot_rl_agents/blob/main/examples/stable_baselines3_example.py) ([instructions for using the script](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/ADV_STABLE_BASELINES_3.md#train-a-model-from-scratch)), enabling the option `--onnx_export_path=GameModel.onnx`
2. Then, using the **mono version** of the Godot Editor, add the onnx model path to the sync node. If you do not seen this option you may need to download the plugin from [source](https://github.com/edbeeching/godot_rl_agents_plugin)
3. The game should now load and run using the onnx model. If you are having issues building the project, ensure that the contents of the `.csproj` and `.sln` files in you project match that those of the plugin [source](https://github.com/edbeeching/godot_rl_agents_plugin).

## Advanced usage

[https://user-images.githubusercontent.com/7275864/209160117-cd95fa6b-67a0-40af-9d89-ea324b301795.mp4](https://user-images.githubusercontent.com/7275864/209160117-cd95fa6b-67a0-40af-9d89-ea324b301795.mp4)

Please ensure you have successfully completed the quickstart guide before following this section.

Godot RL Agents supports 4 different RL training frameworks, the links below detail a more in depth guide of how to use a particular backend:

- [StableBaselines3](docs/ADV_STABLE_BASELINES_3.md) (Windows, Mac, Linux)
- [SampleFactory](docs/ADV_SAMPLE_FACTORY.md) (Mac, Linux)
- [CleanRL](docs/ADV_CLEAN_RL.md) (Windows, Mac, Linux)
- [Ray rllib](docs/ADV_RLLIB.md) (Windows, Mac, Linux)

## Contributing
We welcome new contributions to the library, such as:
- New environments made in Godot
- Improvements to the readme files
- Additions to the python codebase

Start by forking the repo and then cloning it to your machine, creating a venv and performing an editable installation.

```
# If you want to PR, you should fork the lib or ask to be a contibutor

git clone git@github.com:YOUR_USERNAME/godot_rl_agents.git
cd godot_rl_agents
python -m venv venv
pip install -e ".[dev]"
# check tests run
make test
```

Then add your features.
Format your code with:
```
make style
make quality
```
Then make a PR against main on the original repo.

## FAQ

### Why have we developed Godot RL Agents?

The objectives of the framework are to:

- Provide a free and open source tool for Deep RL research and game development.
- Enable game creators to imbue their non-player characters with unique behaviors.
- Allow for automated gameplay testing through interaction with an RL agent.

### How can I contribute to Godot RL Agents?

Please try it out, find bugs and either raise an issue or if you fix them yourself, submit a pull request.

### When will you be providing Mac support?

This should now be working, let us know if you have any issues.

### Can you help with my game project?

If the README and docs here not provide enough information, reach out to us on [Discord](https://discord.gg/HMMD2J8SxY) or GitHub and we may be able to provide some advice.

### How similar is this tool to Unity ML agents?

We are inspired by the the Unity ML agents toolkit and we aim to provide a more compact, concise and hackable codebase, with little abstraction.

# License

Godot RL Agents is MIT licensed. See the [LICENSE file](https://www.notion.so/huggingface2/LICENSE) for details.

"Cartoon Plane" ([https://skfb.ly/UOLT](https://skfb.ly/UOLT)) by antonmoek is licensed under Creative Commons Attribution ([http://creativecommons.org/licenses/by/4.0/](http://creativecommons.org/licenses/by/4.0/)).

# Citing Godot RL Agents

```
@article{beeching2021godotrlagents,
  author={Beeching, Edward and Dibangoye, Jilles and
    Simonin, Olivier and Wolf, Christian},
title = {Godot Reinforcement Learning Agents},
journal = {{arXiv preprint arXiv:2112.03636.},
year = {2021},
}
```

# Acknowledgments

We thank the authors of the Godot Engine for providing such a powerful and flexible game engine for AI agent development.
We thank the developers at Sample Factory, Clean RL, Ray and Stable Baselines for creating easy to use and powerful RL training frameworks.
We thank the creators of the Unity ML Agents Toolkit, which inspired us to create this work.
