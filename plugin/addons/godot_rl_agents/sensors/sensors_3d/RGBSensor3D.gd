extends ISensor3D

class_name RGBSensor3D
tool

export(int) var width = 32 setget set_width
export(int) var height = 32 setget set_height
var virtual_camara = null


func set_width(value):
    width = value

    _rebuild_if_editor()
        
func set_height(value):
    height = value
    _rebuild_if_editor()

func _rebuild_if_editor():
    if Engine.editor_hint: 
        _rebuild()    
        
    
func _ready():
    _rebuild()


func _rebuild():
    # remove any spawned children
    for child in get_children():
        child.queue_free()
    
    virtual_camara = preload("res://addons/godot_rl_agents/sensors/sensors_3d/VirtualCamera3D.tscn").instance()
    
    add_child(virtual_camara)
    virtual_camara.set_owner(get_tree().edited_scene_root)
    virtual_camara.set_viewport_size(Vector2(width, height))
