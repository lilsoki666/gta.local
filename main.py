
__version__ = "0.1.0"

import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Triangle, Line, Ellipse, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.metrics import dp


# ------------------------------------------
# KOTA NUSANTARA 3D - PROTOTYPE 0.1
# ------------------------------------------

WORLD_SEED = 17
random.seed(WORLD_SEED)

ROAD_HALF = 4.0
BUILDING_ROWS = 7
ROW_GAP = 9.0
FOCAL_LENGTH = 430.0


class World3D(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.px = 0.0
        self.py = 0.0
        self.yaw = 0.0

        self.move_x = 0.0
        self.move_y = 0.0
        self.sprinting = False

        self.camera_yaw = 0.0
        self.camera_pitch = 0.20

        self.left_touch = None
        self.right_touch = None
        self.last_right_x = 0.0
        self.joy_center = (0, 0)
        self.joy_pos = (0, 0)

        self.objects = []
        self.make_city()

        Clock.schedule_interval(self.update, 1 / 30)

    def make_city(self):
        self.objects.clear()

        # Rumah toko dan rumah warga di kedua sisi jalan.
        colors = [
            (0.80, 0.62, 0.40),
            (0.78, 0.76, 0.65),
            (0.72, 0.42, 0.30),
            (0.48, 0.66, 0.55),
            (0.85, 0.76, 0.50),
        ]

        for row in range(-BUILDING_ROWS, BUILDING_ROWS + 1):
            y = row * ROW_GAP

            if abs(y) < 1:
                continue

            for side in (-1, 1):
                x = side * random.uniform(6.0, 8.5)
                w = random.uniform(2.5, 3.5)
                d = random.uniform(3.0, 5.0)
                h = random.uniform(3.0, 6.0)
                color = random.choice(colors)

                self.add_box(
                    x, y, 0, w, d, h, color, "building"
                )

                # Atap sederhana.
                roof = (
                    min(color[0] * 0.68, 1),
                    min(color[1] * 0.68, 1),
                    min(color[2] * 0.68, 1),
                )
                self.add_box(
                    x, y, h, w + 0.15, d + 0.15,
                    0.18, roof, "roof"
                )

            # Pohon tropis.
            for side in (-1, 1):
                tx = side * random.uniform(4.6, 5.5)
                ty = y + random.uniform(-2.5, 2.5)
                self.add_box(
                    tx, ty, 0, 0.22, 0.22, 1.5,
                    (0.38, 0.22, 0.10), "tree"
                )
                self.add_box(
                    tx, ty, 1.25, 1.0, 1.0, 1.4,
                    (0.15, 0.46, 0.20), "leaf"
                )

    def add_box(self, x, y, z, w, d, h, color, kind):
        self.objects.append({
            "x": x, "y": y, "z": z,
            "w": w, "d": d, "h": h,
            "color": color, "kind": kind
        })

    def update(self, dt):
        dt = min(dt, 0.05)

        # Joystick: bergerak relatif terhadap arah kamera.
        speed = 5.5 if not self.sprinting else 8.0
        forward = self.move_y
        strafe = self.move_x

        angle = self.yaw
        dx = (
            math.sin(angle) * forward
            + math.cos(angle) * strafe
        )
        dy = (
            math.cos(angle) * forward
            - math.sin(angle) * strafe
        )

        length = math.sqrt(dx * dx + dy * dy)
        if length > 1:
            dx /= length
            dy /= length

        nx = self.px + dx * speed * dt
        ny = self.py + dy * speed * dt

        # Tabrakan sederhana dengan bangunan.
        if abs(nx) < 4.0:
            self.px = nx
        if self.clear_position(nx, ny):
            self.px = nx
            self.py = ny
        elif self.clear_position(self.px, ny):
            self.py = ny

        if length > 0.12:
            self.yaw = math.atan2(dx, dy)

        self.draw_world()

    def clear_position(self, x, y):
        for obj in self.objects:
            if obj["kind"] != "building":
                continue

            if (
                abs(x - obj["x"]) < obj["w"] / 2 + 0.45
                and abs(y - obj["y"]) < obj["d"] / 2 + 0.45
            ):
                return False

        return True

    def project(self, x, y, z):
        # Kamera mengikuti pemain dari belakang.
        cyaw = self.yaw + self.camera_yaw

        cam_x = self.px - math.sin(cyaw) * 6.5
        cam_y = self.py - math.cos(cyaw) * 6.5
        cam_z = 3.0

        dx = x - cam_x
        dy = y - cam_y
        dz = z - cam_z

        right_x = math.cos(cyaw)
        right_y = -math.sin(cyaw)

        cx = dx * right_x + dy * right_y
        forward = dx * math.sin(cyaw) + dy * math.cos(cyaw)

        pitch = 0.28
        depth = forward * math.cos(pitch) - dz * math.sin(pitch)
        vertical = forward * math.sin(pitch) + dz * math.cos(pitch)

        if depth < 0.35:
            return None

        scale = FOCAL_LENGTH / depth
        sx = self.center_x + cx * scale
        sy = self.center_y - vertical * scale

        return (sx, sy, depth)

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height * 0.53

    def draw_triangle(self, points, color):
        projected = [
            self.project(*p) for p in points
        ]
        if any(p is None for p in projected):
            return

        pts = []
        for p in projected:
            pts.extend([p[0], p[1]])

        Color(*color)
        Triangle(points=pts)

    def draw_face(self, vertices, color, depth):
        # Permukaan segiempat dibagi menjadi dua segitiga.
        self.draw_triangle(
            [vertices[0], vertices[1], vertices[2]], color
        )
        self.draw_triangle(
            [vertices[0], vertices[2], vertices[3]], color
        )

    def box_faces(self, o):
        x, y, z = o["x"], o["y"], o["z"]
        w, d, h = o["w"], o["d"], o["h"]

        x1, x2 = x - w / 2, x + w / 2
        y1, y2 = y - d / 2, y + d / 2
        z1, z2 = z, z + h

        c = o["color"]

        # Warna berbeda per sisi untuk efek low-poly.
        side_a = tuple(v * 0.72 for v in c)
        side_b = tuple(v * 0.86 for v in c)

        return [
            ([(x1,y1,z1),(x2,y1,z1),(x2,y1,z2),(x1,y1,z2)], side_a),
            ([(x2,y1,z1),(x2,y2,z1),(x2,y2,z2),(x2,y1,z2)], side_b),
            ([(x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)], c),
        ]

    def draw_world(self):
        self.canvas.clear()

        with self.canvas:
            # Langit dan tanah.
            Color(0.47, 0.72, 0.89)
            Rectangle(
                pos=self.pos,
                size=(self.width, self.height)
            )

            Color(0.30, 0.53, 0.29)
            Rectangle(
                pos=(self.x, self.y),
                size=(self.width, self.height * 0.43)
            )

            # Jalan digambar sebagai bidang perspektif.
            road = [
                (-ROAD_HALF, self.py - 15, 0.02),
                ( ROAD_HALF, self.py - 15, 0.02),
                ( ROAD_HALF, self.py + 70, 0.02),
                (-ROAD_HALF, self.py + 70, 0.02),
            ]
            self.draw_face(road, (0.22, 0.23, 0.24), 0)

            # Trotoar.
            for side in (-1, 1):
                sidewalk = [
                    (side * 4, self.py - 15, 0.04),
                    (side * 5, self.py - 15, 0.04),
                    (side * 5, self.py + 70, 0.04),
                    (side * 4, self.py + 70, 0.04),
                ]
                self.draw_face(
                    sidewalk, (0.62, 0.60, 0.52), 0
                )

            # Marka jalan.
            for y in range(
                int(self.py) - 10,
                int(self.py) + 70,
                5
            ):
                mark = [
                    (-0.07, y, 0.06),
                    (0.07, y, 0.06),
                    (0.07, y + 2, 0.06),
                    (-0.07, y + 2, 0.06),
                ]
                self.draw_face(mark, (0.94, 0.88, 0.60), 0)

            # Objek jauh digambar sebelum objek dekat.
            visible = []
            for obj in self.objects:
                dist = math.hypot(
                    obj["x"] - self.px,
                    obj["y"] - self.py
                )
                if dist < 42:
                    visible.append((dist, obj))

            visible.sort(reverse=True, key=lambda item: item[0])

            for _, obj in visible:
                for verts, col in self.box_faces(obj):
                    self.draw_face(verts, col, 0)

            # Karakter sederhana berbentuk badan dan kepala.
            x, y = self.px, self.py
            self.draw_triangle(
                [
                    (x - 0.30, y, 0.05),
                    (x + 0.30, y, 0.05),
                    (x, y + 0.10, 0.05),
                ],
                (0.10, 0.10, 0.10)
            )

            self.add_character_box(x, y)

            # HUD joystick.
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
            Color(1, 1, 1, 0.50)
            Ellipse(
                pos=(kx - dp(17), ky - dp(17)),
                size=(dp(34), dp(34))
            )

    def add_character_box(self, x, y):
        # Karakter low-poly terdiri dari beberapa bentuk sederhana.
        self.draw_triangle(
            [
                (x - 0.23, y + 0.10, 0.20),
                (x + 0.23, y + 0.10, 0.20),
                (x + 0.20, y + 0.10, 1.05),
            ],
            (0.12, 0.34, 0.66)
        )
        self.draw_triangle(
            [
                (x - 0.23, y + 0.10, 0.20),
                (x + 0.20, y + 0.10, 1.05),
                (x - 0.20, y + 0.10, 1.05),
            ],
            (0.18, 0.44, 0.80)
        )

        # Kepala.
        self.draw_triangle(
            [
                (x - 0.17, y + 0.10, 1.05),
                (x + 0.17, y + 0.10, 1.05),
                (x, y + 0.10, 1.38),
            ],
            (0.72, 0.48, 0.31)
        )

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        if touch.x < self.x + self.width * 0.45:
            self.left_touch = touch
            self.joy_center = touch.pos
            self.joy_pos = touch.pos
            touch.grab(self)
            return True

        self.right_touch = touch
        self.last_right_x = touch.x
        touch.grab(self)
        return True

    
def on_touch_move(self, touch):
    if touch.grab_current is not self:
        return super().on_touch_move(touch)

    if touch is self.left_touch:
        cx, cy = self.joy_center
        dx = (touch.x - cx) / dp(42)
        dy = (touch.y - cy) / dp(42)

        length = math.hypot(dx, dy)
        if length > 1:
            dx /= length
            dy /= length

        self.move_x = dx
        self.move_y = dy
        self.joy_pos = (
            cx + dx * dp(28),
            cy + dy * dp(28)
        )

    elif touch is self.right_touch:
        delta = touch.x - self.last_right_x

        # Kamera jauh lebih halus.
        delta = max(-40, min(40, delta))
        self.camera_yaw -= delta * 0.0015

        self.last_right_x = touch.x

    return True


    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)

        if touch is self.left_touch:
            self.left_touch = None
            self.move_x = 0
            self.move_y = 0

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
            text="[b]KOTA NUSANTARA[/b]  [size=12]PROTOTYPE 0.1[/size]",
            markup=True,
            size_hint=(None, None),
            size=(dp(260), dp(40)),
            pos_hint={"x": 0.02, "top": 0.98},
            halign="left",
        )
        root.add_widget(title)

        self.status = Label(
            text="JALAN: 0 km/jam",
            size_hint=(None, None),
            size=(dp(190), dp(35)),
            pos_hint={"right": 0.98, "top": 0.98},
        )
        root.add_widget(self.status)

        sprint = Button(
            text="LARI",
            size_hint=(None, None),
            size=(dp(78), dp(58)),
            pos_hint={"right": 0.96, "y": 0.12},
            background_color=(0.10, 0.45, 0.85, 0.90),
        )
        sprint.bind(
            on_press=lambda *_: setattr(
                self.world, "sprinting", True
            ),
            on_release=lambda *_: setattr(
                self.world, "sprinting", False
            ),
        )
        root.add_widget(sprint)

        Clock.schedule_interval(self.update_hud, 0.2)
        return root

    def update_hud(self, dt):
        w = self.world
        speed = math.hypot(w.move_x, w.move_y)
        speed *= 8.0 if w.sprinting else 5.5
        self.status.text = f"JALAN: {int(speed * 3.6)} km/jam"


if __name__ == "__main__":
    NusantaraApp().run()
