extends KinematicBody
 
const MOVE_SPEED = 12
const JUMP_FORCE = 30
const GRAVITY = 0.98
const MAX_FALL_SPEED = 30
 
const LOOK_SENS = 1.0
 
onready var cam = $Camera
var move_vec = Vector3()
var y_velo = 0

# RL related variables
onready var end_position = $"../EndPosition"
onready var raycast_sensor = $"RaycastSensor"
var done = false
var just_reached_end = false
var just_fell_off = false
var best_goal_distance = 10000.0
var grounded
var _heuristic = "player"
var move_action = 0
var jump_action = false

func _ready():
    reset()

func _physics_process(delta):
    
#    if Input.is_action_pressed("move_forwards"):
#        move_vec.z -= 1
#    if Input.is_action_pressed("move_backwards"):
#        move_vec.z += 1
#    if Input.is_action_pressed("move_right"):
#        move_vec.x += 1
#    if Input.is_action_pressed("move_left"):
#        move_vec.x -= 1    
#    if Input.is_action_pressed("turn_right"):
#        rotation_degrees.y -= LOOK_SENS
#    if Input.is_action_pressed("turn_left"):
#        rotation_degrees.y += LOOK_SENS
    move_vec *= 0
    move_vec = get_move_vec()
    move_vec = move_vec.normalized()
    move_vec = move_vec.rotated(Vector3(0, 1, 0), rotation.y)
    move_vec *= MOVE_SPEED
    move_vec.y = y_velo
    move_and_slide(move_vec, Vector3(0, 1, 0))
 
    grounded = is_on_floor()
    y_velo -= GRAVITY
    var just_jumped = false
    if grounded and get_jump_action():
        just_jumped = true
        y_velo = JUMP_FORCE
    if grounded and y_velo <= 0:
        y_velo = -0.1
    if y_velo < -MAX_FALL_SPEED:
        y_velo = -MAX_FALL_SPEED
    
    if Input.is_action_just_pressed("r_key"):
        reset()

func get_move_vec() -> Vector3:
    if done:
        move_vec = Vector3.ZERO
        return move_vec
        
    if _heuristic == "model":
        return Vector3(
        0,
        0,
        move_action
    )
        
    var move_vec := Vector3(
        0,
        0,
        Input.get_action_strength("move_backwards") - Input.get_action_strength("move_forwards")
    )
    
    return move_vec

func get_jump_action() -> bool:
    if done:
        jump_action = false
        return jump_action
        
    if _heuristic == "model":
        return jump_action  
    
    return Input.is_action_just_pressed("jump")
  
func reset():
    done = false
    just_reached_end = false
    just_fell_off = false
    jump_action = false
     # Replace with function body.
    set_translation(Vector3(0,5,0))
    y_velo = 0.1
    best_goal_distance = translation.distance_to(end_position.translation)
    
func set_action(action):
    move_action = action["move"][0]
    jump_action = action["jump"] == 1
    
func reset_if_done():
    if done:
        reset()

func get_obs():
    var obs = []
    obs.append_array([move_vec.x/MOVE_SPEED,
                      move_vec.y/MAX_FALL_SPEED,
                      move_vec.z/MOVE_SPEED])
    #obs.append_array([translation.x,translation.y,translation.z])
    obs.append(grounded)
    obs.append_array(raycast_sensor.get_raycast_buffer())
    
    return obs

func get_reward():
    var reward = 0.0
    reward -= 0.01 # step penalty
    if just_reached_end:
        reward += 10.0
        just_reached_end = false
    
    if just_fell_off:
        reward -= 10.0
        just_fell_off = false
    
    reward += shaping_reward()
    return reward
    
func shaping_reward():
    var s_reward = 0.0
    var goal_distance = translation.distance_to(end_position.translation)
    
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
        "move" : {
             "size": 1,
            "action_type": "continuous"
           },
        "jump": {
            "size": 2,
            "action_type": "discrete"
           }
       }

func get_done():
    return done

func _on_Area_body_entered(body):
    done = true
    just_fell_off = true
    #reset_if_done()

func _on_EndTrigger_body_entered(body):
    done = true
    just_reached_end = true
    #reset_if_done()
