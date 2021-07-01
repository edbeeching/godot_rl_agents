extends KinematicBody2D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
export var speed := 500
export var friction = 0.18
var _velocity := Vector2.ZERO
    
func _physics_process(delta):
    var direction := Vector2(
        Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
        Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
    )
    if direction.length() > 1.0:
        direction = direction.normalized()
    # Using the follow steering behavior.
    var target_velocity = direction * speed
    _velocity += (target_velocity - _velocity) * friction
    _velocity = move_and_slide(_velocity)

    
    
func set_action():
    pass

func set_reward():
    pass
    
func set_observation():
    pass
    
func get_observation():
    pass
    
func get_reward():
    pass
    

