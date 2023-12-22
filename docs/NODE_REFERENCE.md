# Node reference

This page will provide basic information on the properties and usage of the nodes available in
the [Godot RL Agents Plugin](https://github.com/edbeeching/godot_rl_agents_plugin).

> [!NOTE]
> If you don't have Godot and the Godot-RL plugin installed, check these two sections of the custom environment tutorial
> first: [Installing Godot](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#installing-the-godot-game-engine), [Installing the plugin](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#installing-the-godot-rl-agents-plugin).
> To make sure you have the latest features, you can use the plugin from the GitHub repository (linked above).

## AIController Node

There are two variants of the AIController node available (2D and 3D).

You can find instructions on how to use the AIController node in the custom env
tutorial: [Adding the AI Controller](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#adding-the-ai-controller).

### Properties:

#### Reset After:

![Reset after](https://github.com/edbeeching/godot_rl_agents/assets/61947090/9ca2a36e-11e5-4199-b1f6-11a9f0b6fdef)

Once the number of steps has passed, the flag `needs_reset` will be set to `true` for this instance. Then, you can handle
the restart of the agent and any other parts of the scene that may need to be restarted.

Other than the flag being set to `true`, the restart will not happen automatically. This needs to be handled either
through the AIController node or through another node (e.g. the Player node), as done in the custom environment
tutorial:

```gdscript
func _physics_process(delta):
	if ai_controller.needs_reset:
		ai_controller.reset()
		ball.reset()
		return
```

`needs_reset` is also set to `true` manually (along with `done`) when finishing the episode due to e.g. game over
conditions.
Calling `ai_controller.reset()` will set it to `false` and reset the `AIController`'s internal step counter to 0.

#### How to disable the time-out reset:

In case you wish to disable the automatic restarting, and setting a very large number of steps is not sufficient, in
your
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

## Sync Node

This is the main node that controls training and inference (using the trained model).

### Properties:

#### Control Mode:

There are three modes:

- Training - will start training when you click `Play` in Godot editor (or use the exported application as `--env_path`
  in training).

> [!NOTE]
> For training to work, you need
> to [install Godot-RL](https://github.com/edbeeching/godot_rl_agents#installation-and-first-training) and start the
> training server using `gdrl`, or, to have the ability to save the model after training is done, using
> the [sb3 example script](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/ADV_STABLE_BASELINES_3.md#sb3-example-script-usage).

- Human - `ai_controller.heuristic` will be set to `"human"`. You can use this to test the environment by manually
  controlling the agent, e.g. as implemented in
  the [custom env tutorial](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#adding-the-ai-controller):

```gdscript
	var movement : float
	if ai_controller.heuristic == "human":
		movement = Input.get_axis("rotate_anticlockwise", "rotate_clockwise")
	else:
		movement = ai_controller.move_action
```

- Onnx Inference - once you have finished training
  and [exported an onnx file of the model](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/ADV_STABLE_BASELINES_3.md#train-a-model-for-100_000-steps-then-save-and-export-the-model),
  you can use it for inference from Godot without using the Python server. It needs Godot with C#/net
  support and `.csproj` file to work,
  check [onnx inference error](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/TROUBLESHOOTING.md#onnx-inference-error).

#### Action Repeat:

Every n steps as set by action repeat, the Godot agent will send the observations, rewards, and dones info to the Python server,
and receive the actions from the Python server.
By not doing this on every step, training can potentially be faster as there is less data to process. Running the
environment can also be faster as data is exchanged less frequently. Some calculations, e.g. for the RayCast sensors,
are also done less frequently.

#### Speed Up:

Speeds the physics up in the environments to enable faster training.

#### Onnx Model Path:

The path to a trained .onnx model file to use for inference (only needed for the `Onnx Inference` control mode).

## Sensors

### RayCastSensor

There are two variants of the RayCast Sensor (2D and 3D).

The sensor can be used to add information about the objects in the environment to the agent.

![RayCastSensorExample](https://github.com/edbeeching/godot_rl_agents/assets/61947090/af4d5cd7-6d45-4c58-96fb-76e0a06007ab)

Multiple [examples](https://github.com/edbeeching/godot_rl_agents_examples/tree/main/examples) use this sensor (e.g.
BallChase, 3DCarParking, and others).

#### Properties of the 3D version:

![3D Raycast Sensor](https://github.com/edbeeching/godot_rl_agents/assets/61947090/a09416b2-c289-4aa2-8c5a-f2baafccb73a)

##### Collision Mask:

The rays from the raycast sensor will detect the objects in these physics layers.
> [!TIP]
> You can make multiple raycast sensors, with different collision masks, to detect different object types (e.g. one for
> walls, one for collectibles, and one for avoidables).

##### Boolean Class Mask:

If you enable `Class Sensor`, this will differentiate in the observations returned whether the object that was hit by a
ray is both in one of the layers from the collision mask and one of the layers from the boolean class mask. You could
use this to differentiate from two different object groups (e.g. wall or coin).

##### N Rays Width:

How many rays to add to the cone of rays (width).

##### N Rays Height:

How many rays to add to the cone of rays (height).

##### Ray Length:

Length of the rays.

##### Cone Width:

Width of the cone.

##### Cone Height:

Height of the cone.

##### Collide with areas:

Whether the raycasts from the sensor should collide with areas.

##### Collide with bodies:

Whether the raycasts from the sensor should collide with bodies.

##### Class sensor:

Whether two classes should be differentiated (check [Boolean Class Mask](#boolean-class-mask)).

#### Properties that are different in the 2D version:

2D Version doesn't have the class sensor related options.

##### N Rays:

Total number of rays.

##### Debug Draw:

Whether to visualize the rays.

### GridSensor

The GridSensor also comes in two variants (2D and 3D).
This sensor uses a grid of area nodes, allowing the agent to collect information about various objects from multiple
categories (e.g. collectibles, avoidables, walls, etc.).

Check out the [Ships](https://github.com/edbeeching/godot_rl_agents_examples/tree/main/examples/Ships) example that uses
this sensor:

![Grid Sensor used in Ships example](https://github.com/edbeeching/godot_rl_agents/assets/61947090/4dab95b6-1e48-41cc-807b-bf950317c64b)

#### Properties of the 3D version

![Grid Sensor 3D Properties](https://github.com/edbeeching/godot_rl_agents/assets/61947090/399c3230-15b7-4eed-9c63-0eb8ca4ba24d)

##### Debug View:

Whether to display the grid and detected collisions in the game/environment.

##### Detection Mask:

Will detect objects that are in the selected physics layers.
Use different layers for different object categories (e.g. one layer for collectibles, another layer for avoidables).

##### Collide with Areas:

Whether to detect areas.

##### Collide with Bodies:

Whether to detect bodies.

##### Cell Width:

The width of each cell in the grid.

##### Cell Height:

The width of each cell in the grid.

##### Grid Size X:

The number of cells in the grid along the X axis.

##### Grid Size Z:

The number of cells in the grid along the Z axis.

#### Properties of the 2D version

Same as the 3D version, except that grid size axes are X and Y.

### CameraSensor

Enables the agent to get observations rendered by a camera. Check out
the [Virtual Camera](https://github.com/edbeeching/godot_rl_agents_examples/tree/main/examples/VirtualCamera) example
that uses it.
