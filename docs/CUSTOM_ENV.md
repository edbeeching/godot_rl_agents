# Creating Custom Environments with Godot RL Agents
(please ensure you have install the library and have run the examples before following this tutorial)

In this section, you will learn how to create a custom environment in the Godot Game Engine and then implement an AI controller that learns to play with Deep Reinforcement Learning. The example game we create today is simple, but shows off many of the features of the Godot Engine and the Godot RL Agents library. You can then dive into the examples for more complex environments and behaviors. 

The environment we will be building today is called Ring Pong, the game of pong but the pitch is a ring and the paddle moves around the ring. The objective is to keep the ball bouncing inside the ring. The video below shows and example policy that has learned to play this game using Deep RL, you should achieve similar results by the end of this chapter.

https://user-images.githubusercontent.com/7275864/222367265-b0ca1f91-3ae2-4f43-b775-d6ed1d7e2f0b.mp4

## Installing the Godot Game Engine

The Godot game engine is an open source tool for the creation of video games, tools and user interfaces. 

Godot Engine is a feature-packed, cross-platform game engine designed to create 2D and 3D games from a unified interface. It provides a comprehensive set of common tools, so users can focus on making games without having to reinvent the wheel. Games can be exported in one click to a number of platforms, including the major desktop platforms (Linux, macOS, Windows) as well as mobile (Android, iOS) and web-based (HTML5) platforms.

