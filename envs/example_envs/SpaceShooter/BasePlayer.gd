class_name BasePlayer

extends KinematicBody2D

var speed = 200
var move_target =  Vector2.ZERO
var velocity = Vector2.ZERO
export var controlled = false
export var _team = 0

const HALF_SCREEN_WIDTH = 512 
const HALF_SCREEN_HEIGHT = 300
onready var guns = [$Gun, $Gun2] 
const MAX_HEALTH = 50
var current_gun = 0
var done = false
var n_steps = 0
var _heuristic := "player"
const MAX_STEPS = 5000
var hits_taken = 0
var hits_given = 0 
var episode_index = 0
var should_shoot = false
var shoot_target = Vector2.ZERO
var health = MAX_HEALTH
var just_died = false
var just_killed_enemy = false
var _team1 = null
var _team2 = null
var _bound_x := Vector2.ZERO
var _bound_y := Vector2.ZERO
var _initialized = false
var o = null
var n_collisions = 0

#var shoot_angle = 0.0

func _ready():
    for g  in guns:
        g.set_shooter(self)

func _input(event):
    if !controlled:
        return
    if event is InputEventMouseButton and event.pressed:
        match event.button_index:
            BUTTON_LEFT:
                move_target = get_global_mouse_position() 
            BUTTON_RIGHT:
                shoot_target = get_global_mouse_position()
                should_shoot = true
                
      
func shoot():
    if !should_shoot:
        return
    should_shoot = false
    if guns[current_gun].can_fire(): # fire the current gun, changes gun
        guns[current_gun].shoot_at_position(shoot_target)
        current_gun  = (current_gun+1) % 2
    elif guns[(current_gun+1) % 2 ].can_fire(): # see if other gun can fire
        guns[(current_gun+1) % 2 ].shoot_at_position(shoot_target)
    else:
        return
    
            
func _physics_process(delta):
    if !_initialized:
        reset()
        _initialized = true
    n_steps += 1
    if n_steps > MAX_STEPS:
        done = true
    
    if move_target:
        look_at(move_target)
        velocity = transform.x * speed
        # stop moving if we get close to the move_target

        if position.distance_to(move_target) > 5:
            velocity = move_and_slide(velocity)
            
    shoot() 
    check_if_out_of_bounds()
    if Input.is_action_just_pressed("r_key"):
        reset()
    
func check_if_out_of_bounds():
    if (
        global_position.x > _bound_x[0] and 
        global_position.x < _bound_x[1] and       
        global_position.y > _bound_y[0] and 
        global_position.y < _bound_y[1]     
    ):
        return
    done = true
    just_died = true

func hit_by_enemy(enemy:BasePlayer):
    hits_taken += 1
    health -= 10
    if health <= 0:
        done = true
        just_died = true
        if enemy:
            enemy.killed_enemy()
            #print("killed by enemy")
    
    
func killed_enemy():
    just_killed_enemy = true

func hit_enemy():
    hits_given += 1

func set_bounds( bound_x :Vector2 ,  bound_y : Vector2):
    _bound_x = bound_x
    _bound_y = bound_y

func set_teams(team1, team2):
    _team1 = team1
    _team2 = team2


func calculate_k_nearest(team, k):
    # given an array of positions, return the k nearest positions to the objects global position
    var arr = []
    for entity in team.get_children():
        if entity == self: continue # no need to encode myself
        var obs_vector = get_obs_vector(global_position, entity.global_position)
        arr.append(obs_vector)
    
    assert(len(arr) >= k)
    # sort the obs vector
    arr.sort_custom(self, "custom_sort")
    arr.invert()
    
    return arr.slice(0,k)
    
func custom_sort(a,b):
    # return the value with the smallest distance
    return a[2] < b[2]

func reset():
    # assign a random position
    global_position.x = rand_range(_bound_x[0], _bound_x[1])
    global_position.y = rand_range(_bound_y[0], _bound_y[1])
    move_target = global_position
    # reset health
    # reset guns
    for g in guns:
        g.reset()
    
    done = false
    n_steps = 0
    hits_taken = 0
    hits_given = 0 
    current_gun = 0
    n_collisions = 0
    episode_index += 1
    should_shoot = false
    
    just_died = false
    just_killed_enemy = false
    # assign a random position
    # reset health  
    health = MAX_HEALTH  

func reset_if_done():
    if done:
        reset()

