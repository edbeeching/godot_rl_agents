extends ImmediateGeometry
tool

var points := []

func remove_points():
    points = []
    clear()
    
func add_point(start : Vector3, end: Vector3) ->void:
    points.append([start, end])
    clear()
    begin(Mesh.PRIMITIVE_LINES)
    for point in points:
        
        var start_v = point[0]
        var end_v = point[1]
        #var result = space_state.intersect_ray(start_v, end_v)
        set_color(Color.aqua)
        add_vertex(start_v)
        add_vertex(end_v)
#        if result:
#            add_vertex(result.position)
#        else:
#            add_vertex(end_v)
    end()
#
#func _physics_process(delta) -> void:
#    #var space_state = get_world().direct_space_state
#    clear()
#    begin(Mesh.PRIMITIVE_LINES)
#    for point in points:
#
#        var start_v = point[0]
#        var end_v = point[1]
#        print(start_v,end_v)
#        #var result = space_state.intersect_ray(start_v, end_v)
#        set_color(Color.yellow)
#        add_vertex(start_v)
#        add_vertex(end_v)
##        if result:
##            add_vertex(result.position)
##        else:
##            add_vertex(end_v)
#    end()

