extends Area2D
class_name Player
onready var ray = $RayCast2D

export var speed = 3
export var animated = false
export var obs_shape = Vector2(5,3)

export(NodePath) onready var world = get_node(world) as TileMap


var direction = Vector2.RIGHT

var inputs = {"right": Vector2.RIGHT,
            "left": Vector2.LEFT,
            "forward": Vector2.UP,
            "backward": Vector2.DOWN}
    
func _ready():
    world.set_player(self)
    position = position.snapped(Vector2.ONE * Constants.TILE_SIZE)
    position += Vector2.ONE * Constants.TILE_SIZE/2
    world.reset()


func _physics_process(delta):
    for dir in inputs.keys():
        if Input.is_action_just_pressed(dir):
            move(dir)    
            world.get_observation(position, obs_shape, Constants.get_direction(rotation_degrees))
            break # to remove the option to move diagonally

            
func move(dir):
    if dir == "forward":    
        ray.cast_to = Vector2.RIGHT * Constants.TILE_SIZE
        ray.force_raycast_update()
        if !ray.is_colliding():
                position += direction * Constants.TILE_SIZE
                
    if dir == "backward":    
        ray.cast_to = Vector2.LEFT* Constants.TILE_SIZE
        ray.force_raycast_update()
        if !ray.is_colliding():
                position -= direction * Constants.TILE_SIZE
                
    if dir == "left":
        rotate(-PI/2)   
        direction = direction.rotated(-PI/2)
        
    if dir == "right":
        rotate(PI/2)
        direction = direction.rotated(PI/2)
        
func exit_found(_area):
    print("exit found")
    world.reset()
  
