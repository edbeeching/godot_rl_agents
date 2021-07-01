extends Node2D

var _bounds := Rect2(50,50,1280-50,720-50)
onready var player = $Player
onready var fruit = $Fruit

func _ready():
    reset()

func reset():
    # set the player to a random location
    # set the fruit to a random location
    # reset the score
    player._velocity = Vector2.ZERO
    player.position.x = rand_range(_bounds.position.x, _bounds.end.x)
    player.position.y = rand_range(_bounds.position.y, _bounds.end.y)	
    fruit.position.x = rand_range(_bounds.position.x, _bounds.end.x)
    fruit.position.y = rand_range(_bounds.position.y, _bounds.end.y)
    
    print("player", player.position)
    print("fruit", fruit.position)



func _on_Fruit_body_entered(body):
    reset()
