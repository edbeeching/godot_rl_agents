extends Node
# --fixed-fps 2000 --disable-render-loop
export var action_repeat := 8
export(float) var speed_up = 1.0
var n_action_steps = 0

const MAJOR_VERSION := "0"
const MINOR_VERSION := "1" 
const DEFAULT_PORT := 11008
const DEFAULT_SEED := 1
const DEFAULT_ACTION_REPEAT := 8
var client : StreamPeerTCP = null
var connected = false
var message_center
var should_connect = true
var agents
var need_to_send_obs = false
var args = {}
onready var start_time = OS.get_ticks_msec()
var initialized = false
var just_reset = false
func _ready():
	yield(get_tree().root, "ready")
	get_tree().set_pause(true) 
	_initialize()
	yield(get_tree().create_timer(1.0), "timeout")
	get_tree().set_pause(false) 
		
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
		
	print("handshake complete")

func _get_dict_json_message():
	# returns a dictionary from of the most recent message
	# this is not waiting
	#TODO: Handled through another flag in Godot 4.0, need to check if this is available in 3.5
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
	var json_data = JSON.parse(message).result
		
	return json_data

func _send_dict_as_json_message(dict):
	client.put_string(to_json(dict))

func _send_env_info():
	var json_dict = _get_dict_json_message()
	assert(json_dict["type"] == "env_info")
		
	var message = {
		"type" : "env_info",
		#"obs_size": agents[0].get_obs_size(),
		"observation_space": agents[0].get_obs_space(),
		"action_space":agents[0].get_action_space(),
		"n_agents": len(agents)
	   }
	_send_dict_as_json_message(message)


func connect_to_server():
	print("Waiting for one second to allow server to start")
	OS.delay_msec(1000)
	print("trying to connect to server")
	client = StreamPeerTCP.new()
		
	#set_process(true)"localhost" was not working on windows VM, had to use the IP
	var ip = "127.0.0.1"
	var port = _get_port()
	var connect = client.connect_to_host(ip, port)
		
	print(connect, client.get_status())
	client.set_no_delay(true) # TODO check if this improves performance or not
	return client.get_status() == 2

func _get_args():
	print("getting command line arguments")
	var arguments = {}
	for argument in OS.get_cmdline_args():
		# Parse valid command-line arguments into a dictionary
		if argument.find("=") > -1:
			var key_value = argument.split("=")
			arguments[key_value[0].lstrip("--")] = key_value[1]
		else:
			# Options without an argument will be present in the dictionary,
			# with the value set to an empty string.
			arguments[argument.lstrip("--")] = ""

	return arguments   

func _get_speedup():
	print(args)
	return int(args.get("speedup", speed_up))

func _get_port():	
	return int(args.get("port", DEFAULT_PORT))

func _set_seed():
	var _seed = int(args.get("env_seed", DEFAULT_SEED))
	seed(_seed)

func _set_action_repeat():
	action_repeat = int(args.get("action_repeat", DEFAULT_ACTION_REPEAT))
		

func disconnect_from_server():
	client.disconnect_from_host()

func _initialize():
	_get_agents()
	Engine.iterations_per_second = _get_speedup() * 60 # Replace with function body.
	Engine.time_scale = _get_speedup() * 1.0
	prints("physics ticks", Engine.iterations_per_second, Engine.time_scale, _get_speedup(), speed_up)
	
	args = _get_args()
	connected = connect_to_server()
	if connected:
		_set_heuristic("model")
		_handshake()
		_send_env_info()
	else:
		_set_heuristic("human")  
		
	_set_seed()
	_set_action_repeat()
	initialized = true  

func _physics_process(delta): 
	# two modes, human control, agent control
	# pause tree, send obs, get actions, set actions, unpause tree
	if n_action_steps % action_repeat != 0:
		n_action_steps += 1
		return
		 
	n_action_steps += 1
		
	if connected:
		get_tree().set_pause(true) 
		
		if just_reset:
			just_reset = false
			var obs = _get_obs_from_agents()
		
			var reply = {
				"type": "reset",
				"obs": obs
			}
			_send_dict_as_json_message(reply)
			# this should go straight to getting the action and setting it on the agent, no need to perform one phyics tick
			get_tree().set_pause(false) 
			return
		
		if need_to_send_obs:
			need_to_send_obs = false
			var reward = _get_reward_from_agents()
			var done = _get_done_from_agents()
			#_reset_agents_if_done() # this ensures the new observation is from the next env instance : NEEDS REFACTOR
			
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
		print("resetting all agents")
		_reset_all_agents()
		just_reset = true
		get_tree().set_pause(false) 
		#print("resetting forcing draw")
#		VisualServer.force_draw()
#		var obs = _get_obs_from_agents()
#		print("obs ", obs)
#		var reply = {
#			"type": "reset",
#			"obs": obs
#		}
#		_send_dict_as_json_message(reply)   
		return true
		
	if message["type"] == "call":
		var method = message["method"]
		var returns = _call_method_on_agents(method)
		var reply = {
			"type": "call",
			"returns": returns
		}
		print("calling method from Python")
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

func _call_method_on_agents(method):
	var returns = []
	for agent in agents:
		returns.append(agent.call(method))
		
	return returns


func _reset_agents_if_done():
	for agent in agents:
		if agent.get_done(): 
			agent.set_done_false()

func _reset_all_agents():
	for agent in agents:
		agent.needs_reset = true
		#agent.reset()   

func _get_obs_from_agents():
	var obs = []
	for agent in agents:
		obs.append(agent.get_obs())
	return obs
		
func _get_reward_from_agents():
	var rewards = [] 
	for agent in agents:
		rewards.append(agent.get_reward())
		agent.zero_reward()
	return rewards	
		
func _get_done_from_agents():
	var dones = [] 
	for agent in agents:
		var done = agent.get_done()
		if done: agent.set_done_false()
		dones.append(done)
	return dones	
		
func _set_agent_actions(actions):
	for i in range(len(actions)):
		agents[i].set_action(actions[i])
		
