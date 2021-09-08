extends Spatial


var raycasts = null

# Called when the node enters the scene tree for the first time.
func _ready():
    raycasts = get_children()

func _physics_process(delta):
    get_raycast_buffer()
    
func get_raycast_buffer():
    var raycast_buffer := []
    for child in raycasts:
        raycast_buffer.append(_get_raycast_distance(child))
    return raycast_buffer
    
func _get_raycast_distance(rc : RayCast) -> float : 
    if !rc.is_colliding():
        return 0.0
         
    var distance = (get_translation() - rc.get_collision_point()).length()
    distance = clamp(distance, 0.0, 40.0)
    return (40.0 - distance) / 40.0
