extends PathFollow

export var speed = 5

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
    offset += delta*speed

func reset():
    offset += rand_range(0,100)
