extends Spatial
class_name RGBCameraSensor3D
var camera_pixels = null

onready var camera_texture := $Control/TextureRect/CameraTexture as Sprite
onready var viewport = $Viewport


func get_camera_pixel_encoding():
#    var tex_id = viewport.get_texture().get_rid()
#    var gl_id = VisualServer.texture_get_texid(tex_id)
#    prints(tex_id.get_id(), gl_id, viewport.get_viewport_rid().get_id())
    #print(viewport.get_texture().get_data().data["data"])
    return viewport.get_texture().get_data().data["data"].hex_encode()
    #return camera_texture.get_texture().get_data().data["data"].hex_encode()
    # hex encode : 10.63 ms for 32 calls.
    # data["data"] 8.28 ms
    # get_data() 7.37 ms
    # camera_texture.get_texture() 0.01 ms
    
    # camera_texture.get_texture().get_data() is the bottleneck

func get_camera_shape()-> Array:
    return [$Viewport.size[0], $Viewport.size[1], 4]

