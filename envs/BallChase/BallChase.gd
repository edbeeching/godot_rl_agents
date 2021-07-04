extends Node2D

var _bounds := Rect2(50,50,1280-50,720-50)
onready var player = $Player
onready var fruit = $Fruit
export var STEP_REWARD := -0.01
export var GOAL_REWARD := 1.0
export var FAIL_REWARD := -1.0
var just_got_fruit = false
var just_wall_hit = false
var done = false
#var reward = 0.0


const MAJOR_VERSION := "0"
const MINOR_VERSION := "1" 

var client
var wrapped_client
var connected = false
var message_center
var should_connect = true
onready var start_time = OS.get_ticks_msec()

func _ready():
    client = StreamPeerTCP.new()
    client.set_no_delay(true)
    
    connect_to_server(1.0)
    _handshake()
    _send_env_info()
    
    reset()

func _handshake():
    print("performing handshake")
    
    var json_dict = _get_dict_json_message()
    assert(json_dict["type"] == "handshake")
    var major_version = json_dict["major_version"]
    var minor_version = json_dict["minor_version"]
    if major_version != MAJOR_VERSION:
        print("WARNING: major verison mismatching ", major_version, " ", MAJOR_VERSION)  
    if minor_version != MINOR_VERSION:
        print("WARNING: major verison mismatching ", minor_version, " ", MINOR_VERSION)

func _get_dict_json_message():
    # returns a dictionartary from of the most recent message
    # this is not waiting
    while client.get_available_bytes() == 0:
        OS.delay_msec(1)
    var message = client.get_string()

    print("message received")
    print(message)
    var json_data = JSON.parse(message).result
    
    return json_data

func _send_dict_as_json_message(dict):
    print("Sending: %s" % to_json(dict))
    client.put_string(to_json(dict))

func _send_env_info():
    var json_dict = _get_dict_json_message()
    assert(json_dict["type"] == "env_info")
    
    var message = {
        "type" : "env_info",
        "obs_size":"4",
        "action_size": "2",
        "action_type": "continuous",
        "n_agents": "2"
       }
    _send_dict_as_json_message(message)


func connect_to_server(timeout_seconds):
    set_process(true)
    should_connect = false
    var ip = "localhost"
    var port = 10008
    var connect = client.connect_to_host(ip, port)
    if client.is_connected_to_host():
        print("connected to host")
        connected = true

        wrapped_client = PacketPeerStream.new()
        wrapped_client.set_stream_peer(client)


func disconnect_from_server():
    client.disconnect_from_host()

        
func reset():
    player._velocity = Vector2.ZERO
    player.position.x = rand_range(_bounds.position.x, _bounds.end.x)
    player.position.y = rand_range(_bounds.position.y, _bounds.end.y)	
    fruit.position.x = rand_range(_bounds.position.x, _bounds.end.x)
    fruit.position.y = rand_range(_bounds.position.y, _bounds.end.y)
    
    done = true

func _get_obs():
    return [0.0,1.0,2.0,3.0]
    
func _get_done():
    return true

func _get_reward():
    return -0.5

func get_reward():
    var reward = 0.0
    reward += STEP_REWARD
    
    if(just_got_fruit):
        reward += GOAL_REWARD
        just_got_fruit = false    
    if(just_wall_hit):
        reward += FAIL_REWARD
        just_wall_hit = false
    return reward
    
func _physics_process(delta):    
    # two modes, human control, agent control
    # pause tree, send obs, get actions, set actions, unpause tree
    print("pause")
    get_tree().set_pause(true) 
    var message = {
        "type":"step",
        "obs": _get_obs(),
        "reward": _get_reward(),
        "done": _get_done()
           
       }
    _send_dict_as_json_message(message)
    
    var response = _get_dict_json_message()
    var action = response["action"]
    player.set_action(action)
    print("action received")
    
    
    get_tree().set_pause(false) 

func step():
    get_reward()
    var obs =  player.position
    
    done = false

func _on_Fruit_body_entered(body):
    just_got_fruit = true
    reset()


func _wall_hit():
    just_wall_hit = true
    reset()

func _on_LeftWall_body_entered(body):
    _wall_hit()


func _on_RightWall_body_entered(body):
    _wall_hit()


func _on_TopWall_body_entered(body):
    _wall_hit()


func _on_BottomWall_body_entered(body):
    _wall_hit()
