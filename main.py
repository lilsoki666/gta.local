__version__ = "0.2.0"

import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Triangle, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


# ============================================================
# KOTA NUSANTARA 3D - PROTOTYPE 0.2
# Lightweight procedural pseudo-3D prototype using Kivy canvas.
# This is not a full 3D engine; see README for known limitations.
# ============================================================

WORLD_SEED = 17
random.seed(WORLD_SEED)

ROAD_HALF = 4.0
FOCAL_LENGTH = 470.0
VIEW_DISTANCE = 48.0
CAMERA_DISTANCE = 6.0
CAMERA_HEIGHT = 2.8
CAMERA_SENSITIVITY = 0.0015
JOYSTICK_RADIUS = dp(42)
JOYSTICK_DEADZONE = 0.12


class World3D(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Player world coordinates. World Y is the road direction.
        self.px = 0.0
        self.py = 0.0
        self.player_yaw = 0.0

        # Camera orbit is independent from player facing.
        self.camera_yaw = 0.0
        self.camera_pitch = 0.16

        self.move_x = 0.0
        self.move_y = 0.0
        self.sprinting = False

        self.left_touch = None
        self.right_touch = None
        self.joy_center = (0.0, 0.0)
        self.joy_pos = (0.0, 0.0)
        self.last_right_x = 0.0

        self.objects = []
        self.make_city()
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def make_city(self):
        self.objects.clear()

        building_colors = [
            (0.78, 0.59, 0.39),
            (0.78, 0.75, 0.63),
            (0.68, 0.38, 0.29),
            (0.43, 0.61, 0.51),
            (0.83, 0.73, 0.49),
            (0.62, 0.68, 0.68),
        ]

        # Buildings are positioned outside the sidewalks.
        for row in range(-12, 13):
            y = row * 8.0
            if abs(y) < 5.0:
                continue

            for side in (-1, 1):
                x = side * random.uniform(7.1, 9.2)
                w = random.uniform(2.3, 3.3)
                d = random.uniform(2.8, 4.3)
                h = random.uniform(2.8, 5.3)
                color = random.choice(building_colors)

                self.add_box(x, y, 0, w, d, h, color, "building")

                roof_color = tuple(max(0.05, c * 0.68) for c in color)
                self.add_box(
                    x, y, h, w + 0.12, d + 0.12,
                    0.16, roof_color, "roof"
                )

            # Trees between buildings and sidewalk.
            for side in (-1, 1):
                tx = side * random.uniform(5.2, 6.0)
                ty = y + random.uniform(-2.0, 2.0)
                self.add_box(
                    tx, ty, 0, 0.22, 0.22, 1.35,
                    (0.34, 0.20, 0.10), "trunk"
                )
                self.add_box(
                    tx, ty, 1.2, 1.15, 1.15, 1.35,
                    (0.12, 0.39, 0.17), "leaf"
                )

    def add_box(self, x, y, z, w, d, h, color, kind):
        self.objects.append({
            "x": x, "y": y, "z": z,
            "w": w, "d": d, "h": h,
            "color": color, "kind": kind
        })

    def update(self, dt):
        dt = min(dt, 0.05)

        # Movement follows camera heading, not the player's previous heading.
        heading = self.camera_yaw
        speed = 8.0 if self.sprinting else 4.8

        forward = self.move_y
        strafe = self.move_x

        dx = math.sin(heading) * forward + math.cos(heading) * strafe
        dy = math.cos(heading) * forward - math.sin(heading) * strafe

        magnitude = math.hypot(dx, dy)
        if magnitude > 1.0:
            dx /= magnitude
            dy /= magnitude

        if magnitude > JOYSTICK_DEADZONE:
            nx = self.px + dx * speed * dt
            ny = self.py + dy * speed * dt

            # Separate-axis movement allows sliding along walls.
            if self.clear_position(nx, self.py):
                self.px = nx
            if self.clear_position(self.px, ny):
                self.py = ny

            # Character faces movement direction.
            self.player_yaw = math.atan2(dx, dy)

        self.draw_world()

    def clear_position(self, x, y):
        # Keep player on the street/sidewalk zone and out of buildings.
        if abs(x) > 5.15:
            return False

        for obj in self.objects:
            if obj["kind"] != "building":
                continue
            if (
                abs(x - obj["x"]) < obj["w"] / 2 + 0.40
                and abs(y - obj["y"]) < obj["d"] / 2 + 0.40
            ):
                return False
        return True

    @property
    def center_x(self):
        return self.x + self.width * 0.5

    @property
    def center_y(self):
        return self.y + self.height * 0.46

    def project(self, x, y, z):
        # Orbit camera follows the player while remaining independent of facing.
        angle = self.camera_yaw
        cam_x = self.px - math.sin(angle) * CAMERA_DISTANCE
        cam_y = self.py - math.cos(angle) * CAMERA_DISTANCE
        cam_z = CAMERA_HEIGHT

        dx = x - cam_x
        dy = y - cam_y
        dz = z - cam_z

        right_x = math.cos(angle)
        right_y = -math.sin(angle)
        camera_x = dx * right_x + dy * right_y
        forward = dx * math.sin(angle) + dy * math.cos(angle)

        pitch = self.camera_pitch
        depth = forward * math.cos(pitch) - dz * math.sin(pitch)
        vertical = forward * math.sin(pitch) + dz * math.cos(pitch)

        if depth <= 0.25:
            return None

        scale = FOCAL_LENGTH / depth
        sx = self.center_x + camera_x * scale
        sy = self.center_y - vertical * scale

        # Ignore objects far outside the screen to reduce drawing load.
        if sx < self.x - self.width or sx > self.right + self.width:
            return None
        if sy < self.y - self.height or sy > self.top + self.height:
            return None

        return (sx, sy, depth)

    def draw_face(self, vertices, color):
        projected = [self.project(*vertex) for vertex in vertices]
        if any(point is None for point in projected):
            return

        # Use two triangles. Kivy canvas has no 3D depth buffer here.
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
        side_a = tuple(max(0.0, v * 0.70) for v in c)
        side_b = tuple(max(0.0, v * 0.84) for v in c)

        # Front, side and top faces.
        return [
            ([(x1, y1, z1), (x2, y1, z1),
              (x2, y1, z2), (x1, y1, z2)], side_a),
            ([(x2, y1, z1), (x2, y2, z1),
              (x2, y2, z2), (x2, y1, z2)], side_b),
            ([(x1, y1, z2), (x2, y1, z2),
              (x2, y2, z2), (x1, y2, z2)], c),
        ]

    def draw_world(self):
        self.canvas.clear()

        with self.canvas:
            # Sky background.
            Color(0.46, 0.72, 0.88)
            Rectangle(pos=self.pos, size=self.size)

            # World ground plane, projected in the same coordinate system
            # as the road and buildings.
            ground = [
                (-65, self.py - 18, -0.03),
                (65, self.py - 18, -0.03),
                (65, self.py + 75, -0.03),
                (-65, self.py + 75, -0.03),
            ]
            self.draw_face(ground, (0.28, 0.48, 0.27))

            # Road and sidewalks sit just above ground level.
            road = [
                (-ROAD_HALF, self.py - 18, 0.01),
                (ROAD_HALF, self.py - 18, 0.01),
                (ROAD_HALF, self.py + 75, 0.01),
                (-ROAD_HALF, self.py + 75, 0.01),
            ]
            self.draw_face(road, (0.20, 0.22, 0.23))

            for side in (-1, 1):
                sidewalk = [
                    (side * 4.0, self.py - 18, 0.025),
                    (side * 5.0, self.py - 18, 0.025),
                    (side * 5.0, self.py + 75, 0.025),
                    (side * 4.0, self.py + 75, 0.025),
                ]
                self.draw_face(sidewalk, (0.61, 0.59, 0.51))

            # Dashed center line.
            for mark_y in range(int(self.py) - 15, int(self.py) + 75, 6):
                marking = [
                    (-0.07, mark_y, 0.05),
                    (0.07, mark_y, 0.05),
                    (0.07, mark_y + 2.5, 0.05),
                    (-0.07, mark_y + 2.5, 0.05),
                ]
                self.draw_face(marking, (0.93, 0.84, 0.54))

            # Approximate far-to-near painter's order.
            visible = []
            for obj in self.objects:
                distance = math.hypot(
                    obj["x"] - self.px,
                    obj["y"] - self.py
                )
                if distance <= VIEW_DISTANCE:
                    visible.append((distance, obj))
            visible.sort(key=lambda pair: pair[0], reverse=True)

            for _, obj in visible:
                for vertices, color in self.box_faces(obj):
                    self.draw_face(vertices, color)

            self.draw_player()

            # On-screen joystick base and knob.
            if self.left_touch is not None:
                jx, jy = self.joy_center
            else:
                jx, jy = self.x + dp(75), self.y + dp(75)

            Color(1, 1, 1, 0.20)
            Ellipse(
                pos=(jx - dp(42), jy - dp(42)),
                size=(dp(84), dp(84))
            )

            kx, ky = self.joy_pos
            if self.left_touch is None:
                kx, ky = jx, jy

            Color(1, 1, 1, 0.48)
            Ellipse(
                pos=(kx - dp(16), ky - dp(16)),
                size=(dp(32), dp(32))
            )

    def draw_player(self):
        x, y = self.px, self.py

        # Simplified body made from projected polygons.
        self.draw_face(
            [
                (x - 0.25, y, 0.12),
                (x + 0.25, y, 0.12),
                (x + 0.20, y, 0.98),
                (x - 0.20, y, 0.98),
            ],
            (0.12, 0.34, 0.72)
        )

        self.draw_face(
            [
                (x - 0.16, y, 0.98),
                (x + 0.16, y, 0.98),
                (x + 0.13, y, 1.30),
                (x - 0.13, y, 1.30),
            ],
            (0.72, 0.48, 0.31)
        )

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        # Left side: joystick. Right side: camera orbit.
        if touch.x < self.x + self.width * 0.43:
            self.left_touch = touch
            self.joy_center = touch.pos
            self.joy_pos = touch.pos
            touch.grab(self)
        else:
            self.right_touch = touch
            self.last_right_x = touch.x
            touch.grab(self)

        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_move(touch)

        if touch is self.left_touch:
            cx, cy = self.joy_center
            dx = (touch.x - cx) / JOYSTICK_RADIUS
            dy = (touch.y - cy) / JOYSTICK_RADIUS

            length = math.hypot(dx, dy)
            if length > 1.0:
                dx /= length
                dy /= length

            # Dead zone avoids tiny unintended movement.
            if math.hypot(dx, dy) < JOYSTICK_DEADZONE:
                dx, dy = 0.0, 0.0

            self.move_x = dx
            self.move_y = dy
            self.joy_pos = (
                cx + dx * dp(28),
                cy + dy * dp(28)
            )

        elif touch is self.right_touch:
            delta_x = touch.x - self.last_right_x
            delta_x = max(-40.0, min(40.0, delta_x))
            self.camera_yaw -= delta_x * CAMERA_SENSITIVITY
            self.last_right_x = touch.x

        return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)

        if touch is self.left_touch:
            self.left_touch = None
            self.move_x = 0.0
            self.move_y = 0.0

        if touch is self.right_touch:
            self.right_touch = None

        return True


