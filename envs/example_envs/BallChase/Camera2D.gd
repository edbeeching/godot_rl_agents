extends Camera2D

const MOVE_SPEED = 1000


func _process(delta):
    if Input.is_action_pressed("left_arrow"):
        global_position += Vector2.LEFT * delta * MOVE_SPEED
    elif Input.is_action_pressed("right_arrow"):
        global_position += Vector2.RIGHT * delta * MOVE_SPEED
