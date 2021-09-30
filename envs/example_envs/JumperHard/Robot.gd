extends Spatial


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

onready var player = $AnimationPlayer

# Called when the node enters the scene tree for the first time.
func _ready():
    pass # Replace with function body.



func set_animation(anim):
    if player.current_animation == anim:
        return
    
    player.play(anim)
