extends Node2D

func _draw():
    for x in range(0, 1024, 64):
        draw_line(Vector2(x, 0), Vector2(x, 600), Color8(0, 0, 0))
    for y in range(0, 600, 64):
        draw_line(Vector2(0, y), Vector2(1024, y), Color8(0, 0, 0))
