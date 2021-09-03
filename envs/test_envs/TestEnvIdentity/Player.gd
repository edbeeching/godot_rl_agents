extends Node


var done 
var state = 0
var _action = 0
var n_steps = 0
var _heuristic = "human"

func _ready():
    reset()

func _physics_process(delta):
    state += (_action % 2)
    state %= 3
    n_steps += 1
    
    if n_steps > 10:
        done = true

func reset():
    done = false
    state = 0
    n_steps = 0
    
func set_action(action):
    _action = int(action["action"])
    
    
func reset_if_done():
    if done:
        reset()

func get_obs() -> Array:
    var obs = [0.0,0.0,0.0]
    obs[state] = 1.0
    
    return obs

func get_reward() -> float:
    return float(_action == state)*0.1
    
     
func get_action_space():
    return {
        "action" : {
             "size": 3,
            "action_type": "discrete"
           }
       }

func get_obs_size():
    return len(get_obs())
     
func set_heuristic(heuristic):
    self._heuristic = heuristic
    
func get_done():
    return done
