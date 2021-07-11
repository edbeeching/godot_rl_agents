extends Node

var action_repeat = 8
var n_action_steps = 0

const MAJOR_VERSION := "0"
const MINOR_VERSION := "1" 

var client
var connected = false
var message_center
var should_connect = true
var agents
onready var start_time = OS.get_ticks_msec()

func _ready():
    _get_agents()
    
    connected = connect_to_server()
    if connected:
        _set_heuristic("model")
        _handshake()
        _send_env_info()
    else:
        _set_heuristic("human")
        
        
func _get_agents():
    agents = get_tree().get_nodes_in_group("AGENT")

func _set_heuristic(heuristic):
    for agent in agents:
        agent.set_heuristic(heuristic)

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
    var json_data = JSON.parse(message).result
    
    return json_data

func _send_dict_as_json_message(dict):
    client.put_string(to_json(dict))

func _send_env_info():
    var json_dict = _get_dict_json_message()
    assert(json_dict["type"] == "env_info")
    
    var message = {
        "type" : "env_info",
        "obs_size": agents[0].get_obs_size(),
        "action_size": agents[0].get_action_size(),
        "action_type": agents[0].get_action_type(),
        "n_agents": len(agents)
       }
    _send_dict_as_json_message(message)


func connect_to_server():
    print("trying to connect to server")
    client = StreamPeerTCP.new()
    client.set_no_delay(true)
    #set_process(true)
    var ip = "localhost"
    var port = 10008
    var connect = client.connect_to_host(ip, port)
    
    print(connect, client.get_status())
    
    return client.get_status() == 2;


func disconnect_from_server():
    client.disconnect_from_host()
 
func _physics_process(delta):    
    # two modes, human control, agent control
    # pause tree, send obs, get actions, set actions, unpause tree
    if n_action_steps % action_repeat != 0:
        n_action_steps += 1
        return
    n_action_steps += 1
    
    
    if connected:
        get_tree().set_pause(true) 
        
        var reward = _get_reward_from_agents()
        var done = _get_done_from_agents()
        _reset_agents_if_done() # this ensures the new observation is from the next env instance
        
        var obs = _get_obs_from_agents()
        
        var message = {
            "type": "step",
            "obs": obs,
            "reward": reward,
            "done": done
        }
        _send_dict_as_json_message(message)
        
        var response = _get_dict_json_message()
        var action = response["action"]
        _set_agent_actions(action)
        
        get_tree().set_pause(false) 
    else:
        _reset_agents_if_done()

func _reset_agents_if_done():
     for agent in agents:
        agent.reset_if_done()

func _get_obs_from_agents():
    var obs = []
    for agent in agents:
        obs.append(agent.get_obs())
    return obs
    
func _get_reward_from_agents():
    var rewards = [] 
    for agent in agents:
        rewards.append(agent.get_reward())
    return rewards    
    
func _get_done_from_agents():
    var dones = [] 
    for agent in agents:
        dones.append(agent.get_done())
    return dones    
    
func _set_agent_actions(actions):
    for i in range(len(actions)):
        agents[i].set_action(actions[i])
    
