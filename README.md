
# Godot RL Agents
The Godot RL Agents is a fully Open Source packages that allows video game creators, AI researchers and hobbiest the opportunity to learn complex behaviors for their Non Player Characters or agents. 
This repository provides:
* An interface between games created in Godot and Machine Learning algorithms running in Python
* Access to 21 state of the art Machine Learning algorithms, provided by the [Ray RLLib](https://docs.ray.io/en/latest/rllib-algorithms.html) framework.
* Support for memory-based agents, with LSTM or attention based interfaces
* Support for 2D and 3D games
* A suite of AI sensors to augment your agent's capacity to observe the game world
* Godot and Godot RL agents are completely free and open source under the very permissive MIT license. No strings attached, no royalties, nothing. 

You can find out more about Godot RL agents in our AAAI-2022 Workshop [paper](https://arxiv.org/abs/2112.03636).

https://user-images.githubusercontent.com/7275864/140730165-dbfddb61-cc90-47c7-86b3-88086d376641.mp4

## Contents
<!-- no toc -->
1. [Motivation](#motivation)
2. [Citing Godot RL Agents](#citing-godot-rl-agents)
3. [Installation](#installation)
4. [Examples](#examples)
5. [Documentation](#documentation)
6. [Roadmap](#roadmap)
7. [FAQ](#faq)
8. [Licence](#licence)
9. [Acknowledgments](#acknowledgments)
10. [References](#references)
  

### Motivation
Over the next decade advances in AI algorithms, notably in the fields of Machine Learning and Deep Reinforcement Learning, are primed to revolutionize the Video Game industry. Customizable enemies, worlds and story telling will lead to diverse gameplay experiences and new genres of games. Currently the field is dominated by large organizations and pay to use engines that have the budget to create such AI enhanced agents. The objective of the Godot RL Agents package is to lower the bar of accessability so that game developers can take their idea from creation to publication end-to-end with an open source and free package.
### Citing Godot RL Agents
```
@article{beeching2021godotrlagents,
  author={Beeching, Edward and Dibangoye, Jilles and 
    Simonin, Olivier and Wolf, Christian},
title = {Godot Reinforcement Learning Agents},
journal = {{arXiv preprint arXiv:2112.03636.},
year = {2021}, 
}


```
### Installation
Please follow the [installation instructions](docs/INSTALLATION.md) to install Godot RL agents.
### Examples
We provide several reference implementations and instructions to implement your own environment, please refer to the [Examples](docs/EXAMPLE_ENVIRONMENTS.md) documentation.
### Creating custom environments
Once you have studied the example environments, you can follow the instructions in [Custom environments](docs/CUSTOM_ENV.md) in order to make your own. 
### Roadmap
We have number features that will soon be available in versions 0.2.0 and 0.3.0. 
Refer to the [Roadmap](docs/ROADMAP.md) for more information.


### FAQ
1. Why have we developed Godot RL Agents?
  The objectives of the framework are to:
* Provide a free and open source tool for Deep RL research and game development.
* Enable game creators to imbue their non-player characters with unique * behaviors.
* Allow for automated gameplay testing through interaction with an RL agent.
1. How can I contribute to Godot RL Agents?
   Please try it out, find bugs and either raise an issue or if you fix them yourself, submit a pull request.
2. When will you be providing Mac support?
   I would like to provide this ASAP but I do not own a mac so I cannot perform any manual testing of the codebase.
3. Can you help with my game project? 
   If the game example do not provide enough information, reach out to us on github and we may be able to provide some advice.
4. How similar is this tool to Unity ML agents?
   We are inspired by the the Unity ML agents toolkit and make no effort to hide it.

### Licence
Godot RL Agents is MIT licensed. See the [LICENSE file](LICENSE) for details.

"Cartoon Plane" (https://skfb.ly/UOLT) by antonmoek is licensed under Creative Commons Attribution (http://creativecommons.org/licenses/by/4.0/).
### Acknowledgments
We thank the authors of the Godot Engine for providing such a powerful and flexible game engine for AI agent development.
We thank the developers at Ray and Stable baselines for creating easy to use and powerful RL training frameworks.
We thank the creators of the Unity ML Agents Toolkit, which inspired us to create this work.
### References
