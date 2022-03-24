# Installation

Godot RL Agents currently supports Windows and Linux (Tested on Ubuntu 20.10).
The framework has been most extensively tested on Linux, so if you find bugs please raise an issue on the github page and we will look into it.

Please ensure to download a release version of Godot RL agents as the main branch is subject to change and may be unstable.
|  **Version**   | **Release Date** |                                **Download**                                 |
| :------------: | :--------------: | :-------------------------------------------------------------------------: |
| Release v0.1.0 |    17/10/2021    | [v0.1.0](https://github.com/edbeeching/godot_rl_agents/releases/tag/v0.1.0) |

## Windows
The [conda](https://docs.conda.io/en/latest/miniconda.html) package manager is used to install all packages.
Execute the following commands from a terminal window (e.g powershell)
Make sure you are inside the godot_rl_agents directory
```
conda create env
conda activate gdrl_conda
conda install -c conda-forge brotlipy # this may we required on windows

pip install .
```

## Linux
The [conda](https://docs.conda.io/en/latest/miniconda.html) package manager is used to install all packages.
Execute the following commands from a terminal window
Make sure you are inside the godot_rl_agents directory
```
conda create env
conda activate gdrl_conda
conda install -c conda-forge brotlipy # this may we required on windows

pip install .
```

# After Installation
We recommend taking a look at the examples in envs/example/envs, more details are found in the [example envs](docs/../EXAMPLE_ENVIRONMENTS.md) documentation.
