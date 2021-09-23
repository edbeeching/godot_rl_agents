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

func hit_by_enemy(enemy:BasePlayer):
    hits_taken += 1
    health -= 10
    if health <= 0:
        done = true
        just_died = true
        if enemy:
            enemy.killed_enemy()
            print("killed by enemy")
    
    print("hit by enenmy")
    
func killed_enemy():
    just_killed_enemy = true

func hit_enemy():
    hits_given += 1
    print("hit enemy")

func set_teams(team1, team2):
    _team1 = team1
    _team2 = team2

func reset():
    # assign a random position
    # reset health
    # reset guns
    for g in guns:
        g.reset()
    
    done = false
    n_steps = 0
    hits_taken = 0
    hits_given = 0 
    current_gun = 0
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

func get_obs():
    var obs := [
        #ammo
        float(guns[0].ammo) / 3.0,
        float(guns[1].ammo) / 3.0,
       ]
    
    # player locations & enemy locations   
    # TODO: use vector and inverse distance, as closer enemies are more dangerous
    for team in [_team1, _team2]:
        for entity in team.children():
            var relative_position = entity.global_position - global_position
            relative_position.x /= HALF_SCREEN_WIDTH
            relative_position.y /= HALF_SCREEN_HEIGHT
            relative_position.x = clamp(relative_position.x, -1.0,1.0)
            relative_position.y = clamp(relative_position.y, -1.0,1.0)
            obs.append(relative_position.x)
            obs.append(relative_position.y)
    
    return obs
        

func get_reward():
    # final game, reward for killing enemies, negative reward for taking damage
    var reward = 0.0
    
    reward += float(hits_given)
    hits_given = 0
    reward -= float(hits_taken)
    hits_taken = 0
        
    if just_died:
        just_died = false
        reward -= 10.0   
        
    if just_killed_enemy:
        just_killed_enemy = false
        reward += 10.0
    
    return reward + shaping_reward()
    

func shaping_reward():
    return 0.0


func set_heuristic(heuristic):
    self._heuristic = heuristic

func get_obs_size():
    return len(get_obs())
   
func get_action_space():
    return {
        "move_target" : {
             "size": 2,
            "action_type": "continuous"
           },        
        "shoot_target" : {
             "size": 2,
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

    # map action space in (-1,1) to 1024
    move_target = global_position + Vector2(
        action["move_target"][0]*HALF_SCREEN_WIDTH ,
        action["move_target"][1]*HALF_SCREEN_HEIGHT 
    )    
    shoot_target = global_position + Vector2(
        action["shoot_target"][0]*HALF_SCREEN_WIDTH ,
        action["shoot_target"][1]*HALF_SCREEN_HEIGHT 
    )
    
    print("shoot action ", action["shoot_action"])
    should_shoot = action["shoot_action"] == 1
    
