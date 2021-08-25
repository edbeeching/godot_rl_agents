extends RigidBody



export var acceleration := 1
export var max_vertical_speed := 10
export var max_horizontal_speed := 6

# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
    pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#    pass

func _physics_process(delta):
    if Input.is_action_pressed("move_up"):
        add_central_force(Vector3(0,1,0) * acceleration)    
        
    var direction := Vector2(
        Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
        Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
    )
    
    
    
    
    
    
    if Input.is_action_pressed("move_left"):
        add_central_force(Vector3(-1,0,0) * acceleration)   
    if Input.is_action_pressed("move_right"):
        add_central_force(Vector3(1,0,0) * acceleration)
        
    if linear_velocity.y > max_vertical_speed:
        linear_velocity.y = max_vertical_speed    
    if linear_velocity.x > max_horizontal_speed:
        linear_velocity.x = max_horizontal_speed    
    if linear_velocity.x < -max_horizontal_speed:
        linear_velocity.x = -max_horizontal_speed    
    