class NusantaraApp(App):
    def build(self):
        Window.size = (960, 540)
        root = FloatLayout()

        self.world = World3D(size_hint=(1, 1))
        root.add_widget(self.world)

        title = Label(
            text="[b]KOTA NUSANTARA[/b]  [size=12]PROTOTYPE 0.2[/size]",
            markup=True,
            size_hint=(None, None),
            size=(dp(280), dp(42)),
            pos_hint={"x": 0.025, "top": 0.98},
            halign="left",
            valign="middle",
        )
        title.bind(size=lambda instance, value: setattr(
            instance, "text_size", value
        ))
        root.add_widget(title)

        self.status = Label(
            text="KECEPATAN: 0 km/jam",
            size_hint=(None, None),
            size=(dp(210), dp(38)),
            pos_hint={"right": 0.98, "top": 0.98},
            halign="right",
            valign="middle",
        )
        self.status.bind(size=lambda instance, value: setattr(
            instance, "text_size", value
        ))
        root.add_widget(self.status)

        sprint = Button(
            text="LARI",
            size_hint=(None, None),
            size=(dp(82), dp(58)),
            pos_hint={"right": 0.96, "y": 0.12},
            background_normal="",
            background_color=(0.07, 0.25, 0.40, 0.92),
        )
        sprint.bind(
            on_press=lambda *_: setattr(self.world, "sprinting", True),
            on_release=lambda *_: setattr(self.world, "sprinting", False),
        )
        root.add_widget(sprint)

        Clock.schedule_interval(self.update_hud, 0.2)
        return root

    def update_hud(self, dt):
        w = self.world
        input_strength = min(1.0, math.hypot(w.move_x, w.move_y))
        speed = (8.0 if w.sprinting else 4.8) * input_strength
        self.status.text = f"KECEPATAN: {int(speed * 3.6)} km/jam"


if __name__ == "__main__":
    NusantaraApp().run()
