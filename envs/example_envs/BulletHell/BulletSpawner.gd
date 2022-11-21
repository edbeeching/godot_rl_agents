class_name BulletSpawner
extends Node3D


@export var Bullet : PackedScene
@export var node_path: NodePath
@onready var node_ref = get_node(node_path) as BulletHolder

@export var path_path: NodePath
@onready var path = get_node(path_path) as PathFollow3D

var fire_rate = 1.0
var next_fire = fire_rate
var delta_sum = 0.0
var time_start = 0
func _ready():
	time_start = Time.get_unix_time_from_system()
func _process(delta):
	delta_sum += delta
	fire_rate = 0.2 + pow(sin(Time.get_unix_time_from_system() - time_start), 2)
	next_fire = fire_rate
	
	rotate_y(delta)
	
	while delta_sum > next_fire:
		delta_sum -= fire_rate
		
		for i in range(8):
			var b = Bullet.instantiate()
			if node_ref != null:
				node_ref.add_child(b)
			else:
				owner.add_child(b)
			b.transform = transform
			b.position = get_parent().position
			
			b.velocity = -b.transform.basis.z * b.speed 
			rotate_y(deg_to_rad(30))     
		
func reset():
	if path != null:
		path.reset()
	print("resetting bullet spawner")
