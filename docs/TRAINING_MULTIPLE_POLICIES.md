This is a brief guide on training multiple policies focusing on Rllib specifically. If you don’t require agents with different action/obs spaces, you might also consider using Sample Factory (it’s fully supported on Linux), or for simpler multi-agent envs, SB3 might work using a single shared policy for all agents.

## Installation and configuration:

### Install dependencies:

`pip install https://github.com/edbeeching/godot_rl_agents/archive/refs/heads/main.zip` (to get the latest version)

`pip install ray[rllib]`

`pip install PettingZoo`

### Download the examples file and config file:

From https://github.com/edbeeching/godot_rl_agents/tree/main/examples, you will need `rllib_example.py` and `rllib_config.yaml.`

### Open the config file:

If your env has multiple different policies you wish to train (explained below), set `env_is_multiagent: true`, otherwise keep it `false`. 

Change `env_path: None *# Set your env path here (exported executable from Godot) - e.g. 'env_path.exe' on Windows`* to point to your exported env from Godot. In-editor training with this script is not recommended as it will launch the env multiple times, to get info about different policy names, to train, and to export to onnx after training, so while possible, you would need to press `Play` in Godot editor multiple times during the process.

You can also adjust the stop criteria (set to 1200 seconds by default), and other settings.

## Configuring and exporting the Godot Env:

### Multipolicy env design differences:

When you set `env_is_multiagent` to `true`, if one agent (AIController) has `done = true` set, it will receive actions with zeros as values until all agents have set `done = true` at least once during that episode, at which point Rllib considers the episode for all agents to be done and will send a reset signal (this sets `needs_reset = true` in each AIController), and display episode rewards in stats. 

If you notice individual agents standing still or behaving oddly (depending on what action values set to zeros do in the game), it’s possible that some agents had `done = true` set previously in the episode while others are still active.

In the example env, we have a training manager script that sets all agents `done` to true at the same time after a fixed amount of steps, and we’re ignoring the `needs_reset = true` signal as we’re manually resetting all agents once the episode is done. You could also handle resetting agents when `needs_reset` is set to `true` in your env instead (keep in mind that AIControllers also automatically set it to `true` after `reset_after` steps, you can override the behavior if needed).

**The behavior described above is different from setting `env_is_multiagent` to `false`, or e.g. using the [SB3 example to train](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/ADV_STABLE_BASELINES_3.md)**, in which case a single policy will be trained as a vectorized environment, meaning that each agent can have its own episode lengths and it will continue to receive actions even after setting `done = true`, as the agents are considered to auto-reset in the env itself (the reset needs to be implemented in Godot as in the example envs).

### Setting policy names:
For each AIController, you can set a different policy name in Godot. Policies will be assigned to agents based on this name. E.g. if you have 10 agents assigned to `policy1`, they will all use policy 1, and if you have one agent assigned to `policy2`, it will use policy 2.

![setting-policy-names](https://github.com/edbeeching/godot_rl_agents/assets/61947090/13eb9b46-f7fb-467c-ad16-8609cda9f292)

Screenshot from [MultiAgent Simple env](https://github.com/edbeeching/godot_rl_agents_examples/tree/main/examples/MultiAgentSimple).

> [!IMPORTANT]  
> All agents that have the same policy name must have the same observation and action space.

## Training:
After installing the prerequisites and adjusting the config, you can start training by using `python rllib_example.py` in your conda env/venv (if you are in the same folder).
Rllib will print out useful info in the console, such as the command to start `Tensorboard` to see the training logs for the session.
Onnx files will automatically be exported once training is done and their paths will be printed near the bottom of the console log (you can also stop mid training with `CTRL+C`, but if you press it twice in a row, saving/exporting will not be done).

For an example of a multi-policy env with 2 policies, check out the [MultiAgent Simple env](https://github.com/edbeeching/godot_rl_agents_examples/tree/main/examples/MultiAgentSimple).

Additional arguments:
- You can change the folder for logging, checkpoints, and onnx files by using:`--experiment_dir [experiment_path]`,
- You can resume stopped sessions by using: `--restore [resume_path]` argument (rllib will print out the path to resume in the console if you stop training),
- You can set the config file location using `--config_file [path_to_config.yaml]` (default is set to `rllib_config.yaml`).
