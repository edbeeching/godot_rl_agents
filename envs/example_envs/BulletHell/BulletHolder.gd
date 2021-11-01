class_name BulletHolder

extends Spatial



func get_bullets():
    pass

func add_bullet():
    pass
    
func remove_bullet():
    pass

func reset():
    print("resetting bullet holder")
    for n in get_children():
        n.queue_free()
