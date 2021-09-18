extends CSGTorus



func _on_Area_body_entered(body):
    print("body entered")
    body.goal_reached(self)
