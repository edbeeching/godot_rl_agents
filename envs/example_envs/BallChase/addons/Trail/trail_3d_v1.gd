#tool
extends ImmediateGeometry

export(bool) 			var emit = true
export(float) 			var max_distance = 0.5
export(int, 0, 99999)	var segments = 20
export(float) 			var life_time = 5.0
export(float, 0, 99999) var base_width = 1.0
export(bool)			var tiled_texture = false
export(int)				var tiling = 0
export(Curve) 			var width_profile
export(Curve) 			var width_over_time
export(Gradient)		var color_gradient
export(float, 0, 0.5) 	var smoothing_ratio = 0.2
export(int, 4) 			var smoothing_iterations = 1
export(String, "View", "Motion", "Object") 	var alignment = "View"
export(String, "Idle", "Fixed") 			var prcess_mode = "Idle"
export(bool) 			var show_wireframe = false
export(Color) 			var wireframe_color = Color(1, 1, 1)

var target
var path_points = []


class Point:
	var position = Vector3()
	var normal = Vector3()
	var age = 0
	
	func _init(position, normal, age):
		self.position = position
		self.normal = normal
		self.age = age
	
	func update(delta):
		age -= delta

func _ready():
	set_as_toplevel(true)
	target = get_parent()
	global_transform = Transform()
	
func _process(delta):
	if emit:
		add_point()
	update_points()
	render()
	
	
func add_point():
	if target:
		var pos = target.global_transform.origin
		var normal = target.global_transform.basis.y.normalized()

		if emit:
			var points_count = path_points.size()
	
			if points_count < 1:
				var point = Point.new(pos, normal, life_time)
				path_points.append(point)
			else:
				var distance = path_points[points_count-2].position.distance_squared_to(pos)
				if distance > (max_distance * max_distance):
					var point = Point.new(pos, normal, life_time)
					path_points.append(point)
	
			if points_count > 1:
				path_points[points_count-1].position = pos


func update_points():
	var delta = 0
	if prcess_mode == "Fixed": 
		delta = get_physics_process_delta_time()
	else:
		delta = get_process_delta_time()
		
	var points_count = path_points.size()
	if points_count > segments:
		path_points.pop_front()

	for i in range(path_points.size()-1):
		path_points[i].update(delta)
		if path_points[i].age <= 0:
			path_points.remove(i)
			

func render():
	if path_points.size() < 2:
		clear()
		return

#	path_points = [Vector3(-5, 2, 0),Vector3(-5, 2, 0),Vector3(5, 2, 0)]
	var to_be_rendered: Array = []
	for point in path_points:
		to_be_rendered.append(point.position)
	to_be_rendered = chaikin(to_be_rendered, smoothing_iterations)
	
	var points_to_render: int = to_be_rendered.size()
#	var tiling_factor: float = segments*max_distance/base_width if tiled_texture else 0
	var step: float = 1.0/(points_to_render-1)
	var factor: float = 0
	var wire_points: Array = []
	var _u = 0
	
	clear()
	begin(Mesh.PRIMITIVE_TRIANGLE_STRIP, null)
	
	for i in range(1, to_be_rendered.size()):
		var mapped_index = floor(float(i) / points_to_render * path_points.size())
		var normal = Vector3()
		if alignment == "Motion":
			normal = path_points[mapped_index].normal
		
		elif alignment == "View":
			var path_direction = (to_be_rendered[i] - to_be_rendered[i-1]).normalized()
			var cam_pos = get_viewport().get_camera().get_global_transform().origin
			normal = (cam_pos - (to_be_rendered[i] + to_be_rendered[i-1])/2).cross(path_direction).normalized()
		
		else:
			normal = target.get_global_transform().basis.y.normalized()

		var rr = 1-factor
		var width = base_width
		if width_profile:
			width = base_width * width_profile.interpolate(rr)
		if width_over_time:
			var fact = 1 - path_points[mapped_index].age/life_time
			width = width * width_over_time.interpolate(fact)
			
		var color = Color(1, 1, 1)
		if color_gradient:
			color = color_gradient.interpolate(rr)
		
		# --------------------------RENDERING----------------------------
		var p1 = to_be_rendered[i] - normal*width/2
		var p2 = to_be_rendered[i] + normal*width/2
		var u: float = factor
		
		if tiled_texture:
			if tiling:
				u *= tiling
			else:
				_u += (to_be_rendered[i] - to_be_rendered[i-1]).length()/base_width
				u = _u
		
		set_color(color)
		set_uv(Vector2(u, 0))
		add_vertex(p1)
		set_uv(Vector2(u, 1))
		add_vertex(p2)
		factor += step
		
		wire_points += [p1, p2]
	end()
	
	if show_wireframe:
		begin(Mesh.PRIMITIVE_LINE_STRIP, null)
		set_color(wireframe_color)
		for i in range(1, wire_points.size()-2, 2):
			## i-1, i+1, i, i+2
			add_vertex(wire_points[i-1])
			add_vertex(wire_points[i+1])
			add_vertex(wire_points[i])
			add_vertex(wire_points[i+2])
		end()


func chaikin(points, iterations):
	""" Chaikin’s Algorithms for curves """
	if points.size() > 1:
		if (iterations == 0):
			return points
		
		var result = [points[0]]
		for i in range(0, points.size()-1):
			result += chaikin_cut(points[i], points[i+1])
		result += [points[points.size()-1]]
		
		return chaikin(result, iterations-1)
	return points
	
func chaikin_cut(a, b):
	""" Cutting one segment """
	var ratio = clamp(smoothing_ratio, 0, 1)
	if (ratio > 0.5): ratio = 1 - ratio;
	
	# Find point at a given ratio going from A to B
	var p1 = a.linear_interpolate(b, ratio)
	# Find point at a given ratio going from B to A
	var p2 = b.linear_interpolate(a, ratio)

	return [p1, p2]

