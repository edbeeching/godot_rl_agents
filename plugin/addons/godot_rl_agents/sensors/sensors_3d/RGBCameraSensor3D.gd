extends Spatial
class_name RGBCameraSensor3D
var camera_pixels = null

onready var camera_texture := $Control/TextureRect/CameraTexture as Sprite

func get_camera_pixel_encoding():
    return camera_texture.get_texture().get_data().data["data"].hex_encode()

func get_camera_shape()-> Array:
    return [$Viewport.size[0], $Viewport.size[1], 4]
