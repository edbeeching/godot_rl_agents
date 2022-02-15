extends KinematicBody
class_name Player
const MOVE_SPEED = 12
const JUMP_FORCE = 30
const GRAVITY = 0.98
const MAX_FALL_SPEED = 30
const TURN_SENS = 2.0
const MAX_STEPS = 10000
 
onready var cam = $Camera
var move_vec = Vector3()
var y_velo = 0

# RL related variables
onready var robot = $Robot
onready var virtual_camera = $VirtualCamera

var next = 1
var done = false
var needs_reset = false
var just_reached_negative = false
var just_reached_positive = false
var just_fell_off = false
var best_goal_distance := 10000.0
var grounded := false
var _heuristic := "player"
var move_action := 0.0
var turn_action := 0.0
var jump_action := false
var n_steps = 0

func _ready():
    return
    #reset()

func _physics_process(_delta):

    if needs_reset:
        needs_reset = false
        reset()
        return
    
    move_vec *= 0
    move_vec = get_move_vec()
    #move_vec = move_vec.normalized()
    
    move_vec = move_vec.rotated(Vector3(0, 1, 0), rotation.y)
    move_vec *= MOVE_SPEED
    move_vec.y = y_velo
    move_and_slide(move_vec, Vector3(0, 1, 0))
    
    # turning
    
    var turn_vec = get_turn_vec()
    rotation_degrees.y += turn_vec*TURN_SENS
 
    grounded = is_on_floor()

    y_velo -= GRAVITY
    var just_jumped = false

    if grounded and y_velo <= 0:
        y_velo = -0.1
    if y_velo < -MAX_FALL_SPEED:
        y_velo = -MAX_FALL_SPEED
    
    if y_velo < 0 and !grounded :
        robot.set_animation("falling-cycle")
    
    var horizontal_speed = Vector2(move_vec.x, move_vec.z)
    if horizontal_speed.length() < 0.1 and grounded:
        robot.set_animation("idle")
    elif horizontal_speed.length() >=1.0 and grounded:
        robot.set_animation("walk-cycle")    
#    elif horizontal_speed.length() >= 1.0 and grounded:
#        robot.set_animation("run-cycle")
    
    if Input.is_action_just_pressed("r_key"):
        reset()
        
    n_steps +=1
        
    if n_steps >= MAX_STEPS:
        done = true
     
    
    #reset_if_done()

func get_move_vec() -> Vector3:
    if done:
        move_vec = Vector3.ZERO
        return move_vec
    
    if _heuristic == "model":
        return Vector3(
        0,
        0,
        clamp(move_action, -1.0, 0.5)
    )
        
    var move_vec := Vector3(
        0,
        0,
        clamp(Input.get_action_strength("move_backwards") - Input.get_action_strength("move_forwards"),-1.0, 0.5)
        
    )
    return move_vec

func get_turn_vec() -> float:
    if _heuristic == "model":
        return turn_action
    var rotation_amount = Input.get_action_strength("turn_left") - Input.get_action_strength("turn_right")

    return rotation_amount

  
func reset():
    needs_reset = false
    next = 1
    n_steps = 0
    #done = false
    just_reached_negative = false
    just_reached_positive = false
    jump_action = false
     # Replace with function body.
    set_translation(Vector3(0,1.5,0))
    rotation_degrees.y = rand_range(-180,180)
    y_velo = 0.1
    
func set_action(action):
    move_action = action["move"][0]
    turn_action = action["turn"][0]
    
func reset_if_done():
    if done:
        reset()

func get_obs():
    var obs = []
    obs.append_array([move_vec.x/MOVE_SPEED,
                      move_vec.y/MAX_FALL_SPEED,
                      move_vec.z/MOVE_SPEED])

    obs.append(grounded)
    #print(virtual_camera.get_camera_pixel_encoding())
    return {
        "obs_1d": obs,
        "camera_2d": virtual_camera.get_camera_pixel_encoding(),
        "steps": n_steps
       }
    
func get_obs_space():
    # typs of obs space: box, discrete, repeated
    return {
        "obs_1d": {
            "size": [len(get_obs()["obs_1d"])],
            "space": "box"
           },
        "camera_2d":{
            "size": virtual_camera.get_camera_shape(),
            "space":"box"
           },
        "steps":{
            "size": [1],
            "space": "box"
           }
       }
    
func get_reward():
    var reward = 0.0
    reward -= 0.01 # step penalty
    
    if just_reached_negative:
        reward -= 1.0
    if just_reached_positive:
        reward += 1.0
    
    reward += shaping_reward()
    return reward
    
func shaping_reward():
    var s_reward = 0.0
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
        "turn" : {
             "size": 1,
            "action_type": "continuous"
           }
       }

func get_done():
    return done
    
func set_done_false():
    done = false


func calculate_translation(other_pad_translation : Vector3) -> Vector3:
    var new_translation := Vector3.ZERO
    var distance = rand_range(12,16)
    var angle = rand_range(-180,180)
    new_translation.z = other_pad_translation.z + sin(deg2rad(angle))*distance 
    new_translation.x = other_pad_translation.x + cos(deg2rad(angle))*distance
    
    return new_translation



func _on_NegativeGoal_body_entered(body: Node) -> void:
    just_reached_negative = true
    done = true
    needs_reset = true


func _on_PositiveGoal_body_entered(body: Node) -> void:
    just_reached_positive = true
    done = true
    needs_reset = true
