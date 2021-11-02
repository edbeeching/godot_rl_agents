class_name BulletHolder

extends Spatial

func get_bullets():
    return get_children().slice(0, 98)

func add_bullet():
    pass
    
func remove_bullet():
    pass

func reset():
    print("resetting bullet holder")
    for n in get_children():
        n.queue_free()
