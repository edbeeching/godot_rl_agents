extends PathFollow3D

@export var speed = 5

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	h_offset += delta*speed

func reset():
	h_offset += randf_range(0,100)
