extends Node2D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var raycasts = null

# Called when the node enters the scene tree for the first time.
func _ready():
    raycasts = get_children()

func _physics_process(delta):
    get_raycast_buffer()
        #print(child.is_colliding())
    
func get_raycast_buffer():
    var raycast_buffer := []
    for child in raycasts:
        raycast_buffer.append(_get_raycast_distance(child))
    return raycast_buffer
    
func _get_raycast_distance(rc : RayCast2D) -> float : 
    if !rc.is_colliding():
        return 0.0
        
    var distance = (global_position - rc.get_collision_point()).length()
    distance = clamp(distance,0.0,200.0)
    return (200.0 - distance) / 200.0
