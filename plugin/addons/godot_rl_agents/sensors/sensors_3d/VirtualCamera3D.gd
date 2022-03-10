extends Spatial
class_name VirtualCamera3D
var steps = 0
var camera_pixels = null

onready var camera_texture := $Control/TextureRect/CameraTexture as Sprite
onready var viewport := $Viewport

func get_camera_pixel_encoding():
    return camera_texture.get_texture().get_data().data["data"].hex_encode()

func get_camera_shape()-> Array:
    return [viewport.size[0], viewport.size[1], 4]
    
func _physics_process(delta):
    steps += 1
#    if steps % 120:
#        print(camera_texture.get_texture().get_data().data.format)
#        print(camera_texture.get_texture().get_data().data.keys(), 
#        len(camera_texture.get_texture().get_data().data["data"]), " ",
#        camera_texture.get_texture().get_data().data["data"],
#         camera_texture.get_texture().get_data().data["data"].hex_encode()
#
#        )
    #camera_pixels = camera_texture.get_texture().get_data().data["data"].hex_encode()


func set_viewport_size(size):
    $Viewport.size = size
