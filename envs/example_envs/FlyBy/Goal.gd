extends CSGTorus3D



func _on_Area_body_entered(body):
	body.goal_reached(self)
