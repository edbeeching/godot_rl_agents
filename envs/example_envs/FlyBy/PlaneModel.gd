extends Node3D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
@onready var anim = $AnimationPlayer

# Called when the node enters the scene tree for the first time.
func _ready():
	get_node("AnimationPlayer").get_animation("Main")#.set_loop(true)
	anim.play("Main")


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#    pass
