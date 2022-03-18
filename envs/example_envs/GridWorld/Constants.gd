extends Node
class_name Constants


const TILE_SIZE := 64 
enum TILES {
    PLAYER = 0,
    GOAL = 1
    EMPTY = 2 ,
    WALL = 3,
    BLUE_KEY = 4
   }
enum DIRECTIONS {
    NORTH,
    SOUTH,
    EAST,
    WEST,
   }

#const DIRECTION_LOOKUP = {
#    Vector2.UP : DIRECTIONS.NORTH,
#    Vector2.DOWN : DIRECTIONS.SOUTH,
#    Vector2.RIGHT: DIRECTIONS.EAST,
#    Vector2.LEFT: DIRECTIONS.WEST    
#   }
const DIRECTION_LOOKUP = {
    270 : DIRECTIONS.NORTH,
    90 : DIRECTIONS.SOUTH,
    0: DIRECTIONS.EAST,
    180: DIRECTIONS.WEST    
   }

static func get_direction(rotation_degrees):
    # a bit hacky but works
    var degrees = fmod(round(rotation_degrees)+360000.0, 360.0)
    
    return DIRECTION_LOOKUP[int(degrees)]
    
    
    
