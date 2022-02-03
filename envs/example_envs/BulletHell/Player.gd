extends KinematicBody


export var speed := 50
export var friction = 0.18
var _velocity := Vector3.ZERO

var done = false
export(NodePath) var bullet_spawner_path
onready var bullet_spawner = get_node(bullet_spawner_path) as BulletSpawner

export(NodePath) var bullet_holder_path
onready var bullet_holder = get_node(bullet_holder_path) as BulletHolder


# for RL training
var _heuristic := "player"
# example actions
var move_action
var hit_by_bullet = false 
var n_steps = 0
var max_steps = 20000

func _ready():
    reset()

func _physics_process(delta):
    var direction = get_direction()
    if direction.length() > 1.0:
        direction = direction.normalized()
    # Using the follow steering behavior.
    var target_velocity = direction * speed
    _velocity += (target_velocity - _velocity) * friction
    _velocity = move_and_slide(_velocity)
    
    # episode termination condition
    n_steps += 1
    if n_steps >  max_steps:
        done = true
    
func get_direction():
    if done:
        _velocity = Vector3.ZERO
        return Vector3.ZERO
        
    if _heuristic == "model":
        return  Vector3(
        move_action[0],
        0.0,
        move_action[1]
    )
        
    var direction := Vector3(
        Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
        0.0,
        Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
    )
    
    return direction
    
func hit_by_bullet():
    print("player hit by bullet")
    done = true


func reset():
    done = false
    hit_by_bullet = false
    n_steps = 0 
    if bullet_spawner != null:
        bullet_spawner.reset()    
    if bullet_holder != null:
        bullet_holder.reset()
    translation.x = rand_range(-20,20)
    translation.z = rand_range(-20,20)
    # The reset logic e.g reset if a player dies etc, reset health, ammo, position, etc ...
    # reset the player position
    # reset the bullet spawner position
    pass

func reset_if_done():
    if done:
        reset()

func get_obs():
# The observation of the agent, think of what is the key information that is needed to perform the task, try to have things in coordinates that a relative to the play
    # get a variable sized vector of observations from the bullet holder
    var obs = []
    var bs = bullet_spawner.translation - translation
    obs.append([
        clamp(bs.x/40.0,-1.0,1.0),
        clamp(bs.y/40.0,-1.0,1.0),
        clamp(bs.z/40.0,-1.0,1.0),
    ])
    var bullets = bullet_holder.get_bullets()
    for b in bullets:
        var bs2 = b.translation - translation
        obs.append([
            clamp(bs2.x/40.0,-1.0,1.0),
            clamp(bs2.y/40.0,-1.0,1.0),
            clamp(bs2.z/40.0,-1.0,1.0),
        ])
    print("send obs", obs)
    return {"obs": obs}

func get_reward():
    var reward = 0
    if hit_by_bullet:
        reward -= 10.0
        hit_by_bullet = false
    # What behavior do you want to reward, kills? penalties for death, key waypoints
    return reward + shaping_reward()

func shaping_reward():
    return 0.01


func set_heuristic(heuristic):
    # sets the heuristic from "human" or "model" nothing to change here
    self._heuristic = heuristic

func get_obs_size():
    # nothing to change here
    return len(get_obs())
    
func get_obs_space():
    # typs of obs space: box, discrete, repeated (for variable length observations)
    return {
        "obs": {
            "size": len(get_obs()["obs"][0]),
            "space": "repeated",
            "subspace": "box",
            "max_length": 100
           }
       }
     
func get_action_space():
    # Define the action space of you agent, below is an example, GDRL allows for discrete and continuous state spaces (assuming the RL algorithm allows it)
    return {
        "move" : {
             "size": 2,
            "action_type": "continuous"
           }
       }

func get_done():
    # nothing to change here
    return done


func set_action(action):
    # reads off the actions sent from the RL model to the agent
    # the keys here should match the dictionary keys in the "get_action_space" function
    move_action = action["move"]
    
