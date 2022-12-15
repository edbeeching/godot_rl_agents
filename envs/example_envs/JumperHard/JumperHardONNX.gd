extends Node

var inferencer = null
var obs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# Called when the node enters the scene tree for the first time.
func _ready():
	inferencer = ONNXModel.new("res://model.onnx", 1)
	

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if inferencer != null:
		var test = inferencer.run_inference(obs, 0)
		if test == null:
			set_process(false)
		else:
			print(test)
