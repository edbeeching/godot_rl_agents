extends KinematicBody2D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
const pad = 100
const WIDTH = 1280
const HEIGHT = 720
var _bounds := Rect2(pad,pad,WIDTH-2*pad,HEIGHT-2*pad)

export var speed := 500
export var friction = 0.18
var _velocity := Vector2.ZERO
var _action = Vector2.ZERO
var _heuristic = "player"
onready var fruit = $"../Fruit"
var fruit_just_entered = false
var just_hit_wall = false
var done = false

func _physics_process(delta):
    var direction = get_direction()
    if direction.length() > 1.0:
        direction = direction.normalized()
    # Using the follow steering behavior.
    var target_velocity = direction * speed
    _velocity += (target_velocity - _velocity) * friction
    _velocity = move_and_slide(_velocity)

func reset():
    fruit_just_entered = false
    just_hit_wall = false
    done = false
    _velocity = Vector2.ZERO
    _action = Vector2.ZERO
    print("bounds,", _bounds.position.x," ", _bounds.end.x," ", _bounds.position.y, " ",_bounds.end.y, " ", rand_range(_bounds.position.x, _bounds.end.x))
    position.x = rand_range(_bounds.position.x, _bounds.end.x)
    position.y = rand_range(_bounds.position.y, _bounds.end.y)	
    fruit.position.x = rand_range(_bounds.position.x, _bounds.end.x)
    fruit.position.y = rand_range(_bounds.position.y, _bounds.end.y)


    
func get_direction():
    if done:
        _velocity = Vector2.ZERO
        return Vector2.ZERO
        
    if _heuristic == "model":
        return _action
        
    var direction := Vector2(
        Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
        Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
    )
    
    return direction
    
func set_action(action):
    _action.x = action[0]
    _action.y = action[1]
    
func reset_if_done():
    if done:
        reset()
        
func get_obs():
    var relative = fruit.position - position
    var result = []
    result.append(((position.x / WIDTH)-0.5) * 2)
    result.append(((position.y / HEIGHT)-0.5) * 2)  
    result.append(((relative.x / WIDTH)-0.5) * 2)
    result.append(((relative.y / HEIGHT)-0.5) * 2)  
    return result
    
func get_reward():
    var reward = 0.0
    reward -= 0.01 # step penalty
    if fruit_just_entered:
        reward += 1.0
        fruit_just_entered = false
    
    if just_hit_wall:
        reward -= 1.0
        just_hit_wall = false
    
    return reward
    
func set_heuristic(heuristic):
    print("setting heuristic")
    self._heuristic = heuristic

func get_obs_size():
    return 4
    
func get_action_size():
    return 2
    
func get_action_type():
    return "continuous"

func get_done():
    return done

func _on_Fruit_body_entered(body):
    done = true
    fruit_just_entered = true


func _on_LeftWall_body_entered(body):
    done = true
    just_hit_wall = true


func _on_RightWall_body_entered(body):
    done = true
    just_hit_wall = true


func _on_TopWall_body_entered(body):
    done = true
    just_hit_wall = true


func _on_BottomWall_body_entered(body):
    done = true
    just_hit_wall = true
