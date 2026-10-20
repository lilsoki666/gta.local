extends Node3D

@onready var player: CharacterBody3D = $Player
@onready var camera: Camera3D = $Camera3D
@onready var status_label: Label = $HUD/Status
@onready var minimap: Control = $HUD/MiniMap
var driving_mode := false
var sprinting := false
var shooting_flash := 0.0

func _ready():
    Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
    _build_world()
    _build_player()
    _build_camera()
    _build_hud()
    get_viewport().size_changed.connect(_layout_hud)

func _build_world():
    var world = Node3D.new()
    world.name = "World"
    world.set_script(load("res://scripts/World.gd"))
    add_child(world)

func _build_player():
    player.position = Vector3(0, 0.1, 18)
    player.add_to_group("player")

func _build_camera():
    camera.position = Vector3(0, 5.5, 27)
    camera.current = true
    camera.fov = 72

func _build_hud():
    var hud=CanvasLayer.new()
    hud.name="HUD"
    add_child(hud)
    var root=Control.new()
    root.name="Root"
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    hud.add_child(root)
    var status=Label.new()
    status.name="Status"
    status.text="KOTA NUSANTARA  |  HP 100  |  RP 2.500.000"
    status.add_theme_font_size_override("font_size",22)
    status.add_theme_color_override("font_color",Color.WHITE)
    status.add_theme_color_override("font_shadow_color",Color.BLACK)
    status.add_theme_constant_override("shadow_offset_x",2)
    status.position=Vector2(18,16)
    root.add_child(status)
    var map=Panel.new()
    map.name="MiniMap"
    map.custom_minimum_size=Vector2(145,145)
    map.position=Vector2(18,54)
    map.add_theme_stylebox_override("panel",_style(Color(0.06,0.08,0.08,0.86),Color(0.8,0.85,0.8),70))
    root.add_child(map)
    var mapdot=ColorRect.new()
    mapdot.color=Color(1,0.28,0.18)
    mapdot.size=Vector2(9,9)
    mapdot.position=Vector2(68,68)
    map.add_child(mapdot)
    var settings=_button("Settings","⚙",Vector2(-74,18),Vector2(54,54),root)
    settings.anchor_left=1; settings.anchor_right=1
    settings.pressed.connect(func(): status.text="PENGATURAN | Audio: ON | Grafik: Sedang")
    var joy=Panel.new()
    joy.name="JoystickPad"
    joy.custom_minimum_size=Vector2(150,150)
    joy.position=Vector2(28,-178)
    joy.anchor_top=1; joy.anchor_bottom=1
    joy.add_theme_stylebox_override("panel",_style(Color(0.1,0.12,0.14,0.4),Color(1,1,1,0.6),80))
    root.add_child(joy)
    var jlabel=Label.new()
    jlabel.text="◉"
    jlabel.add_theme_font_size_override("font_size",50)
    jlabel.position=Vector2(49,38)
    joy.add_child(jlabel)
    joy.gui_input.connect(_joystick_input)
    var actions=Control.new()
    actions.name="Actions"
    actions.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.add_child(actions)
    _button("Weapon","🔫",Vector2(-182,-278),Vector2(62,62),actions).pressed.connect(func(): status.text="Senjata dipilih: pistol")
    _button("Jump","↑",Vector2(-105,-200),Vector2(62,62),actions).pressed.connect(func(): player.jump())
    _button("Shoot","●",Vector2(-105,-120),Vector2(62,62),actions).pressed.connect(func(): _shoot())
    _button("Sprint","⚡",Vector2(-182,-120),Vector2(62,62),actions).pressed.connect(func(): _toggle_sprint())
    _button("Drive","CAR",Vector2(-260,-200),Vector2(62,62),actions).pressed.connect(func(): _toggle_drive())
    _layout_hud()

func _style(bg:Color, border:Color, radius:int):
    var s=StyleBoxFlat.new()
    s.bg_color=bg
    s.border_color=border
    s.set_border_width_all(2)
    s.set_corner_radius_all(radius)
    s.content_margin_left=8; s.content_margin_right=8
    return s

func _button(n:String, text_value:String, pos:Vector2, size_value:Vector2, parent:Control):
    var b=Button.new()
    b.name=n
    b.text=text_value
    b.custom_minimum_size=size_value
    b.size=size_value
    b.position=pos
    b.add_theme_font_size_override("font_size",20)
    b.add_theme_color_override("font_color",Color.WHITE)
    b.add_theme_stylebox_override("normal",_style(Color(0.07,0.1,0.13,0.75),Color(0.9,0.92,0.95,0.8),60))
    b.add_theme_stylebox_override("pressed",_style(Color(0.13,0.32,0.42,0.9),Color.WHITE,60))
    parent.add_child(b)
    return b

func _layout_hud():
    if not has_node("HUD/Root/Actions"): return
    var size=get_viewport().get_visible_rect().size
    var a=$HUD/Root/Actions
    var buttons={"Weapon":Vector2(size.x-188,size.y-292),"Jump":Vector2(size.x-110,size.y-215),"Shoot":Vector2(size.x-110,size.y-137),"Sprint":Vector2(size.x-188,size.y-137),"Drive":Vector2(size.x-266,size.y-215)}
    for n in buttons:
        a.get_node(n).position=buttons[n]
    $HUD/Root/Settings.position=Vector2(size.x-72,16)
    $HUD/Root/JoystickPad.position=Vector2(28,size.y-178)

func _joystick_input(event):
    var pad=$HUD/Root/JoystickPad
    if event is InputEventScreenTouch:
        if event.pressed:
            _set_joy_from_position(event.position,pad)
        else:
            player.input_vector=Vector2.ZERO
    elif event is InputEventScreenDrag:
        _set_joy_from_position(event.position,pad)

func _set_joy_from_position(pos:Vector2,pad:Control):
    var local=pos
    var center=pad.size/2
    var v=(local-center)/55.0
    player.input_vector=Vector2(clamp(v.x,-1,1),clamp(v.y,-1,1))

func _toggle_sprint():
    sprinting=!sprinting
    player.walk_speed=9.0 if sprinting else 6.0
    $HUD/Root/Status.text="SPRINT ON" if sprinting else "SPRINT OFF"

func _toggle_drive():
    driving_mode=!driving_mode
    $HUD/Root/Status.text="MODE KENDARAAN: AKTIF (kontrol dasar)" if driving_mode else "MODE JALAN KAKI"
    # Vehicle entry/physics is intentionally a prototype placeholder; see README.

func _shoot():
    $HUD/Root/Status.text="Pistol: 12 / 48  |  tembakan prototipe"
    shooting_flash=0.15

func _process(delta):
    var target=player.global_position+Vector3(0,4.5,8.5)
    camera.global_position=camera.global_position.lerp(target,delta*4.0)
    camera.look_at(player.global_position+Vector3(0,1,0),Vector3.UP)
    if shooting_flash>0:
        shooting_flash-=delta

func _input(event):
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode==KEY_SPACE: player.jump()
        if event.keycode==KEY_SHIFT: _toggle_sprint()
