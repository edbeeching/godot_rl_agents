extends TileMap
class_name GridWorld

var _player = null

    
export var rooms_size := Vector2(2, 6)
export var rooms_max := 15


var map_size = Vector2(16,16)
var level_size = Vector2(16,16)

func set_player(player:Player):
    _player = player
    
func reset():
    assert(_player != null)
    
    generate_map()

func place_player():
    pass

func clear_goals():
    for goal in $Goals.get_children():
        goal.queue_free()

func generate_map():
    
    clear()    
    clear_goals()
    # create the walls
    create_walls()
    
    _generate()
    # place the player
    create_player()
    # create the goal
    create_goal()

func create_walls():
    # clear the map
    for i in map_size.y:
            for j in map_size.x:
                set_cellv(Vector2(j,i),Constants.TILES.WALL)
#                if j in [0,map_size.x-1] or i in [0,map_size.y-1]:
#                    set_cellv(Vector2(j,i),Constants.TILES.WALL)
#                else:
#                    set_cellv(Vector2(j,i),Constants.TILES.EMPTY)
    
func create_player():
    var player_position = get_valid_position()  
                                                       
    _player.position = map_to_world(player_position) + Vector2(Constants.TILE_SIZE, Constants.TILE_SIZE)/2 

func get_valid_position():
    var position = Vector2(randi() % int(map_size.x-2) +1 ,
                                    randi() % int(map_size.y-2) +1 )                   
    while get_cellv(position) == Constants.TILES.WALL:
        position = Vector2(randi() % int(map_size.x-2) +1 ,
                                        randi() % int(map_size.y-2) +1 )     

    return position 

func create_goal():
    var goal_position = get_valid_position()  

    set_cellv(goal_position, Constants.TILES.GOAL)         
    print(goal_position)                    
    var goal = preload("res://Goal.tscn").instance()
    goal.position = map_to_world(goal_position) + Vector2(Constants.TILE_SIZE, Constants.TILE_SIZE)/2
    goal.connect("area_entered", _player, "exit_found")   
    #goal.connect("area_entered", self, "goal_reached")  
    $Goals.add_child(goal)  
    
    
    # Static typing with enums will be available in Godot 4
func get_observation(position : Vector2, shape: Vector2, orientation: int) -> Array:
    var obs = []
    assert(int(shape.x)%2 ==1) #  assume observations centred on the agent
    var agent_position = world_to_map(position)
    match orientation:
        Constants.DIRECTIONS.NORTH:
            for i in range(-int(shape.y)+1, 1, 1):
                for j in range(-int(shape.x /2), int(shape.x /2)+1, 1):
                    var cell = get_cell(agent_position.x + j, agent_position.y + i)
                    var result = [cell,0,0] #  object type, color, state
                    obs.append(result)
        Constants.DIRECTIONS.SOUTH:
            for i in range(int(shape.y)-1, -1, -1):
                for j in range(int(shape.x /2), -1*(int(shape.x /2)+1), -1):
                    var cell = get_cell(agent_position.x + j, agent_position.y + i)
                    var result = [cell,0,0] #  object type, color, state
                    obs.append(result)
        Constants.DIRECTIONS.WEST:
            for j in range(int(shape.y)-1, -1, -1):
                for i in range(int(shape.x /2), -1*(int(shape.x /2)+1), -1):
                    var cell = get_cell(agent_position.x + j, agent_position.y + i)
                    var result = [cell,0,0] #  object type, color, state
                    obs.append(result)
        Constants.DIRECTIONS.EAST:
            for j in range(-int(shape.y)+1, 1, 1):
                for i in range(-int(shape.x /2), int(shape.x /2)+1, 1):
                    var cell = get_cell(agent_position.x + j, agent_position.y + i)
                    var result = [cell,0,0] #  object type, color, state
                    obs.append(result)
    return obs
    

func _generate() -> void:
    
    for vector in _generate_data():
        set_cellv(vector, Constants.TILES.EMPTY)


func _generate_data() -> Array:
    var rng := RandomNumberGenerator.new()
    rng.randomize()

    var data := {}
    var rooms := []
    for r in range(rooms_max):
        var room := _get_random_room(rng)
        if _intersects(rooms, room):
            continue

        _add_room(data, rooms, room)
        if rooms.size() > 1:
            var room_previous: Rect2 = rooms[-2]
            _add_connection(rng, data, room_previous, room)
    return data.keys()


func _get_random_room(rng: RandomNumberGenerator) -> Rect2:
    var width := rng.randi_range(rooms_size.x, rooms_size.y)
    var height := rng.randi_range(rooms_size.x, rooms_size.y)
    var x := rng.randi_range(0, level_size.x - width - 1)
    var y := rng.randi_range(0, level_size.y - height - 1)
    return Rect2(x, y, width, height)


func _add_room(data: Dictionary, rooms: Array, room: Rect2) -> void:
    rooms.push_back(room)
    for x in range(room.position.x, room.end.x):
        for y in range(room.position.y, room.end.y):
            data[Vector2(x, y)] = null


func _add_connection(rng: RandomNumberGenerator, data: Dictionary, room1: Rect2, room2: Rect2) -> void:
    var room_center1 := (room1.position + room1.end) / 2
    var room_center2 := (room2.position + room2.end) / 2
    if rng.randi_range(0, 1) == 0:
        _add_corridor(data, room_center1.x, room_center2.x, room_center1.y, Vector2.AXIS_X)
        _add_corridor(data, room_center1.y, room_center2.y, room_center2.x, Vector2.AXIS_Y)
    else:
        _add_corridor(data, room_center1.y, room_center2.y, room_center1.x, Vector2.AXIS_Y)
        _add_corridor(data, room_center1.x, room_center2.x, room_center2.y, Vector2.AXIS_X)


func _add_corridor(data: Dictionary, start: int, end: int, constant: int, axis: int) -> void:
    for t in range(min(start, end), max(start, end) + 1):
        var point := Vector2.ZERO
        match axis:
            Vector2.AXIS_X: point = Vector2(t, constant)
            Vector2.AXIS_Y: point = Vector2(constant, t)
        data[point] = null


func _intersects(rooms: Array, room: Rect2) -> bool:
    var out := false
    for room_other in rooms:
        if room.intersects(room_other):
            out = true
            break
    return out
    
    
    
    
    

