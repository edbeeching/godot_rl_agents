extends Spatial
class_name ISensor3D

var _obs = null
var _active := false

func get_observation():
    pass
    
func activate():
    _active = true
    
func deactivate():
    _active = false

func _update_observation():
    pass
    
func reset():
    pass
