# Imitation Learning

For imitation learning, we use the imitation library: https://github.com/HumanCompatibleAI/imitation

From the docs:
> Imitation provides clean implementations of imitation and reward learning algorithms, under a unified and
> user-friendly API. Currently, we have implementations of Behavioral Cloning, DAgger (with synthetic examples),
> density-based reward modeling, Maximum Causal Entropy Inverse Reinforcement Learning, Adversarial Inverse
> Reinforcement
> Learning, Generative Adversarial Imitation Learning, and Deep RL from Human Preferences.

### Installation:

In the conda env or Python venv where you have Godot-RL installed, use:
`pip install imitation`.

Then you can use it by using and or modifying [this example](/examples/sb3_imitation.py).

### Tutorial

For a quick tutorial on how to use Imitation Learning, we'll modify one of the example environments to use imitation
learning. This tutorial assumes you have Godot, Godot RL Agents, Imitation, and Blender installed, and have completed
the quick-start guide from the readme of this repository and potentially
the [custom env tutorial](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md) as well.

#### Download all the examples:

https://github.com/edbeeching/godot_rl_agents_examples/tree/main (either clone or click on `Code` > `Download ZIP`)

#### Update plugin:

At the time of writing this tutorial, envs don't currently have the plugin version that includes the demo recorder.
We'll use the MultiLevelRobotEnv example. First download
the [latest plugin from GitHub](https://github.com/edbeeching/godot_rl_agents_plugin) and then copy the `addons` folder
from the plugin folder to the previously downloaded example folder:
`godot_rl_agents_examples-main\examples\MultiLevelRobot\addons` (replace all the files or remove the addons folder in
the game example before pasting the one from the plugin).

#### In Godot editor, import the MultiLevelRobotEnv example.

#### Open the testing scene:

![testing scene](https://github.com/edbeeching/godot_rl_agents/assets/61947090/212ae90b-9077-472b-81b9-4f1a10fff1a1)

We'll use this scene to record the demonstrations. First, we have to modify the AIController settings to use the demo
recorder mode.

#### Right click on `GameScene`, then click on `Editable Children`:

![make game scene editable](https://github.com/edbeeching/godot_rl_agents/assets/61947090/91e5a74f-1186-4b28-bdbe-8032b9b9d6ab)

#### Right click on `Robot`, then click on `Editable Children`:

![make robot editable](https://github.com/edbeeching/godot_rl_agents/assets/61947090/2e0bab9c-5b65-4b1e-843d-d56cc4882a0a)

#### Set Control Mode to `Record Expert Demos` and write a file path to save the demos to:

![image](https://github.com/edbeeching/godot_rl_agents/assets/61947090/be531a1e-14e9-4fb3-8055-698d3f99a1e5)

#### Add an `InputEventKey` to `Remove Last Episode Key`:

![image](https://github.com/edbeeching/godot_rl_agents/assets/61947090/ff94ffb6-23e8-4c3e-8dc3-ca8d07cbfc45)

#### Set a key of your choice, then click on `OK`:

![image](https://github.com/edbeeching/godot_rl_agents/assets/61947090/1d10a016-2944-411d-a4ab-cb00409fda04)

This key will be used to remove the last episode during recording. We can use this during demo recording if we recorded
an episode with a non-optimal outcome (e.g. if the robot fell or hit an enemy robot, the episode timed out, etc.).

#### Set action_repeat to 10:

This will produce some input lag while recording demos, but this is what is set for training/inference as well. What it
means is that the currently set action will repeat for 10 frames before the next action is set. Also, only once every 10
frames, the obs/action will be read and saved to the demo file. You can optionally set a lower value here to reduce lag,
in that case
you may also want to lower it in the `sync` node in `training_scene.tscn` and `testing_scene.tscn`.

![action repeat 10](https://github.com/edbeeching/godot_rl_agents/assets/61947090/50dd4ca3-1386-4435-a229-2becd71c42a1)

#### Open `RobotAIController.gd`:

(You can search for it in `Filter Files` box in the `FileSystem` if it's not showing up)

![image](https://github.com/edbeeching/godot_rl_agents/assets/61947090/49651e15-e1e9-4307-936d-7e6fbf434637)

We need to change some things in the AIController to allow for demo recording to work properly.

#### Modify `set_action` and implement `get_action`

Find the set_action method, and replace the code of the method with:

```gdscript
## Returns the action that is currently applied to the robot.
func get_action():
	return [robot.requested_movement.x, robot.requested_movement.z]

## Sets the action to the robot. 
func set_action(action = null) -> void:	
	if action:
		robot.requested_movement = Vector3(
			clampf(action.movement[0], -1.0, 1.0), 
			0.0, 
			clampf(action.movement[1], -1.0, 1.0)).limit_length(1.0)
	else:
		robot.requested_movement = Vector3(
			int(Input.is_action_pressed("ui_down")) - int(Input.is_action_pressed("ui_up")), 
			0.0, 
			int(Input.is_action_pressed("ui_left")) - int(Input.is_action_pressed("ui_right"))
		).limit_length(1.0)
```

The way this works is that if we are running training or inference with a RL agent, the `set_action` method will be
called
with action values provided. However, during demo recording, `set_acation` will be called without any action provided,
so we need
to manually set the values.

> [!NOTE]
> `set_action()` will be called just before `get_action()`, so the demo recorder will record the currently applied
> action
> for the current state/observations.

Now we can simplify the heuristic handling code (for when "human control" mode is used) in robot.gd.

#### Open `robot.gd`

Change the `handle_movement` method to the following code:

```gdscript
func handle_movement(delta):
	var movement := Vector3()

	if ai_controller.heuristic == "human":
		ai_controller.set_action()

	movement = requested_movement

	apply_acceleration(movement, delta)
	apply_gravity(delta)
	apply_friction(delta)
	apply_conveyor_belt_velocity(delta)
	limit_horizontal_speed()

	move_and_slide()

	rotate_toward_movement(delta)
	update_wheels_and_visual_rotation(delta)
```

Let's also set the game to only use the last level. This will simplify the demo recording and training for this
tutorial.

Find the `reset()` method and change it to:

```gdscript
func reset():
	current_level = 7
	velocity = Vector3.ZERO
	global_position = level_manager.get_spawn_position(current_level)
	current_goal_transform = level_manager.randomize_goal(current_level)
	previous_distance_to_goal = global_position.distance_to(current_goal_transform.origin)
```

#### Record some demos

To record demos, press `F6` or click on `Run Current Scene`.

Record some demos of successfully completing the level. You can use the key previously set for removing the last episode
if the robot hits an enemy or falls down during recording.

Here's a highly sped-up video of recording 18 episodes:

https://github.com/edbeeching/godot_rl_agents/assets/61947090/7bdc19ba-6e88-431d-b87b-7ec3e0ce1a7c

> [!NOTE]
> I found it difficult to control the robot with action repeat 10, and I removed a few episodes where the robot hit
> an enemy robot during recording so that they don't end up in the recorded demos file. I would recommend setting action
> repeat to a lower value like 6-8 (both in AIController and sync node in the two scenes mentioned previously).
> Another way to make this easier is to drag the sync.gd script to Sync node in both training and testing scene.
> An extended sync script is set in this example which set uses a 30 ticks per second physics setting, which is not
> ideal for manual control.
> It's also possible to change the `speed up` property of the `sync` node while recording demos to make the process
> easier, as it
> will slow down or speed up the game according to the setting.

Once you are done recording, click on `x` to close the game window (do not use the `Stop` button in the editor as that
will not save the file), and you will see `demo.json` in the filesystem.

#### Export the game

Click on `Project` > `Export` and export the game for your current OS. We will use the exported game for training.

#### Open conda terminal or venv terminal:

I use conda in this example, but you can use the corresponding commands with venv or the system that you are using for
managing Python environments.

#### Type `conda activate gdrl_il`

(replace gdrl_il with the name you're using for the virtual env, it should have godot rl agents and imitation library
installed)

#### Move to the folder with the Imitation Learning Example

Download the [sb3 imitation example](/examples/sb3_imitation.py) and `cd` into the folder where the file is.

#### Set the arguments and start the training

E.g. on Windows:

````
python sb3_imitation.py --env_path="PATH_TO_EXPORTED_GAME_EXE_FILE_HERE" --il_timesteps=250_000 --demo_files="PATH_TO_THE_RECORDED_demo.json_FILE_HERE" --eval_episode_count=20 --n_parallel=5 --speedup=15
````

Training should begin. As we set a small amount of timesteps, the results won't be perfect, but it shouldn't take too
long (may still take a while, you can reduce the timesteps if you wish to run a quick test). Beside increasing
timesteps, you can open the scripta and modify the hyperaparameters to get better results. Having more high quality
recorded demos can help too. You can load multiple files by adding them to the `--demo_files` argument,
e.g. `--demo_files="file1_path" "file2_path" "file3_path"`.
After the training is done, an evaluation environment should open, and you will see the trained agent solving the env
for
20 episodes.

In my case, I got:
```Mean reward after evaluation: 5.906429767608643```
The exact results you get may be different for various reasons, including the possibility that the hyperparameters
and/or other variables may have changed since then.

For comparison, when training just with `--rl_timesteps=250_000` I got a reward of:
```Mean reward after evaluation: 9.194426536560059```

The imitation-learned reward could be improved by tweaking hyperaparameters (the parameters provided in the script are
not optimized), recording more high quality demos, doing some RL timesteps after it, etc.
As this environment was designed and tested with PPO RL, in this case the environment is simple enough that PPO alone
can learn it quickly from the reward function and imitation learning isn't necessary.
However, in more complex environments where it might be difficult to define a good dense reward function, learning from
demonstrations and/or combining it with RL learning from sparse rewards could be helpful.

There are a couple of other options to mention:

After imitation learning, you can continue model training with PPO using the environment rewards to further improve the
results. This is done by adding an argument to the script, e.g. `--rl_timesteps=250_000`.

You can set the script to export the trained model to onnx by adding e.g. `--onnx_export_path="model.onnx"`. That model
can be then be copied to the game folder, and set in sync node in testing_scene to be used for inference without the
Python server.
