class_name Gun

extends Node2D

export (PackedScene) var Bullet
const MAX_AMMO = 3
var ammo = MAX_AMMO
var _shooter = null
var episode_index
    
func shoot_at_position(position: Vector2):
    assert(ammo > 0)
    var b = Bullet.instance()
    get_tree().current_scene.add_child(b)
    
    b.position = global_position
    b.look_at(position)
    b.set_shooter(_shooter)
    
    ammo -= 1

func set_shooter(shooter: BasePlayer):
    _shooter = shooter  
 
func can_fire():
    return ammo > 0

func add_ammo():
    ammo += 1
    ammo = min(ammo, MAX_AMMO)
    
func reset():
    ammo = MAX_AMMO


func _on_Timer_timeout():
    add_ammo()