While we will guide you through the steps to implement your agent, you may wish to learn more about the Godot Game Engine. Their [documentation](https://docs.godotengine.org/en/latest/index.html) is thorough, there are many tutorials on YouTube we would also recommend [GDQuest](https://www.gdquest.com/), [KidsCanCode](https://kidscancode.org/godot_recipes/4.x/) and [Bramwell](https://www.youtube.com/channel/UCczi7Aq_dTKrQPF5ZV5J3gg) as sources of information.

In order to create games in Godot, you must first download the editor. The latest version of Godot RL Agents supports the recently released Godot 4.0. Available on the [Godot Website](https://godotengine.org/).

## Loading the starter project

We provide two versions of the codebase. 

- [A starter project, to download and follow along for this tutorial](https://drive.google.com/file/d/1C7xd3TibJHlxFEJPBgBLpksgxrFZ3D8e/view?usp=share_link)
- [A final version of the project, for comparison and debugging.](https://drive.google.com/file/d/1k-b2Bu7uIA6poApbouX4c3sq98xqogpZ/view?usp=share_link)

To load the project, in the Godot Project Manager click **Import**, navigate to where the files are located and load the **project.godot** file.

If you press F5 or play in the editor, you should be able to play the game in human mode. There are several instances of the game running, this is because we want to speed up training our AI agent with many parallel environments.

## Installing the Godot RL Agents plugin

The Godot RL Agents plugin can be installed from the Github repo or with the Godot Asset Lib in the editor.

First click on the AssetLib and search for “rl”

![addon](https://user-images.githubusercontent.com/7275864/222365663-c6d0527a-6099-48f4-a52a-5f164769705c.png)

Then click on Godot RL Agents, click Download and unselect the LICENSE and README.md files. Then click install.

![addon_load](https://user-images.githubusercontent.com/7275864/222365688-81bb9ef8-fffe-4eda-b1a4-c05ca0a801c8.png)

The Godot RL Agents plugin is now downloaded to your machine your machine. Now click on Project → Project settings and enable the addon:

![addon_enable](https://user-images.githubusercontent.com/7275864/222365708-7ff088c6-13c1-45a3-bc83-6b9075ef3430.png)

## Adding the AI controller

We now want to add an AI controller to our game. Open the player.tscn scene, on the left you should see a hierarchy of nodes that looks like this:

![ai_controller](https://user-images.githubusercontent.com/7275864/222365744-0f57c49c-8bd0-4b24-a6e1-346337e83e76.png)

Right click the **Player** node and click **Add Child Node.** There are many nodes listed here, search for AIController3D and create it. 

![ai_controller_node](https://user-images.githubusercontent.com/7275864/222366065-ab014718-1db4-4149-a245-b04b7899824f.png)

The AI Controller Node should have been added to the scene tree, next to it is a scroll. Click on it to open the script that is attached to the AIController. The Godot game engine uses a scripting language called GDScript, which is syntactically similar to python. The script contains methods that need to be implemented in order to get our AI controller working.

```python
#-- Methods that need implementing using the "extend script" option in Godot --#
func get_obs() -> Dictionary:
	assert(false, "the get_obs method is not implemented when extending from ai_controller") 
	return {"obs":[]}

func get_reward() -> float:	
	assert(false, "the get_reward method is not implemented when extending from ai_controller") 
	return 0.0
	
func get_action_space() -> Dictionary:
	assert(false, "the get get_action_space method is not implemented when extending from ai_controller") 
	return {
		"example_actions_continous" : {
			"size": 2,
			"action_type": "continuous"
		},
		"example_actions_discrete" : {
			"size": 2,
			"action_type": "discrete"
		},
		}
	
func set_action(action) -> void:	
	assert(false, "the get set_action method is not implemented when extending from ai_controller") 	
# -----------------------------------------------------------------------------#
```

In order to implement these methods, we will need to create a class that inherits from AIController3D. This is easy to do in Godot, and is called “extending” a class.

Right click the AIController3D Node and click “Extend Script” and call the new script `controller.gd`. You should now have an almost empty script file that looks like this:

```python
extends AIController3D

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
```

We will now implement the 4 missing methods, delete this code and replace it with the following:

```python
extends AIController3D

# Stores the action sampled for the agent's policy, running in python
var move_action : float = 0.0

func get_obs() -> Dictionary:
	# get the balls position and velocity in the paddle's frame of reference
	var ball_pos = to_local(_player.ball.global_position)
	var ball_vel = to_local(_player.ball.linear_velocity)
	var obs = [ball_pos.x, ball_pos.z, ball_vel.x/10.0, ball_vel.z/10.0]

	return {"obs":obs}

func get_reward() -> float:	
	return reward
	
func get_action_space() -> Dictionary:
	return {
		"move_action" : {
			"size": 1,
			"action_type": "continuous"
		},
		}
	
func set_action(action) -> void:	
	move_action = clamp(action["move_action"][0], -1.0, 1.0)
```

We have now defined the agent’s observation, which is the position and velocity of the ball in its local coordinate space. We have also defined the action space of the agent, which is a single continuous value ranging from -1 to +1.

The next step is to update the Player’s script to use the actions from the AIController, edit the Player’s script by clicking on the scroll next to the player node, update the code in `Player.gd` to the following the following:

```python
extends Node3D

@export var rotation_speed = 3.0
@onready var ball = get_node("../Ball")
@onready var ai_controller = $AIController3D

func _ready():
	ai_controller.init(self)

func game_over():
	ai_controller.done = true
	ai_controller.needs_reset = true

func _physics_process(delta):
	if ai_controller.needs_reset:
		ai_controller.reset()
		ball.reset()
		return
		
	var movement : float
	if ai_controller.heuristic == "human":
		movement = Input.get_axis("rotate_anticlockwise", "rotate_clockwise")
	else:
		movement = ai_controller.move_action
	rotate_y(movement*delta*rotation_speed)

func _on_area_3d_body_entered(body):
	ai_controller.reward += 1.0
```

We now need to synchronize between the game running in Godot and the neural network being trained in Python. Godot RL agents provides a node that does just that. Open the train.tscn scene, right click on the root node and click “Add child node”. Then, search for “sync” and add a Godot RL Agents Sync node. This node handles the communication between Python and Godot over TCP. 

You can run training live in the the editor, by first launching the python training with:
```
gdrl
```
alternatively you can move to the `godot_rl_agents-main` folder in the console (you can download it from the repository), and then type:
```
python examples/clean_rl_example.py
```



In this simple example, a reasonable policy is learned in several minutes. You may wish to speed up training, click on the Sync node in the train scene and you will see there is a “Speed Up” property exposed in the editor:

![action_repeat](https://user-images.githubusercontent.com/7275864/222365882-0a9dba16-102c-4326-acb1-0448459ed884.png)

Try setting this property up to 8 to speed up training. This can be a great benefit on more complex environments, such as the FPS environment available in the examples.

NOTE: If you receive an error `Invalid get index '0' (on base: 'Array[Node]')` click on `AIController3D` and add an `AGENT` group by clicking on `Node`, clicking on `Groups`, typing in `AGENT` and clicking `Add` to add the new group.

![adding_new_group](https://user-images.githubusercontent.com/7275864/230909061-d4eae2ce-e13f-4d6e-858f-a08691635442.png)

### Adding sensors to your agent  (Optional depending on your custom environment) 
We provide a number of sensors nodes that can be added to your agent called RayCastSensor2D and RayCastSensor3D. The videos below show an overview.

https://user-images.githubusercontent.com/7275864/209363084-f91b2fcb-2042-494c-9c62-53eb4954d62b.mp4

https://user-images.githubusercontent.com/7275864/209363098-a6bee0a6-dc85-4b8d-b69a-d747bcf39635.mp4

## There’s more!

We have only scratched the surface of what can be achieved with Godot RL Agents, the library includes custom sensors and cameras to enrich the information available to the agent. Take a look at the [examples](https://github.com/edbeeching/godot_rl_agents_examples) to find out more!


