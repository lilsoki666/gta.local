extends CharacterBody3D

@export var walk_speed := 6.0
@export var jump_velocity := 5.2
var gravity := 18.0
var input_vector := Vector2.ZERO
var driving := false

func _ready():
    floor_snap_length = 0.4
    var body = MeshInstance3D.new()
    body.name = "PlayerMesh"
    var mesh = CapsuleMesh.new()
    mesh.radius = 0.34
    mesh.height = 1.65
    body.mesh = mesh
    var mat = StandardMaterial3D.new()
    mat.albedo_color = Color(0.12, 0.27, 0.72)
    body.material_override = mat
    body.position.y = 0.85
    add_child(body)
    var head = MeshInstance3D.new()
    var hm = SphereMesh.new()
    hm.radius = 0.27
    head.mesh = hm
    head.position.y = 1.75
    var skin = StandardMaterial3D.new()
    skin.albedo_color = Color(0.75, 0.54, 0.38)
    head.material_override = skin
    add_child(head)

func _physics_process(delta):
    if not is_on_floor():
        velocity.y -= gravity * delta
    var dir = Vector3(input_vector.x, 0, input_vector.y)
    if dir.length() > 1: dir = dir.normalized()
    velocity.x = dir.x * walk_speed
    velocity.z = dir.z * walk_speed
    if input_vector.length() > 0.1:
        rotation.y = lerp_angle(rotation.y, atan2(-dir.x, -dir.z), delta*8.0)
    move_and_slide()

func jump():
    if is_on_floor():
        velocity.y = jump_velocity
