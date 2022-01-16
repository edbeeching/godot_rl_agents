# Installation

Godot RL Agents currently supports Windows and Linux (Tested on Ubuntu 20.10).
The framework has been most extensively tested on Linux, so if you find bugs please raise an issue on the github page and we will look into it.

Please ensure to download a release version of Godot RL agents as the main branch is subject to change and may be unstable.
|  **Version**   | **Release Date** |                                **Download**                                 |
| :------------: | :--------------: | :-------------------------------------------------------------------------: |
| Release v0.1.0 |    17/10/2021    | [v0.1.0](https://github.com/edbeeching/godot_rl_agents/releases/tag/v0.1.0) |

## Windows
Unless you are an experienced python3 user, we recommend installing using
[conda](https://docs.conda.io/en/latest/miniconda.html)
```
conda create -n your_env_name python=3.8 
conda activate your_env_name
conda install -c conda-forge brotlipy # this may we required on windows
cd godot_rl_agents
pip install -r requirements.txt
pip install -e .
```

## Linux
Unless you are an experienced python3 user, we recommend installing using
[conda](https://docs.conda.io/en/latest/miniconda.html)
```
conda create -n your_env_name python=3.8 
conda activate your_env_name
cd godot_rl_agents
pip install -r requirements.txt
pip install -e .
```

# After Installation
We recommend taking a look at the examples in envs/example/envs, more details are found in the [example envs](docs/../EXAMPLE_ENVIRONMENTS.md) documentation.
