# Node reference

This page will provide basic information on the properties and usage of the nodes available in
the [Godot RL Agents Plugin](https://github.com/edbeeching/godot_rl_agents_plugin).

> [!NOTE]
> If you don't have Godot and the Godot-RL plugin installed, check these two sections of the custom environment tutorial
> first: [Installing Godot](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#installing-the-godot-game-engine), [Installing the plugin](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#installing-the-godot-rl-agents-plugin).
>
> To make sure you have the latest features, you can use the plugin from the Github repository (linked above).

## AIController Node

There are two variants of the AIController node available (2D and 3D):

![AI Controller Node Variants](https://github.com/edbeeching/godot_rl_agents/assets/61947090/bbd7a57f-dbce-47e6-a4dc-76da43da1edc)


### Common usage:

You can find instructions on how to use the AIController node in the custom env
tutorial: [Adding the AI Controller](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#adding-the-ai-controller).

### Properties:

#### Reset After:

![Reset after](https://github.com/edbeeching/godot_rl_agents/assets/61947090/9ca2a36e-11e5-4199-b1f6-11a9f0b6fdef)


Once the number of steps has passed, the flag `needs_reset` will be set to true for this instance. Then, you can handle
the restart of the agent and any other parts of the scene that may need to be restarted.

Other than the flag being set to true, the restart will not happen automatically. This needs to be handled either
through the AIController node or through another node (e.g. the Player node), as done in the custom environment
tutorial:

```gdscript
func _physics_process(delta):
	if ai_controller.needs_reset:
		ai_controller.reset()
		ball.reset()
		return
```

`needs_reset` is also set to `true` manually (along with `done`) when finishing the episode due to e.g. game over conditions.
Calling `ai_controller.reset()` will set it to `false` and reset the `AIController`'s internal step counter to 0.

#### How to disable the time-out reset:

In case you wish to disable the automatic restarting, and setting a very large number of steps is not sufficient, in your
extended AIController script (check
the [custom env tutorial](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#adding-the-ai-controller)
if you're not sure how to extend the script), you can override the `_physics_process` method to disable the behavior,
e.g.

```gdscript
func _physics_process(delta):
	n_steps += 1 # Keeps counting steps, but will not set needs_reset
```

> [!WARNING]
> In case some other functionality is added to `_physics_process` of the AIController base class script in the future,
> this override may break the functionality.

> [!NOTE]
> Some statistics during training such as `mean episode reward` and `mean episode length` may not appear if no episodes
> have ended. 
