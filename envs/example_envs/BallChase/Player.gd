extends KinematicBody2D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
const pad = 100
const WIDTH = 1280
const HEIGHT = 720
const MAX_FRUIT = 10
var _bounds := Rect2(pad,pad,WIDTH-2*pad,HEIGHT-2*pad)

export var speed := 500
export var friction = 0.18
var _velocity := Vector2.ZERO
var _action = Vector2.ZERO
var _heuristic = "player"
onready var fruit = $"../Fruit"
onready var raycast_sensor = $"RaycastSensor2D"
onready var walls := $"../Walls"
onready var colision_shape := $"CollisionShape2D"
onready var trail := $"Trail2D"
var fruit_just_entered = false
var just_hit_wall = false
var done = false
var best_fruit_distance = 10000.0
var fruit_count = 0
var n_steps = 0
var max_steps = 5000

onready var emitter = $"../Particles2D"

func emit():
    emitter.set_position(fruit.position)
    emitter.set_emitting(true) 

func _ready():
    reset()

func _physics_process(delta):
    var direction = get_direction()
    if direction.length() > 1.0:
        direction = direction.normalized()
    # Using the follow steering behavior.
    var target_velocity = direction * speed
    _velocity += (target_velocity - _velocity) * friction
    _velocity = move_and_slide(_velocity)
    
    n_steps += 1
    if n_steps > max_steps:
        done = true
        just_hit_wall = true
        
    if Input.is_action_just_pressed("r_key"):
        reset()

func reset():
    fruit_just_entered = false
    just_hit_wall = false
    done = false
    fruit_count = 0
    _velocity = Vector2.ZERO
    _action = Vector2.ZERO
    trail.trail_points = []
    position = _calculate_new_position()
    spawn_fruit()
    
#    position.x = rand_range(_bounds.position.x, _bounds.end.x)
#    position.y = rand_range(_bounds.position.y, _bounds.end.y)	
#    fruit.position.x = rand_range(_bounds.position.x, _bounds.end.x)
#    fruit.position.y = rand_range(_bounds.position.y, _bounds.end.y)
    best_fruit_distance = position.distance_to(fruit.position)
    n_steps = 0 

func _calculate_new_position() -> Vector2:
    var new_position := Vector2.ZERO
    new_position.x = rand_range(_bounds.position.x, _bounds.end.x)
    new_position.y = rand_range(_bounds.position.y, _bounds.end.y)	
   
    var radius = colision_shape.shape.get_radius()
    var rect = Rect2(new_position-Vector2(radius, radius), 
    Vector2(radius*2, radius*2)
    )    
    for wall in walls.get_children():
        #wall = wall as Area2D
        var cr = wall.get_node("ColorRect")
        var rect2 = Rect2(cr.get_position()+wall.position, cr.get_size())
        if rect.intersects(rect2):
            return _calculate_new_position()
    
    return new_position
    
    
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
    _action.x = action["move"][0]
    _action.y = action["move"][1]
    
func reset_if_done():
    if done:
        reset()
        
func get_obs():
    var relative = fruit.position - position
    var distance = relative.length() / 1500.0 
    relative = relative.normalized() 
    var result := []
    result.append(((position.x / WIDTH)-0.5) * 2)
    result.append(((position.y / HEIGHT)-0.5) * 2)  
    result.append(relative.x)
    result.append(relative.y)
    result.append(distance)
    var raycast_obs = raycast_sensor.get_raycast_buffer()
    result.append_array(raycast_obs)
    
#    result.append(((relative.x / WIDTH)-0.5) * 2)
#    result.append(((relative.y / HEIGHT)-0.5) * 2)  
# perform raycast here
    return result
    
func get_reward():
    var reward = 0.0
    reward -= 0.01 # step penalty
    if fruit_just_entered:
        reward += 10.0
        fruit_just_entered = false
    
    if just_hit_wall:
        reward -= 10.0
        just_hit_wall = false
    
    reward += shaping_reward()
    return reward
    
func shaping_reward():
    var s_reward = 0.0
    var fruit_distance = position.distance_to(fruit.position)
    
    if fruit_distance < best_fruit_distance:
        s_reward += best_fruit_distance - fruit_distance
        best_fruit_distance = fruit_distance
        
    s_reward /= 100.0
    return s_reward
    
func set_heuristic(heuristic):
    self._heuristic = heuristic

func get_obs_size():
    return len(get_obs())
    
func get_action_space():
    return {
        "move" : {
             "size": 2,
            "action_type": "continuous"
           }
       }   

func get_done():
    return done

func spawn_fruit():
    fruit.position = _calculate_new_position()

func fruit_collected():
    emit()
    fruit_just_entered = true
    fruit_count += 1
    spawn_fruit()
    if fruit_count > MAX_FRUIT:
        done = true

    
func wall_hit():
    done = true
    just_hit_wall = true

func _on_Fruit_body_entered(body):
    fruit_collected()


func _on_LeftWall_body_entered(body):
    wall_hit()
func _on_RightWall_body_entered(body):
    wall_hit()
func _on_TopWall_body_entered(body):
    wall_hit()
func _on_BottomWall_body_entered(body):
   wall_hit()
