class_name BulletSpawner
extends Spatial


export (PackedScene) var Bullet
export(NodePath) var node_path
onready var node_ref = get_node(node_path) as BulletHolder

export(NodePath) var path_path
onready var path = get_node(path_path) as PathFollow

var fire_rate = 1.0
var next_fire = fire_rate
var delta_sum = 0.0
var time_start = 0
func _ready():
    time_start = OS.get_unix_time()
func _process(delta):
    delta_sum += delta
    fire_rate = 0.2 + pow(sin(OS.get_unix_time() - time_start), 2)
    next_fire = fire_rate
    
    rotate_y(delta)
    
    while delta_sum > next_fire:
        delta_sum -= fire_rate
        
        for i in range(8):
            var b = Bullet.instance()
            if node_ref != null:
                node_ref.add_child(b)
            else:
                owner.add_child(b)
            b.transform = transform
            b.translation = get_parent().translation
            
            b.velocity = -b.transform.basis.z * b.speed 
            rotate_y(deg2rad(30))     
        
func reset():
    if path != null:
        path.reset()
    print("resetting bullet spawner")
