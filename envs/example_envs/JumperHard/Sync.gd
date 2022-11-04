extends Node
# --fixed-fps 2000 --disable-render-loop
var action_repeat = 8
var n_action_steps = 0

const MAJOR_VERSION := "0"
const MINOR_VERSION := "1" 
const DEFAULT_PORT := 11008
var client
var connected = false
var message_center
var should_connect = true
var agents
var need_to_send_obs = false
@onready var start_time = Time.get_ticks_msec()

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
		print("WARNING: major verison mismatch ", major_version, " ", MAJOR_VERSION)  
	if minor_version != MINOR_VERSION:
		print("WARNING: major verison mismatch ", minor_version, " ", MINOR_VERSION)

func _get_dict_json_message():
	# returns a dictionary from of the most recent message
	# this is not waiting
	while client.get_available_bytes() == 0:
		if client.get_status() == 3:
			print("server disconnected status 3, closing")
			get_tree().quit()
			return null

		if !client.is_connected_to_host():
			print("server disconnected, closing")
			get_tree().quit()
			return null
		OS.delay_usec(10)
		
	var message = client.get_string()
	var test_json_conv = JSON.new()
	test_json_conv.parse(message).result
	var json_data = test_json_conv.get_data()
	
	return json_data

func _send_dict_as_json_message(dict):
	client.put_string(JSON.new().stringify(dict))

func _send_env_info():
	var json_dict = _get_dict_json_message()
	assert(json_dict["type"] == "env_info")
	
	var message = {
		"type" : "env_info",
		"obs_size": agents[0].get_obs_size(),
		"action_space":agents[0].get_action_space(),
		"n_agents": len(agents)
	   }
	_send_dict_as_json_message(message)


func connect_to_server():
	print("trying to connect to server")
	client = StreamPeerTCP.new()
	client.set_no_delay(true)
	#set_process(true)
	var ip = "localhost"
	var port = _get_port()
	var connect = client.connect_to_host(ip, port)
	
	print(connect, client.get_status())
	
	return client.get_status() == 2
	
func _get_port():
	print("getting command line arguments")
	var arguments = {}
	for argument in OS.get_cmdline_args():
		# Parse valid command-line arguments into a dictionary
		if argument.find("=") > -1:
			var key_value = argument.split("=")
			arguments[key_value[0].lstrip("--")] = key_value[1]
			
	print("got port ", arguments.get("port", DEFAULT_PORT))
	
	return int(arguments.get("port", DEFAULT_PORT))

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
		
		if need_to_send_obs:
			need_to_send_obs = false
			var reward = _get_reward_from_agents()
			var done = _get_done_from_agents()
			_reset_agents_if_done() # this ensures the new observation is from the next env instance
			
			var obs = _get_obs_from_agents()
			
			var reply = {
				"type": "step",
				"obs": obs,
				"reward": reward,
				"done": done
			}
			_send_dict_as_json_message(reply)
		
		var handled = handle_message()
	else:
		_reset_agents_if_done()

func handle_message() -> bool:
	# get json message: reset, step, close
	var message = _get_dict_json_message()
	if message["type"] == "close":
		print("received close message, closing game")
		get_tree().quit()
		get_tree().set_pause(false) 
		return true
		
	if message["type"] == "reset":
		_reset_all_agents()
		var obs = _get_obs_from_agents()
		var reply = {
			"type": "reset",
			"obs": obs
		}
		_send_dict_as_json_message(reply)   
		return handle_message()
	
	if message["type"] == "action":
		var action = message["action"]
		_set_agent_actions(action) 
		need_to_send_obs = true
		get_tree().set_pause(false) 
		return true
		
	print("message was not handled")
	return false

func _reset_agents_if_done():
	 for agent in agents:
		agent.reset_if_done()

func _reset_all_agents():
	for agent in agents:
		agent.reset()   

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
	
