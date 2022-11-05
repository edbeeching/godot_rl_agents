extends Node3D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var goals = null

# Called when the node enters the scene tree for the first time.
func _ready():
	goals = $Goals.get_children()
	pass # Replace with function body.

func get_next_goal(current_goal):
	if current_goal == null:
		return goals[0]
	var index = null
	for i in len(goals):
		if goals[i] == current_goal:
			index = (i+1) % len(goals)
			break
			
	return goals[index]

func get_last_goal():
	return goals[-1]
			


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#    pass
