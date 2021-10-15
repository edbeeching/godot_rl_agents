
# Custom Environment Creation
**NOTE:** These instructions will be subject to large improvements based on the community feedback. If any aspect is not clear or you struggle at all, please raise an issue on github and we will try to improve it.
****

## Instructions

### Create your game
Before following any instructions, create your primary game scene (without the menus etc) and play it under human control to ensure everything works as expected.

### Install the Godot RL Agents plugin
To interface between the Godot game executable or editor we have implemented a small plugin which is located in the plugin/addons/godot_rl_agents directory. Copy the plugin directory to your addons directory within your game project. For more infomation on plugins see this [page](https://docs.godotengine.org/en/stable/tutorials/plugins/editor/installing_plugins.html).

Once the plugin is installed, a new node is available called "sync" which you will need to attach to the root node of you scene.
### Interaction between Python and Godot
In the script for controlling the player, or another node if that is more convenient. The node that owns this script will need to be added to the group "AGENT". You will then need to add the following variables and functions:

```
var _heuristic := "player"
var done = false
# example actions
var move_action
var turn_action
var jump_action


func reset():
    # The reset logic e.g reset if a player dies etc, reset health, ammo, position, etc ...
    pass

func reset_if_done():
    if done:
        reset()

func get_obs():
# The observation of the agent, think of what is the key information that is needed to perform the task, try to have things in coordinates that a relative to the play
    pass

func get_reward():
    reward = 0
    # What behavior do you want to reward, kills? penalties for death, key waypoints
    return return + shaping_reward()

func shaping_reward():
    # can a sparse reward like kills, death be broken down into denser rewards such as hits taken/given, or distance from the target
    pass


func set_heuristic(heuristic):
    # sets the heuristic from "human" or "model" nothing to change here
    self._heuristic = heuristic

func get_obs_size():
    # nothing to change here
    return len(get_obs())
   
func get_action_space():
    # Define the action space of you agent, below is an example, GDRL allows for discrete and continuous state spaces (assuming the RL algorithm allows it)
    return {
        "move" : {
             "size": 1,
            "action_type": "continuous"
           },        
        "turn" : {
             "size": 1,
            "action_type": "continuous"
           },
        "discrete1": {
            "size": 2,
            "action_type": "discrete"
           }
       }

func get_done():
    # nothing to change here
    return done


func set_action(action):
    # reads off the actions sent from the RL model to the agent
    # the keys here should match the dictionary keys in the "get_action_space" function
    move_action = action["move"][0]
    turn_action = action["turn"][0]
    jump_action = action["jump"] == 1

```

Once these functions have been implemented, and the [installation instructions](../docs/INSTALLATION.md) have been followed, you can run "gdrl" inside the terminal to start an interative training of Godot RL Agents. You can now press play in the editor to watch you agent train. 


### Parallel agents
To speed up traning, it is worthwhile creating multiple versions of your agent and game scene. It is best to refer to the example projects to learn how to do this.
### Outputting an executable.

While training in the editor is possible, training can be parallized with multiple executables running in parallel. You can export you project and run training

```
gdrl --env_path ENV_NAME
```

This will use the default PPO training algorithm and a set of default parameters which are a reasonable starting point for learning an agent behavior. If you wish you can make a copy of the config file and modify it. Call the following to perform training.

```
gdrl --env_path ENV_NAME --config_path CUSTOM_CONFIG.yaml
```

### Hyperparameters 
There are many parameters that control how well you RL agent will perform. Before tuning any of these, make sure that your observation and reward functions are the most logical for the task you wish to learn. Deep RL training is challenging and without the correct reward function and observation, your agent will likely not learning the desired behavior.

Once you have validated that the observation and the reward are the best they can be, we recommend testing the following parameters: 
* Entropy factor: This balances exploration: Test values of 0.01, 0.001, 0.0001
* Gamma: Is there a long time delay between an action and the associated reward? Then try increasing gamma to 0.99
* FC hiddens: the size of your network, smaller networks are easier to train and may be fine for simple problems. Test [16, 16], [64, 64], [256, 256], [1024, 1024]
* If you see warnings about the VF clip param in the terminal, try raising it.