func get_obs_vector(from: Vector2, to: Vector2)->Vector3:
    var result = Vector3.ZERO
    var relative_position = to - from
    var distance = relative_position.length()
    distance = 1.0 - clamp(distance, 0,1000.0)/1000.0
    var vector = relative_position.normalized()

    result[0] = vector[0]
    result[1] = vector[1]
    result[2] = distance
    
    return result
    
func get_obs():
    var obs := [
        #ammo
        float(guns[0].ammo) / 3.0,
        float(guns[1].ammo) / 3.0,
        float(health) / float(MAX_HEALTH)
       ]
    
    # player locations & enemy locations   
    # TODO: use vector and inverse distance, as closer enemies are more dangerous
    for team in [_team2,_team1]:
        var nearest = calculate_k_nearest(team, 3)
        for obs_vector in nearest:
            obs.append(obs_vector[0])
            obs.append(obs_vector[1])
            obs.append(obs_vector[2]) 
            var angle = atan2(obs_vector[1], obs_vector[0])
            obs.append(angle/PI)      
        
#        for entity in team.get_children():
#            if entity == self: continue # no need to encode myself
#            #var relative_position = entity.global_position - global_position
#            var obs_vector = get_obs_vector(global_position, entity.global_position)
#
##            relative_position.x /= (HALF_SCREEN_WIDTH*2)
##            relative_position.y /= (HALF_SCREEN_HEIGHT*2)
##            relative_position.x = clamp(relative_position.x, -1.0, 1.0)
##            relative_position.y = clamp(relative_position.y, -1.0, 1.0)
##            obs.append(relative_position.x)
##            obs.append(relative_position.y)
#
#            obs.append(obs_vector[0])
#            obs.append(obs_vector[1])
#            obs.append(obs_vector[2])
    
#    var shoot_angle = PI*obs[0]
#    shoot_target = global_position + Vector2(
#        cos(shoot_angle)*HALF_SCREEN_HEIGHT,
#        sin(shoot_angle)*HALF_SCREEN_HEIGHT
#    )
    
    var position = Vector2(
        global_position.x / _bound_x[1],
        global_position.y / _bound_y[1]
       )
    position.x = clamp(position.x, -1.0, 1.0)
    position.y = clamp(position.y, -1.0, 1.0)
    obs.append(position.x)
    obs.append(position.y)
    return obs
        

func get_reward():
    # final game, reward for killing enemies, negative reward for taking damage
    var reward = 0.0
    reward -= 0.01
    reward += float(hits_given)
    #print(reward)
    hits_given = 0
    #reward -= float(hits_taken) #remove for testing shooting
    hits_taken = 0
    #reward -= float(n_collisions)
    n_collisions = 0
        
    if just_died:
        just_died = false
        reward -= 10.0 #  removed for testing shooting
        
    if just_killed_enemy:
        just_killed_enemy = false
        reward += 10.0# removed  for testing shooting
    
    return reward + shaping_reward()
    

func shaping_reward():
    return 0.0


func set_heuristic(heuristic):
    self._heuristic = heuristic

func get_obs_size():
    return len(get_obs())
   
func get_action_space():
    return {
        "move_angle" : {
             "size": 1,
            "action_type": "continuous"
           },        
#        "shoot_target" : {
#             "size": 2,
#            "action_type": "continuous"
#           },        
        "shoot_angle" : {
             "size": 1,
            "action_type": "continuous"
           },
        "shoot_action": {
            "size": 2,
            "action_type": "discrete"
           }
       }

func get_done():
    return done

func set_action(action):

    # map action space in (-1,1) to 1024. for the agent we consider a square around it
    var move_angle = PI*action["move_angle"][0]
    move_target = global_position + Vector2(
        cos(move_angle)*HALF_SCREEN_HEIGHT,
        sin(move_angle)*HALF_SCREEN_HEIGHT
    )
    #move_target = global_position
    var shoot_angle = PI*action["shoot_angle"][0]
    shoot_target = global_position + Vector2(
        cos(shoot_angle)*HALF_SCREEN_HEIGHT,
        sin(shoot_angle)*HALF_SCREEN_HEIGHT
    )
    should_shoot = action["shoot_action"] == 1
    


func _on_HealthTimer_timeout():
    health += 10
    health = min(health, MAX_HEALTH)


func _on_Area_area_shape_entered(area_id, area, area_shape, local_shape):
    n_collisions += 1
