```


func reset():
    pass

func reset_if_done():
    if done:
        reset()

func get_obs():
    pass

func get_reward():
    pass

func shaping_reward():
    pass


func set_heuristic(heuristic):
    self._heuristic = heuristic

func get_obs_size():
    return len(get_obs())
   
func get_action_space():
    return {
        "move" : {
             "size": 1,
            "action_type": "continuous"
           },        
        "turn" : {
             "size": 1,
            "action_type": "continuous"
           },
        "discrete1": {
            "size": 2,
            "action_type": "discrete"
           }
       }

func get_done():
    return done


func set_action(action):
    move_action = action["move"][0]
    turn_action = action["turn"][0]
    jump_action = action["jump"] == 1

```