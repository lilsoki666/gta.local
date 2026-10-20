extends Node3D

const HOUSE = preload("res://assets/models/house_shop.obj")
const OFFICE = preload("res://assets/models/office_block.obj")
const CAR = preload("res://assets/models/car_body.obj")

func _ready():
    _make_environment()
    _make_ground()
    _make_roads()
    _make_city()
    _make_trees()
    _make_car()

func _make_environment():
    var env = WorldEnvironment.new()
    var e = Environment.new()
    e.background_mode = Environment.BG_SKY
    e.sky = Sky.new()
    e.sky.sky_material = ProceduralSkyMaterial.new()
    e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    e.ambient_light_color = Color(0.72, 0.78, 0.84)
    e.ambient_light_energy = 0.7
    env.environment = e
    add_child(env)
    var sun = DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-48, -28, 0)
    sun.light_energy = 1.1
    add_child(sun)

func _mat(color: Color, rough=0.9):
    var m = StandardMaterial3D.new()
    m.albedo_color = color
    m.roughness = rough
    return m

func _box(parent, name, pos, size, color):
    var n = MeshInstance3D.new()
    n.name = name
    var mesh = BoxMesh.new()
    mesh.size = size
    n.mesh = mesh
    n.position = pos
    n.material_override = _mat(color)
    parent.add_child(n)
    return n

func _make_ground():
    _box(self, "Terrain", Vector3(0,-0.35,0), Vector3(240,0.5,240), Color(0.30,0.43,0.27))

func _make_roads():
    # connected cross-road, sidewalks, lane markings
    _box(self, "Road_NS", Vector3(0,-0.05,0), Vector3(12,0.12,220), Color(0.12,0.14,0.16))
    _box(self, "Road_EW", Vector3(0,-0.04,0), Vector3(220,0.13,12), Color(0.12,0.14,0.16))
    for i in range(-10,11):
        _box(self, "Dash_NS_%s" % i, Vector3(0,0.025,i*9), Vector3(0.18,0.025,4.2), Color(0.95,0.88,0.56))
        _box(self, "Dash_EW_%s" % i, Vector3(i*9,0.03,0), Vector3(4.2,0.025,0.18), Color(0.95,0.88,0.56))
    for side in [-1,1]:
        _box(self, "Sidewalk_NS_%s" % side, Vector3(side*7.2,0.02,0), Vector3(2.2,0.2,220), Color(0.55,0.55,0.51))
        _box(self, "Sidewalk_EW_%s" % side, Vector3(0,0.02,side*7.2), Vector3(220,0.2,2.2), Color(0.55,0.55,0.51))

func _make_city():
    var colors=[Color(0.78,0.69,0.53),Color(0.70,0.75,0.77),Color(0.82,0.76,0.63),Color(0.66,0.72,0.63),Color(0.76,0.63,0.55)]
    var idx=0
    for x in range(-4,5):
        for z in range(-4,5):
            if abs(x)<=1 or abs(z)<=1: continue
            var pos=Vector3(x*22,0,z*22)
            var h=HOUSE if (idx%3 != 0) else OFFICE
            var inst=MeshInstance3D.new()
            inst.name="Building_%02d" % idx
            inst.mesh=h
            inst.position=pos+Vector3(0,0,-2)
            inst.material_override=_mat(colors[idx%colors.size()])
            if idx%3==0: inst.scale=Vector3(1.15,1.0,1.15)
            add_child(inst)
            # windows as readable facade details
            var levels=3 if idx%3==0 else 2
            for level in range(levels):
                for w in range(3):
                    _box(self,"Window_%d_%d_%d"%(idx,level,w),pos+Vector3((w-1)*1.7,1.7+level*1.8,1.55),Vector3(1.0,0.85,0.08),Color(0.18,0.34,0.43))
            idx+=1

func _make_trees():
    for i in range(30):
        var x=float((i%6)-3)*18.0
        var z=float((i/6)-2)*24.0
        if abs(x)<9 or abs(z)<9: continue
        _box(self,"TreeTrunk_%d"%i,Vector3(x,1.2,z),Vector3(0.5,2.4,0.5),Color(0.32,0.20,0.12))
        var crown=MeshInstance3D.new()
        crown.name="TreeCrown_%d"%i
        var mesh=SphereMesh.new()
        mesh.radius=1.8
        mesh.height=3.5
        crown.mesh=mesh
        crown.position=Vector3(x,3.5,z)
        crown.material_override=_mat(Color(0.16,0.40,0.20))
        add_child(crown)

func _make_car():
    var car=Node3D.new()
    car.name="DrivableCar"
    car.position=Vector3(4,0.15,5)
    var body=MeshInstance3D.new()
    body.mesh=CAR
    body.material_override=_mat(Color(0.75,0.12,0.10),0.45)
    body.position.y=0.8
    car.add_child(body)
    _box(car,"Cabin",Vector3(0,1.65,0),Vector3(2.0,1.0,1.65),Color(0.16,0.28,0.35))
    for x in [-1.45,1.45]:
        for z in [-0.78,0.78]:
            var wheel=MeshInstance3D.new()
            var mesh=CylinderMesh.new()
            mesh.top_radius=0.38
            mesh.bottom_radius=0.38
            mesh.height=0.22
            wheel.mesh=mesh
            wheel.rotation_degrees.z=90
            wheel.position=Vector3(x,0.4,z)
            wheel.material_override=_mat(Color(0.06,0.06,0.06))
            car.add_child(wheel)
    add_child(car)
