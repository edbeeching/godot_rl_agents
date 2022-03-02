extends Node2D
tool
class_name DrawLine3D

class Line:
    var Start
    var End
    var LineColor
    var Time
    
    func _init(Start, End, LineColor, Time):
        self.Start = Start
        self.End = End
        self.LineColor = LineColor
        self.Time = Time

var Lines = []
var RemovedLine = false
var editor_viewport_2d = null
var editor_viewport_3d = null 
var editor_camera_3d = null

func _ready():
    editor_viewport_2d = find_viewport_2d(get_node("/root/EditorNode"), 0)
    editor_viewport_3d = find_viewport_3d(get_node("/root/EditorNode"), 0)
    editor_camera_3d = editor_viewport_3d.get_child(0)


func find_viewport_2d(node: Node, recursive_level):
    if node.get_class() == "CanvasItemEditor":
        return node.get_child(1).get_child(0).get_child(0).get_child(0).get_child(0)
    else:
        recursive_level += 1
        if recursive_level > 15:
            return null
        for child in node.get_children():
            var result = find_viewport_2d(child, recursive_level)
            if result != null:
                return result


func find_viewport_3d(node: Node, recursive_level):
    if node.get_class() == "SpatialEditor":
        return node.get_child(1).get_child(0).get_child(0).get_child(0).get_child(0).get_child(0)
    else:
        recursive_level += 1
        if recursive_level > 15:
            return null
        for child in node.get_children():
            var result = find_viewport_3d(child, recursive_level)
            if result != null:
                return result    

func _process(delta):
    for i in range(len(Lines)):
        Lines[i].Time -= delta
    
    if(len(Lines) > 0 || RemovedLine):
        update() #Calls _draw
        RemovedLine = false


func geteditorcamera(camera_index):
    return editor_camera_3d
    
func get_camera():
    if Engine.editor_hint:
        return geteditorcamera(0)   
    else:
        var Cam = get_viewport().get_camera()
        return Cam

func _draw():
    var Cam = get_camera()
    
    for i in range(len(Lines)):
        var ScreenPointStart = Cam.unproject_position(Lines[i].Start)
        var ScreenPointEnd = Cam.unproject_position(Lines[i].End)
        
        #Dont draw line if either start or end is considered behind the camera
        #this causes the line to not be drawn sometimes but avoids a bug where the
        #line is drawn incorrectly
        if(Cam.is_position_behind(Lines[i].Start) ||
            Cam.is_position_behind(Lines[i].End)):
            continue
        
        draw_line(ScreenPointStart, ScreenPointEnd, Lines[i].LineColor)
    
    #Remove lines that have timed out
    var i = Lines.size() - 1
    while (i >= 0):
        if(Lines[i].Time < 0.0):
            Lines.remove(i)
            RemovedLine = true
        i -= 1

func DrawLine(Start, End, LineColor, Time = 0.0):
    Lines.append(Line.new(Start, End, LineColor, Time))

func DrawRay(Start, Ray, LineColor, Time = 0.0):
    Lines.append(Line.new(Start, Start + Ray, LineColor, Time))

func DrawCube(Center, HalfExtents, LineColor, Time = 0.0):
    #Start at the 'top left'
    var LinePointStart = Center
    LinePointStart.x -= HalfExtents
    LinePointStart.y += HalfExtents
    LinePointStart.z -= HalfExtents
    
    #Draw top square
    var LinePointEnd = LinePointStart + Vector3(0, 0, HalfExtents * 2.0)
    DrawLine(LinePointStart, LinePointEnd, LineColor, Time);
    LinePointStart = LinePointEnd
    LinePointEnd = LinePointStart + Vector3(HalfExtents * 2.0, 0, 0)
    DrawLine(LinePointStart, LinePointEnd, LineColor, Time);
    LinePointStart = LinePointEnd
    LinePointEnd = LinePointStart + Vector3(0, 0, -HalfExtents * 2.0)
    DrawLine(LinePointStart, LinePointEnd, LineColor, Time);
    LinePointStart = LinePointEnd
    LinePointEnd = LinePointStart + Vector3(-HalfExtents * 2.0, 0, 0)
    DrawLine(LinePointStart, LinePointEnd, LineColor, Time);
    
    #Draw bottom square
    LinePointStart = LinePointEnd + Vector3(0, -HalfExtents * 2.0, 0)
    LinePointEnd = LinePointStart + Vector3(0, 0, HalfExtents * 2.0)
    DrawLine(LinePointStart, LinePointEnd, LineColor, Time);
    LinePointStart = LinePointEnd
    LinePointEnd = LinePointStart + Vector3(HalfExtents * 2.0, 0, 0)
    DrawLine(LinePointStart, LinePointEnd, LineColor, Time);
    LinePointStart = LinePointEnd
    LinePointEnd = LinePointStart + Vector3(0, 0, -HalfExtents * 2.0)
    DrawLine(LinePointStart, LinePointEnd, LineColor, Time);
    LinePointStart = LinePointEnd
    LinePointEnd = LinePointStart + Vector3(-HalfExtents * 2.0, 0, 0)
    DrawLine(LinePointStart, LinePointEnd, LineColor, Time);
    
    #Draw vertical lines
    LinePointStart = LinePointEnd
    DrawRay(LinePointStart, Vector3(0, HalfExtents * 2.0, 0), LineColor, Time)
    LinePointStart += Vector3(0, 0, HalfExtents * 2.0)
    DrawRay(LinePointStart, Vector3(0, HalfExtents * 2.0, 0), LineColor, Time)
    LinePointStart += Vector3(HalfExtents * 2.0, 0, 0)
    DrawRay(LinePointStart, Vector3(0, HalfExtents * 2.0, 0), LineColor, Time)
    LinePointStart += Vector3(0, 0, -HalfExtents * 2.0)
    DrawRay(LinePointStart, Vector3(0, HalfExtents * 2.0, 0), LineColor, Time)

