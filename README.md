
# Godot RL Agents

>:warning: **The main branch supports Godot 4 only.** If you want to use Godot RL Agents in Godot 3.5 checkout the branch [godot3.5](https://github.com/edbeeching/godot_rl_agents/tree/godot3.5).

Feel free to join our [Discord](https://discord.gg/HMMD2J8SxY) for help and discussions about Godot RL Agents.


Godot RL Agents is a fully Open Source package that allows video game creators, AI researchers and hobbyists the opportunity to learn complex behaviors for their Non Player Characters or agents. 
This repository provides:
* An interface between games created in the [Godot Engine](https://godotengine.org/) and Machine Learning algorithms running in Python
* Wrappers for three well known rl frameworks: StableBaselines3, Sample Factory and [Ray RLLib](https://docs.ray.io/en/latest/rllib-algorithms.html)
* Support for memory-based agents, with LSTM or attention based interfaces
* Support for 2D and 3D games
* A suite of AI sensors to augment your agent's capacity to observe the game world
* Godot and Godot RL Agents are completely free and open source under the very permissive MIT license. No strings attached, no royalties, nothing. 

You can find out more about Godot RL agents in our AAAI-2022 Workshop [paper](https://arxiv.org/abs/2112.03636).

https://user-images.githubusercontent.com/7275864/140730165-dbfddb61-cc90-47c7-86b3-88086d376641.mp4

## Contents
<!-- no toc -->
1. [Motivation](#motivation)
2. [Installation](#installation)
3. [Examples](#examples)
4. [Creating custom environments ](#creating-custom-environments)
5. [Roadmap](#roadmap)
6. [FAQ](#faq)
7. [Licence](#licence)
8. [Citing Godot RL Agents](#citing-godot-rl-agents)
9. [Acknowledgments](#acknowledgments)
10. [References](#references)
  

## Motivation
Over the next decade advances in AI algorithms, notably in the fields of Machine Learning and Deep Reinforcement Learning, are primed to revolutionize the Video Game industry. Customizable enemies, worlds and story telling will lead to diverse gameplay experiences and new genres of games. Currently the field is dominated by large organizations and pay to use engines that have the budget to create such AI enhanced agents. The objective of the Godot RL Agents package is to lower the bar of accessability so that game developers can take their idea from creation to publication end-to-end with an open source and free package.

## Installation
Godot RL Agents has been tested on Linux and Windows and should work out of the box, we recommend using a virtual environment.
```pip install godot-rl```

In order to perform training we support 3 different backends in Godot RL Agents:
- [Stable Baselines 3](https://stable-baselines3.readthedocs.io/en/master/) ```pip install godot-rl[sb3]```
- [Sample Factory](https://www.samplefactory.dev/) ```pip install godot-rl[sf]```
- [Ray rllib](https://docs.ray.io/en/latest/rllib/index.html) ```pip install godot-rl[rllib]```


If you are having issues with the installation, please refer to our FAQ section or raise an issue.


## Examples
We have created 5 example environments of varying complexity. All environments are hosted in [separate repo](https://github.com/edbeeching/godot_rl_agents_examples) and can be downloaded with:
```shell
gdrl.env_from_hub -r edbeeching/godot_rl_<ENV_NAME>
```
Note you may need to set execution permissions on the binary with:
```shell 
chmod +x examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 
```

Examples of training scripts can be found in the [examples directory](https://github.com/edbeeching/godot_rl_agents/tree/main/examples) of the github repo. Note some RL frameworks such as sb3 and StableBaseline3 do not support action spaces that combine discrete and continous actions, we provide a wrapper that converts these to continuous spaces with a threshold at 0. Sample Factory and rllib support mixed action spaces out of the box.

## Simple environments
### BallChase
https://user-images.githubusercontent.com/7275864/209159206-a7896103-5492-4a62-8a2f-bad1e3741dae.mp4
#### Stable Baselines 3:
```shell
python examples/stable_baselines3_example.py --env_path=examples/godot_rl_BallChase/bin/BallChase.x86_64 --speedup=8
```
#### Clean RL:
```shell
python examples/clean_rl_example.py --env_path=examples/godot_rl_BallChase/bin/BallChase.x86_64 --speedup=8
```
#### Sample Factory:
- Train a model from scratch:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_BallChase/bin/BallChase.x86_64 --num_workers=10 --experiment=BallChase --viz  --speedup=8 --batched_sampling=True
```

- Download a pretrained checkpoint from the HF hub:
```shell
python -m sample_factory.huggingface.load_from_hub -r edbeeching/sample_factory_BallChase
```

- Visualize a trained model:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_BallChase/bin/BallChase.x86_64 --num_workers=1 --experiment=BallChase --viz --eval --batched_sampling=True
```

- Upload a model to the hub:
```shell 
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_BallChase/bin/BallChase.x86_64 --num_workers=1 --experiment=BallChase --viz --eval --batched_sampling=True --speedup=8 --push_to_hub --hf_repository=<HF_USERNAME>/sample_factory_BallChase
```

### FlyBy
https://user-images.githubusercontent.com/7275864/209160025-0781537e-ff37-427d-bb32-753299b30510.mp4

#### Stable Baselines 3:
```shell
python examples/stable_baselines3_example.py --env_path=examples/godot_rl_FlyBy/bin/FlyBy.x86_64 --speedup=8
```

#### Clean RL:
```shell
python examples/clean_rl_example.py --env_path=examples/godot_rl_FlyBy/bin/FlyBy.x86_64 --speedup=8
```
#### Sample-factory:
- Train a model from scratch:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_FlyBy/bin/FlyBy.x86_64 --num_workers=10 --experiment=FlyBy --viz --speedup=8 --batched_sampling=True
```

- Download a pretrained checkpoint from the HF hub:
```shell
python -m sample_factory.huggingface.load_from_hub -r edbeeching/sample_factory_FlyBy
``` 

- Visualize a trained model:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_FlyBy/bin/FlyBy.x86_64 --num_workers=1 --experiment=FlyBy --viz --eval --batched_sampling=True
```

- Upload a model to the hub:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_FlyBy/bin/FlyBy.x86_64 --num_workers=1 --experiment=FlyBy --viz --eval --batched_sampling=True --speedup=8 --push_to_hub --hf_repository=<HF_USERNAME>/sample_factory_FlyBy --max_num_frames=10000
```

## JumperHard
https://user-images.githubusercontent.com/7275864/209160056-b96ed6f4-3b8b-467a-997d-7e4833e99025.mp4
#### Stable Baselines 3:
```shell
python examples/stable_baselines3_example.py --env_path=examples/godot_rl_JumperHard/bin/JumperHard.x86_64 --speedup=8
```

#### Clean RL:
```shell
python examples/clean_rl_example.py --env_path=examples/godot_rl_JumperHard/bin/JumperHard.x86_64 --speedup=8
```
#### Sample-factory:
- Train a model from scratch:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_JumperHard/bin/JumperHard.x86_64 --num_workers=10 --experiment=JumperHard01 --viz --batched_sampling=True --speedup=8
```

- Download a pretrained checkpoint from the HF hub:
```shell
python -m sample_factory.huggingface.load_from_hub -r edbeeching/sample_factory_JumperHard
```

- Visualize a trained model:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_JumperHard/bin/JumperHard.x86_64 --num_workers=1 --experiment=JumperHard --viz --eval --batched_sampling=True
```

- Upload a model to the hub:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_JumperHard/bin/JumperHard.x86_64 --num_workers=1 --experiment=JumperHard --viz --eval --batched_sampling=True --speedup=8 --push_to_hub --hf_repository=<HF_USERNAME>/sample_factory_JumperHard --max_num_frames=10000
```
## Advanced Environments
We highly recommend training these environments on a compute cluster. As they take several hours / GPUs to converge to a decent policy. Note these environments have only been tested with Sample Factory, it unlikely you will get good performance in the FPS environment with other RL frameworks other that sample factory or rllib.
### Racer
https://user-images.githubusercontent.com/7275864/209358492-e0964b51-269b-4106-9b7d-a7b3729217b0.mp4
#### Stable Baselines 3: 
```shell
python examples/stable_baselines3_example.py --env_path=examples/godot_rl_Racer/bin/Racer.x86_64 --speedup=8
```

#### Clean RL:
```shell
python examples/clean_rl_example.py --env_path=examples/godot_rl_Racer/bin/Racer.x86_64 --speedup=8
```
#### Sample-factory:
- Train a model from scratch:
```shell
gdrl--trainer=sf --env=gdrl --env_path=examples/godot_rl_Racer/bin/Racer.x86_64 --train_for_env_steps=10000000 --experiment=Racer --reward_scale=0.01 --worker_num_splits=2 --num_envs_per_worker=2 --num_workers=40 --speedup=8 --batched_sampling=True --batch_size=2048 --num_batches_per_epoch=2 --num_epochs=2  --learning_rate=0.0001 --exploration_loss_coef=0.0001 --lr_schedule=kl_adaptive_epoch --lr_schedule_kl_threshold=0.04 --use_rnn=True --recurrence=32
```

- Download a pretrained checkpoint from the HF hub:
```shell
python -m sample_factory.huggingface.load_from_hub -r edbeeching/sample_factory_FPS
```

- Visualize a trained model:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_Racer/bin/Racer.x86_64 --num_workers=1 --experiment=Racer --viz --eval --batched_sampling=True
```

- Upload a model to the hub:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_Racer/bin/Racer.x86_64 --num_workers=1 --experiment=Racer --viz --eval --batched_sampling=True --speedup=8 --push_to_hub --hf_repository=<HF_USERNAME>/sample_factory_Racer --max_num_frames=10000
```

### Team FPS (experimental)
https://user-images.githubusercontent.com/7275864/209160117-cd95fa6b-67a0-40af-9d89-ea324b301795.mp4

#### Sample-factory:
- Train a model from scratch
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_FPS/bin/FPS.x86_64 --num_workers=10 --experiment=FPS --viz --batched_sampling=True --speedup=8 --num_workers=80 --batched_sampling=False --num_policies=4 --with_pbt=True --pbt_period_env_steps=1000000 --pbt_start_mutation=1000000 --batch_size=2048 --num_batches_per_epoch=2 --num_epochs=2 --learning_rate=0.00005 --exploration_loss_coef=0.001 --lr_schedule=kl_adaptive_epoch --lr_schedule_kl_threshold=0.08 --use_rnn=True --recurrence=32
```

- Download a pretrained checkpoint from the HF hub:
```shell
python -m sample_factory.huggingface.load_from_hub -r edbeeching/sample_factory_FPS
```

- Visualize a trained model:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_FPS/bin/FPS.x86_64 --num_workers=1 --experiment=FPS --viz --eval --batched_sampling=True
```

- Upload a model to the hub:
```shell
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_FPS/bin/FPS.x86_64 --num_workers=1 --experiment=FPS --viz --eval --batched_sampling=True --speedup=8 --push_to_hub --hf_repository=<HF_USERNAME>/sample_factory_FPS --max_num_frames=10000
```

More details about the environments can be found in [Example environments](docs/EXAMPLE_ENVIRONMENTS.md)

## Training on a cluster
The above training commands should all work on a headless cluster, just remove the ```--viz``` flag.

## Downloading the Godot Editor
The Godot 4 Game Engine is lightweight at around 50 MB, you can find the beta version on their [website](https://godotengine.org/).
Alternatively you can download the version used to create these environments (Godot 4 Beta 4) using the command:
```gdrl.download_editor```
The should work on Linux, Mac and Windows. But has not been extensively tested.
## Running Environments in the Editor
Godot RL Agents envs can be run interactively in the editor, for easy debugging and testing of new ideas.
The folling command will attempt to connect to an editor and step through 1000 random actions.
```
gdrl.interactive
```

# Creating custom environments 
(Doc is WIP, raise an issue if anything is unclear)
Once you have studied the example environments, you can follow the instructions in [Custom environments](docs/CUSTOM_ENV.md) in order to make your own. 

# Roadmap
We have number features that will soon be available in versions 0.4.0
Refer to the [Roadmap](docs/ROADMAP.md) for more information.


# FAQ
1. Why have we developed Godot RL Agents?
  The objectives of the framework are to:
* Provide a free and open source tool for Deep RL research and game development.
* Enable game creators to imbue their non-player characters with unique * behaviors.
* Allow for automated gameplay testing through interaction with an RL agent.
2. How can I contribute to Godot RL Agents?
   Please try it out, find bugs and either raise an issue or if you fix them yourself, submit a pull request.
3. When will you be providing Mac support?
   I would like to provide this ASAP but I do not own a mac so I cannot perform any manual testing of the codebase.
4. Can you help with my game project? 
   If the game example do not provide enough information, reach out to us on github and we may be able to provide some advice.
5. How similar is this tool to Unity ML agents?
   We are inspired by the the Unity ML agents toolkit and aims to be a more compact, concise ad hackable codebase, with little abstraction.

# Licence
Godot RL Agents is MIT licensed. See the [LICENSE file](LICENSE) for details.

"Cartoon Plane" (https://skfb.ly/UOLT) by antonmoek is licensed under Creative Commons Attribution (http://creativecommons.org/licenses/by/4.0/).

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
We thank the developers at Ray and Stable baselines for creating easy to use and powerful RL training frameworks.
We thank the creators of the Unity ML Agents Toolkit, which inspired us to create this work.
# References
