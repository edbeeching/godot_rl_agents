extends Node3D
class_name RGBCameraSensor3D
var camera_pixels = null

@onready var camera_texture := $Control/TextureRect/CameraTexture as Sprite2D

func get_camera_pixel_encoding():
	return camera_texture.get_texture().get_data().data["data"].hex_encode()

func get_camera_shape()-> Array:
	return [$SubViewport.size[0], $SubViewport.size[1], 4]
