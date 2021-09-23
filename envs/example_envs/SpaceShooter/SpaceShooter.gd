extends Node2D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var bounds_x = Vector2(-1000,1000)
var bounds_y = Vector2(-1000,1000)

onready var team1 = $Team1
onready var team2 = $Team1
# Called when the node enters the scene tree for the first time.
func _ready():
    for b in team1.children():
        b.set_teams(team1, team2)    
    for b in team2.children():
        b.set_teams(team2, team1)


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#    pass
