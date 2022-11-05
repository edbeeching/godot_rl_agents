extends Area3D


func _on_GameArea_body_exited(body):
    body.exited_game_area()
