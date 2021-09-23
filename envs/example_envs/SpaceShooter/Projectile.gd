extends Area2D


export var speed = 500
export var lifetime = 1.0
onready var anim = $AnimatedSprite
var _shooter = null
var _episode_index = -1 # required if agent is reset before projectile impacts
func _ready():
    anim.play("default")

func set_shooter(shooter: BasePlayer):
    _shooter = shooter
    _episode_index = shooter.episode_index

func _physics_process(delta):
    position += transform.x * speed * delta


func _on_Projectile_body_entered(body):
    if body.is_in_group("player"):
        if body._team != _shooter._team:
            if _shooter.episode_index == _episode_index:
                _shooter.hit_enemy()
                body.hit_by_enemy(_shooter) # in case of kill, need to inform shooter
            else:
                body.hit_by_enemy(null) # in case of kill, no need to inform shooter
            
            queue_free()
        return

    queue_free()


func _on_Timer_timeout():
    queue_free()
