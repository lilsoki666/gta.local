__version__ = "0.3.0"

import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Triangle, Rectangle, Ellipse, Line
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


# Kota Nusantara 3D prototype 0.3
# Lightweight polygon-based 3D projection using Kivy canvas.
# This is a 3D-style prototype, not a hardware-accelerated 3D engine.

ROAD_HALF = 4.0
FOCAL_LENGTH = 520.0
VIEW_DISTANCE = 55.0
CAMERA_DISTANCE = 6.0
CAMERA_HEIGHT = 2.7
CAMERA_SENSITIVITY = 0.0015
JOYSTICK_RADIUS = dp(42)
JOYSTICK_DEADZONE = 0.12


class World3D(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.px = 0.0
        self.py = 0.0
        self.player_yaw = 0.0
        self.camera_yaw = 0.0
        self.camera_pitch = 0.17

        self.move_x = 0.0
        self.move_y = 0.0
        self.sprinting = False

        self.jump_time = 0.0
        self.jump_duration = 0.72
        self.jump_height = 1.45
        self.is_jumping = False

        self.left_touch = None
        self.right_touch = None
        self.joy_center = (0.0, 0.0)
        self.joy_pos = (0.0, 0.0)
        self.last_right_x = 0.0

        self.projectiles = []
        self.shot_flash = 0.0
        self.action_message = ""
        self.message_time = 0.0

        self.objects = []
        self.make_city()
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def make_city(self):
        random.seed(17)
        self.objects.clear()
        colors = [
            (0.78, 0.59, 0.39), (0.78, 0.75, 0.63),
            (0.68, 0.38, 0.29), (0.43, 0.61, 0.51),
            (0.83, 0.73, 0.49), (0.62, 0.68, 0.68),
            (0.77, 0.77, 0.70)
        ]

        # Low-poly Indonesian shop houses on both sides of the road.
        for row in range(-14, 25):
            y = row * 8.0 + 4.0
            for side in (-1, 1):
                x = side * random.uniform(7.8, 10.2)
                w = random.uniform(2.6, 3.8)
                d = random.uniform(3.2, 4.6)
                h = random.uniform(3.0, 5.8)
                color = random.choice(colors)
                self.add_box(x, y, 0, w, d, h, color, "building")
                # Flat roof and simple dark doorway.
                roof = tuple(max(0.04, c * 0.68) for c in color)
                self.add_box(x, y, h, w + 0.12, d + 0.12, 0.18, roof, "roof")
                self.add_box(x, y - d / 2 - 0.015, 0, 0.62, 0.035,
                             min(1.8, h * 0.55), (0.19, 0.16, 0.13), "door")

            # Trees between sidewalk and houses.
            for side in (-1, 1):
                tx = side * random.uniform(5.35, 6.15)
                ty = y + random.uniform(-2.2, 2.2)
                self.add_box(tx, ty, 0, 0.25, 0.25, 1.55,
                             (0.35, 0.21, 0.11), "trunk")
                # Faceted, chunky canopy approximation.
                self.add_box(tx, ty, 1.25, 1.35, 1.35, 1.45,
                             random.choice([(0.12, 0.39, 0.17),
                                            (0.15, 0.44, 0.20),
                                            (0.18, 0.35, 0.13)]), "leaf")

    def add_box(self, x, y, z, w, d, h, color, kind):
        self.objects.append({
            "x": x, "y": y, "z": z, "w": w, "d": d, "h": h,
            "color": color, "kind": kind
        })

    @property
    def center_x(self):
        return self.x + self.width * 0.5

    @property
    def center_y(self):
        return self.y + self.height * 0.47

    def project(self, x, y, z):
        # Camera looks toward the road direction. Screen Y sign is important:
        # near ground must project toward the bottom, distant ground toward horizon.
        a = self.camera_yaw
        cam_x = self.px - math.sin(a) * CAMERA_DISTANCE
        cam_y = self.py - math.cos(a) * CAMERA_DISTANCE
        cam_z = CAMERA_HEIGHT

        dx, dy, dz = x - cam_x, y - cam_y, z - cam_z
        right_x, right_y = math.cos(a), -math.sin(a)
        camera_x = dx * right_x + dy * right_y
        forward = dx * math.sin(a) + dy * math.cos(a)

        pitch = self.camera_pitch
        depth = forward * math.cos(pitch) - dz * math.sin(pitch)
        vertical = forward * math.sin(pitch) + dz * math.cos(pitch)

        if depth <= 0.25:
            return None
        scale = FOCAL_LENGTH / depth
        sx = self.center_x + camera_x * scale
        sy = self.center_y + vertical * scale

        if sx < self.x - self.width or sx > self.right + self.width:
            return None
        if sy < self.y - self.height or sy > self.top + self.height:
            return None
        return (sx, sy, depth)

    def draw_face(self, vertices, color):
        projected = [self.project(*v) for v in vertices]
        if any(p is None for p in projected):
            return
        Color(*color)
        Triangle(points=[
            projected[0][0], projected[0][1],
            projected[1][0], projected[1][1],
            projected[2][0], projected[2][1],
        ])
        Triangle(points=[
            projected[0][0], projected[0][1],
            projected[2][0], projected[2][1],
            projected[3][0], projected[3][1],
        ])

    def box_faces(self, obj):
        x, y, z = obj["x"], obj["y"], obj["z"]
        w, d, h = obj["w"], obj["d"], obj["h"]
        x1, x2 = x - w / 2, x + w / 2
        y1, y2 = y - d / 2, y + d / 2
        z1, z2 = z, z + h
        c = obj["color"]
        dark = tuple(v * 0.69 for v in c)
        mid = tuple(v * 0.84 for v in c)
        return [
            ([(x1,y1,z1),(x2,y1,z1),(x2,y1,z2),(x1,y1,z2)], dark),
            ([(x2,y1,z1),(x2,y2,z1),(x2,y2,z2),(x2,y1,z2)], mid),
            ([(x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)], c),
            ([(x1,y2,z1),(x2,y2,z1),(x2,y2,z2),(x1,y2,z2)], mid),
        ]

    def draw_ground_and_road(self):
        # Draw finite ground tiles so the road and terrain share world coordinates.
        for row in range(-4, 20):
            y1 = self.py + row * 5.0
            y2 = y1 + 5.0
            self.draw_face([
                (-55, y1, -0.04), (55, y1, -0.04),
                (55, y2, -0.04), (-55, y2, -0.04)
            ], (0.25, 0.43, 0.24))

        # Road surface is exactly at ground level, not a floating board.
        y1, y2 = self.py - 24, self.py + 82
        self.draw_face([
            (-ROAD_HALF, y1, 0.015), (ROAD_HALF, y1, 0.015),
            (ROAD_HALF, y2, 0.015), (-ROAD_HALF, y2, 0.015)
        ], (0.17, 0.19, 0.20))

        for side in (-1, 1):
            self.draw_face([
                (side * 4.0, y1, 0.03), (side * 5.0, y1, 0.03),
                (side * 5.0, y2, 0.03), (side * 4.0, y2, 0.03)
            ], (0.58, 0.56, 0.49))

        for mark_y in range(int(self.py) - 20, int(self.py) + 82, 7):
            self.draw_face([
                (-0.075, mark_y, 0.045), (0.075, mark_y, 0.045),
                (0.075, mark_y + 2.7, 0.045), (-0.075, mark_y + 2.7, 0.045)
            ], (0.95, 0.84, 0.51))

    def draw_player(self):
        # A visibly three-dimensional low-poly person made from projected box faces.
        bob = 0.0
        if self.is_jumping:
            t = min(1.0, self.jump_time / self.jump_duration)
            bob = math.sin(math.pi * t) * self.jump_height

        x, y = self.px, self.py
        body = {
            "x": x, "y": y, "z": 0.28 + bob,
            "w": 0.52, "d": 0.36, "h": 0.78,
            "color": (0.12, 0.30, 0.72), "kind": "player"
        }
        head = {
            "x": x, "y": y, "z": 1.10 + bob,
            "w": 0.34, "d": 0.32, "h": 0.34,
            "color": (0.70, 0.47, 0.31), "kind": "player"
        }
        legs = [
            {"x": x - 0.14, "y": y, "z": 0.02 + bob, "w": 0.17,
             "d": 0.24, "h": 0.32, "color": (0.10,0.12,0.15), "kind":"player"},
            {"x": x + 0.14, "y": y, "z": 0.02 + bob, "w": 0.17,
             "d": 0.24, "h": 0.32, "color": (0.10,0.12,0.15), "kind":"player"},
        ]
        for obj in [body, head] + legs:
            for vertices, color in self.box_faces(obj):
                self.draw_face(vertices, color)

        # Small aiming indicator in front of the character.
        fx = x + math.sin(self.player_yaw) * 0.75
        fy = y + math.cos(self.player_yaw) * 0.75
        p1 = self.project(x, y, 1.15 + bob)
        p2 = self.project(fx, fy, 1.15 + bob)
        if p1 and p2:
            Color(1.0, 0.85, 0.25, 0.9)
            Line(points=[p1[0], p1[1], p2[0], p2[1]], width=1.5)

    def fire_weapon(self):
        # Non-graphic arcade projectile for prototype testing.
        a = self.player_yaw
        self.projectiles.append({
            "x": self.px, "y": self.py,
            "vx": math.sin(a) * 18.0,
            "vy": math.cos(a) * 18.0,
            "life": 1.1
        })
        self.shot_flash = 0.12
        self.show_message("TEMBAKAN!")

    def interact(self):
        self.show_message("BELUM ADA OBJEK INTERAKTIF DI DEKATMU")

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_time = 0.0

    def show_message(self, text):
        self.action_message = text
        self.message_time = 1.4

    def update(self, dt):
        dt = min(dt, 0.05)
        speed = 8.0 if self.sprinting else 4.5

        # Input is camera-relative; camera orbit stays independent of player facing.
        heading = self.camera_yaw
        dx = math.sin(heading) * self.move_y + math.cos(heading) * self.move_x
        dy = math.cos(heading) * self.move_y - math.sin(heading) * self.move_x
        mag = math.hypot(dx, dy)
        if mag > 1:
            dx, dy = dx / mag, dy / mag

        if mag > JOYSTICK_DEADZONE:
            nx = self.px + dx * speed * dt
            ny = self.py + dy * speed * dt
            if self.clear_position(nx, self.py):
                self.px = nx
            if self.clear_position(self.px, ny):
                self.py = ny
            self.player_yaw = math.atan2(dx, dy)

        if self.is_jumping:
            self.jump_time += dt
            if self.jump_time >= self.jump_duration:
                self.is_jumping = False
                self.jump_time = 0.0

        for projectile in self.projectiles:
            projectile["x"] += projectile["vx"] * dt
            projectile["y"] += projectile["vy"] * dt
            projectile["life"] -= dt
        self.projectiles = [p for p in self.projectiles if p["life"] > 0]
        self.shot_flash = max(0.0, self.shot_flash - dt)
        self.message_time = max(0.0, self.message_time - dt)

        self.draw_world()

    def clear_position(self, x, y):
        # Player stays in the road + sidewalk corridor for this first prototype.
        if abs(x) > 4.75:
            return False
        for obj in self.objects:
            if obj["kind"] != "building":
                continue
            if (abs(x - obj["x"]) < obj["w"] / 2 + 0.38 and
                abs(y - obj["y"]) < obj["d"] / 2 + 0.38):
                return False
        return True

    def draw_world(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.43, 0.70, 0.86)
            Rectangle(pos=self.pos, size=self.size)

            self.draw_ground_and_road()

            visible = []
            for obj in self.objects:
                dist = math.hypot(obj["x"] - self.px, obj["y"] - self.py)
                if dist < VIEW_DISTANCE:
                    visible.append((dist, obj))
            visible.sort(key=lambda item: item[0], reverse=True)
            for _, obj in visible:
                for vertices, color in self.box_faces(obj):
                    self.draw_face(vertices, color)

            for p in self.projectiles:
                q = self.project(p["x"], p["y"], 1.0)
                if q:
                    Color(1.0, 0.75, 0.12, min(1, p["life"] * 2))
                    Ellipse(pos=(q[0]-dp(3), q[1]-dp(3)), size=(dp(6), dp(6)))

            self.draw_player()

            # Joystick visual.
            if self.left_touch is not None:
                jx, jy = self.joy_center
            else:
                jx, jy = self.x + dp(76), self.y + dp(76)
            Color(1, 1, 1, 0.19)
            Ellipse(pos=(jx-dp(42), jy-dp(42)), size=(dp(84), dp(84)))
            kx, ky = self.joy_pos if self.left_touch is not None else (jx, jy)
            Color(1, 1, 1, 0.48)
            Ellipse(pos=(kx-dp(16), ky-dp(16)), size=(dp(32), dp(32)))


class NusantaraApp(App):
    def build(self):
        Window.clearcolor = (0.43, 0.70, 0.86, 1)
        root = FloatLayout()
        self.world = World3D(size_hint=(1, 1))
        root.add_widget(self.world)

        self.add_label(root, "[b]KOTA NUSANTARA[/b]  [size=11]PROTOTYPE 0.3[/size]",
                       {"x": 0.025, "top": 0.98}, (dp(300), dp(42)), "left")
        self.status = self.add_label(root, "KECEPATAN: 0 km/jam",
                       {"right": 0.98, "top": 0.98}, (dp(230), dp(40)), "right")

        self.add_button(root, "LARI", {"right": 0.96, "y": 0.12},
                        (dp(86), dp(54)),
                        lambda *_: setattr(self.world, "sprinting", True),
                        lambda *_: setattr(self.world, "sprinting", False))
        self.add_button(root, "LOMPAT", {"right": 0.96, "y": 0.29},
                        (dp(86), dp(54)),
                        lambda *_: self.world.jump())
        self.add_button(root, "SENJATA", {"right": 0.96, "y": 0.46},
                        (dp(86), dp(54)),
                        lambda *_: self.world.fire_weapon())
        self.add_button(root, "AKSI", {"right": 0.96, "y": 0.63},
                        (dp(86), dp(54)),
                        lambda *_: self.world.interact())

        self.message = self.add_label(root, "", {"center_x": 0.5, "y": 0.12},
                                      (dp(440), dp(40)), "center")
        Clock.schedule_interval(self.update_hud, 0.15)
        return root

    def add_label(self, root, text, pos_hint, size, align):
        label = Label(
            text=text, markup=True, size_hint=(None, None),
            size=size, pos_hint=pos_hint, halign=align, valign="middle",
            color=(1, 1, 1, 1)
        )
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        root.add_widget(label)
        return label

    def add_button(self, root, text, pos_hint, size, on_press, on_release=None):
        button = Button(
            text=text, size_hint=(None, None), size=size, pos_hint=pos_hint,
            background_normal="", background_down="",
            background_color=(0.05, 0.19, 0.31, 0.94),
            color=(1, 1, 1, 1), font_size=dp(13)
        )
        button.bind(on_press=on_press)
        if on_release:
            button.bind(on_release=on_release)
        root.add_widget(button)
        return button

    def update_hud(self, dt):
        w = self.world
        strength = min(1.0, math.hypot(w.move_x, w.move_y))
        speed = (8.0 if w.sprinting else 4.5) * strength
        self.status.text = f"KECEPATAN: {int(speed * 3.6)} km/jam"
        self.message.text = w.action_message if w.message_time > 0 else ""


if __name__ == "__main__":
    NusantaraApp().run()
