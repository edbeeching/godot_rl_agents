extends KinematicBody

# Maximum airspeed
var max_flight_speed = 30
# Turn rate
export var turn_speed = 5.0
export var level_speed = 12.0
export var turn_acc = 4.0
# Climb/dive rate
var pitch_speed = 2.0
# Wings "autolevel" speed
# Throttle change speed
var throttle_delta = 30
# Acceleration/deceleration
var acceleration = 6.0
# Current speed
var forward_speed = 0
# Throttle input speed
var target_speed = 0

var velocity = Vector3.ZERO
var found_goal = false
var exited_arena = false
var cur_goal = null
onready var environment = get_parent()
# ------- #
var turn_input = 0
var pitch_input = 0
var done = false
var _heuristic = "human"
var best_goal_distance := 10000.0
var transform_backup = null
var n_steps = 0
const MAX_STEPS = 200000

func _ready():
    transform_backup = transform
    pass
    
func reset():
    cur_goal = environment.get_next_goal(null)
    transform_backup = transform_backup
    translation.x = 0 + rand_range(-2,2)
    translation.y = 27 + rand_range(-2,2)
    translation.z = 0 + rand_range(-2,2)
    velocity = Vector3.ZERO
    rotation = Vector3.ZERO
    n_steps = 0
    found_goal = false
    exited_arena = false 
    done = false
    best_goal_distance = to_local(cur_goal.translation).length()
    # reset position, orientation, velocity

func reset_if_done():
    if done:
        reset()

func get_obs():
    if cur_goal == null:
        reset()
    #var goal_vector = (cur_goal.translation - translation).normalized() # global frame of reference
    var goal_vector = to_local(cur_goal.translation)
    var goal_distance = goal_vector.length()
    goal_vector = goal_vector.normalized()
    goal_distance = clamp(goal_distance, 0.0, 50.0)
    
    var next_goal = environment.get_next_goal(cur_goal)
    var next_goal_vector = to_local(next_goal.translation)
    var next_goal_distance = next_goal_vector.length()
    next_goal_vector = next_goal_vector.normalized()
    next_goal_distance = clamp(next_goal_distance, 0.0, 50.0)  

    var obs = [
        goal_vector.x,
        goal_vector.y,
        goal_vector.z,
        goal_distance / 50.0 ,
        next_goal_vector.x,
        next_goal_vector.y,
        next_goal_vector.z,
        next_goal_distance / 50.0
       ]
    
    return obs

func get_reward():
    var reward = 0.0
    reward -= 0.01 # step penalty
    if found_goal:
        reward += 100.0
        found_goal = false 
    if exited_arena:
        reward -= 10.0
        exited_arena = false
    
    reward += shaping_reward()
    return reward
    
func shaping_reward():
    var s_reward = 0.0
    var goal_distance = to_local(cur_goal.translation).length()
    if goal_distance < best_goal_distance:
        s_reward += best_goal_distance - goal_distance
        best_goal_distance = goal_distance
        
    s_reward /= 1.0
    return s_reward 

func set_heuristic(heuristic):
    self._heuristic = heuristic

func get_obs_size():
    return len(get_obs())
   
func get_action_space():
    return {
        "turn" : {
             "size": 1,
            "action_type": "continuous"
           },        
        "pitch" : {
             "size": 1,
            "action_type": "continuous"
           }
       }

func get_done():
    return done

func set_action(action):
    turn_input = action["turn"][0]
    pitch_input = action["pitch"][0]

func _physics_process(delta):
    if cur_goal == null:
        reset()
    set_input()
    if Input.is_action_just_pressed("r_key"):
        reset()
    # Rotate the transform based on the input values
    transform.basis = transform.basis.rotated(transform.basis.x.normalized(), pitch_input * pitch_speed * delta)
    transform.basis = transform.basis.rotated(Vector3.UP, turn_input * turn_speed * delta)
    $PlaneModel.rotation.z = lerp($PlaneModel.rotation.z, turn_input, level_speed * delta)
    $PlaneModel.rotation.x = lerp($PlaneModel.rotation.x, pitch_input, level_speed * delta)

    # Movement is always forward
    velocity = -transform.basis.z.normalized() * max_flight_speed
    # Handle landing/taking off
    move_and_slide(velocity, Vector3.UP)
    n_steps += 1
    if n_steps > MAX_STEPS:
        done = true
        
func set_input():
    if _heuristic == "model":
        return
    else:
        turn_input = Input.get_action_strength("roll_left") - Input.get_action_strength("roll_right")
        pitch_input = Input.get_action_strength("pitch_up") - Input.get_action_strength("pitch_down")


func goal_reached(goal):
    if goal == cur_goal:
        found_goal = true
#        if goal ==  environment.get_last_goal():
#            done = true
        cur_goal = environment.get_next_goal(cur_goal)
    
func exited_game_area():
    done = true
    exited_arena = true
