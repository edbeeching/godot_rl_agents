extends ISensor2D
class_name RaycastSensor2D
tool

export(float,2, 36,2.0) var n_rays := 16.0 setget set_n_rays
export(float,5,200,5.0) var ray_length := 200 setget set_ray_length
export(float,5,360,5.0) var cone_width := 360.0 setget set_cone_width
export var debug_draw := false setget set_debug_draw


var _angles = []
var rays := []


func set_debug_draw(value):
    debug_draw = value
    if Engine.editor_hint:
        _spawn_nodes()   

func set_ray_length(value):
    ray_length = value
    if Engine.editor_hint:
        _spawn_nodes()
        
func set_n_rays(value):
    n_rays = value
    if Engine.editor_hint:
        _spawn_nodes()
        
func set_cone_width(value):
    cone_width = value
    if Engine.editor_hint:
        _spawn_nodes()

func _ready() -> void:
   _spawn_nodes()


func _spawn_nodes():
    for ray in rays:
        ray.queue_free()
    rays = []
        
    _angles = []
    var step = cone_width / (n_rays)
    var start = step/2 - cone_width/2
    
    for i in n_rays:
        var angle = start + i * step
        var ray = RayCast2D.new()
        ray.set_cast_to(Vector2(
            ray_length*cos(deg2rad(angle)),
            ray_length*sin(deg2rad(angle))
        ))
        ray.set_name("node_"+str(i))
        ray.enabled  = true
        ray.collide_with_areas = true
        add_child(ray)
        rays.append(ray)
        
        
        _angles.append(start + i * step)
    

func _physics_process(delta: float) -> void:
    if self._active:
        self._obs = calculate_raycasts()
        
func get_observation() -> Array:
    if self._obs == null:
        #print("obs was null, forcing raycast update")
        return self.calculate_raycasts()
    return self._obs
    

func calculate_raycasts() -> Array:
    var result = []
    for ray in rays:
        ray.force_raycast_update()
        var distance = _get_raycast_distance(ray)
        result.append(distance)
    return result

func _get_raycast_distance(ray : RayCast2D) -> float : 
    if !ray.is_colliding():
        return 0.0
        
    var distance = (global_position - ray.get_collision_point()).length()
    distance = clamp(distance, 0.0, ray_length)
    return (ray_length - distance) / ray_length
    
    
    
