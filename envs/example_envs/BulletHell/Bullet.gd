extends Spatial


export var speed = 10
export var lifetime = 1.0

var velocity = Vector3.ZERO


func _physics_process(delta):
    transform.origin += velocity * delta

func _on_Bullet_body_entered(body):
    queue_free()
    if body.is_in_group("player"):
        body.hit_by_bullet()
