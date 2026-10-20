
__version__ = "0.4.0"

import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, Triangle, Line
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout


FOCAL = 570.0
ROAD = 4.1


class World(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.px = 0.0
        self.py = 0.0
        self.yaw = 0.0
        self.player_yaw = 0.0

        self.mx = 0.0
        self.my = 0.0
        self.run = False

        self.joy_id = None
        self.look_id = None
        self.joy_origin = (0, 0)
        self.joy_knob = (0, 0)
        self.look_last = None

        self.jump = False
        self.jump_t = 0.0

        self.drive = False
        self.car_heading = 0.0
        self.car_speed = 0.0
        self.steer = 0

        self.health = 100
        self.money = 2500

        self.weapon = 0
        self.weapons = ["PISTOL", "SMG", "SHOTGUN"]
        self.ammo = [48, 120, 24]

        self.shots = []
        self.toast = ""
        self.toast_t = 0.0

        self.objs = []
        self.make_city()

        Clock.schedule_interval(self.tick, 1 / 30)

    @property
    def cx(self):
        return self.x + self.width / 2

    @property
    def cy(self):
        return self.y + self.height * 0.47

    def box(self, x, y, z, w, d, h, c, kind):
        self.objs.append({
            "x": x, "y": y, "z": z,
            "w": w, "d": d, "h": h,
            "c": c, "k": kind
        })

    def make_city(self):
        random.seed(44)

        palette = [
            (0.72, 0.62, 0.46),
            (0.73, 0.72, 0.61),
            (0.66, 0.39, 0.30),
            (0.48, 0.61, 0.52),
            (0.78, 0.70, 0.48),
            (0.54, 0.62, 0.64),
            (0.78, 0.75, 0.67),
        ]

        for i in range(-18, 55):
            y = i * 8.5 + 4

            for side in (-1, 1):
                x = side * random.uniform(7.5, 10.2)
                w = random.uniform(2.6, 3.8)
                d = random.uniform(3.5, 4.8)
                h = random.uniform(3.0, 5.7)
                c = random.choice(palette)

                self.box(x, y, 0, w, d, h, c, "building")

                roof = tuple(v * 0.65 for v in c)
                self.box(
                    x, y, h, w + 0.12, d + 0.12,
                    0.16, roof, "roof"
                )

                fy = y - side * (d / 2 + 0.03)

                self.box(
                    x, fy, 0.05, 0.58, 0.05,
                    1.5, (0.18, 0.13, 0.10), "door"
                )

                for wx in (-0.72, 0.72):
                    self.box(
                        x + wx, fy, 1.75,
                        0.48, 0.05, 0.55,
                        (0.24, 0.48, 0.58), "window"
                    )

            for side in (-1, 1):
                tx = side * random.uniform(5.25, 6.0)
                ty = y + random.uniform(-2, 2)

                self.box(
                    tx, ty, 0, 0.22, 0.22, 1.6,
                    (0.32, 0.19, 0.10), "trunk"
                )

                foliage = random.choice([
                    (0.10, 0.34, 0.14),
                    (0.14, 0.42, 0.18),
                    (0.18, 0.38, 0.13),
                ])

                self.box(
                    tx, ty, 1.2, 1.25, 1.25, 1.4,
                    foliage, "foliage"
                )

            if i % 4 == 0:
                side = random.choice([-1, 1])
                lx = side * 5
                ly = y + 2

                self.box(
                    lx, ly, 0, 0.1, 0.1, 3.5,
                    (0.28, 0.29, 0.28), "pole"
                )

                self.box(
                    lx - side * 0.25, ly, 3.4,
                    0.55, 0.18, 0.12,
                    (0.93, 0.81, 0.52), "lamp"
                )

    def project(self, x, y, z):
        a = self.yaw

        camx = self.px - math.sin(a) * 5.5
        camy = self.py - math.cos(a) * 5.5

        dx = x - camx
        dy = y - camy
        dz = z - 2.65

        side = dx * math.cos(a) - dy * math.sin(a)
        forward = dx * math.sin(a) + dy * math.cos(a)

        pitch = 0.14

        depth = (
            forward * math.cos(pitch)
            - dz * math.sin(pitch)
        )

        vert = (
            forward * math.sin(pitch)
            + dz * math.cos(pitch)
        )

        if depth < 0.25:
            return None

        scale = FOCAL / depth

        sx = self.cx + side * scale
        sy = self.cy + vert * scale

        if (
            sx < self.x - self.width
            or sx > self.right + self.width
            or sy < self.y - self.height
            or sy > self.top + self.height
        ):
            return None

        return sx, sy, depth

    def face(self, vertices, color):
        p = [self.project(*v) for v in vertices]

        if any(v is None for v in p):
            return

        Color(*color)

        Triangle(points=[
            p[0][0], p[0][1],
            p[1][0], p[1][1],
            p[2][0], p[2][1]
        ])

        Triangle(points=[
            p[0][0], p[0][1],
            p[2][0], p[2][1],
            p[3][0], p[3][1]
        ])

    def draw_box(self, obj):
        x = obj["x"]
        y = obj["y"]
        z = obj["z"]
        w = obj["w"]
        d = obj["d"]
        h = obj["h"]
        c = obj["c"]

        x1, x2 = x - w / 2, x + w / 2
        y1, y2 = y - d / 2, y + d / 2
        z1, z2 = z, z + h

        faces = [
            (
                [
                    (x1, y1, z1), (x2, y1, z1),
                    (x2, y1, z2), (x1, y1, z2)
                ],
                tuple(v * 0.7 for v in c)
            ),
            (
                [
                    (x2, y1, z1), (x2, y2, z1),
                    (x2, y2, z2), (x2, y1, z2)
                ],
                tuple(min(1, v * 1.12) for v in c)
            ),
            (
                [
                    (x1, y1, z2), (x2, y1, z2),
                    (x2, y2, z2), (x1, y2, z2)
                ],
                c
            ),
            (
                [
                    (x1, y2, z1), (x2, y2, z1),
                    (x2, y2, z2), (x1, y2, z2)
                ],
                tuple(v * 0.72 for v in c)
            )
        ]

        for vertices, color in faces:
            self.face(vertices, color)

    def ground(self):
        start = int(self.py // 12) * 12 - 30

        for i in range(13):
            y = start + i * 12

            color = (
                (0.24, 0.41, 0.23)
                if i % 2 else
                (0.27, 0.44, 0.25)
            )

            self.face([
                (-45, y, -0.03),
                (45, y, -0.03),
                (45, y + 12, -0.03),
                (-45, y + 12, -0.03)
            ], color)

        y1 = self.py - 22
        y2 = self.py + 100

        # Jalan aspal
        self.face([
            (-ROAD, y1, 0.015),
            (ROAD, y1, 0.015),
            (ROAD, y2, 0.015),
            (-ROAD, y2, 0.015)
        ], (0.18, 0.19, 0.20))

        # Trotoar dan pembatas jalan
        for side in (-1, 1):
            self.face([
                (side * 4.1, y1, 0.025),
                (side * 5.0, y1, 0.025),
                (side * 5.0, y2, 0.025),
                (side * 4.1, y2, 0.025)
            ], (0.58, 0.56, 0.49))

            self.face([
                (side * 5.0, y1, 0.03),
                (side * 5.12, y1, 0.03),
                (side * 5.12, y2, 0.03),
                (side * 5.0, y2, 0.03)
            ], (0.73, 0.69, 0.59))

        # Marka tengah jalan
        for y in range(
            int(self.py) - 20,
            int(self.py) + 100,
            7
        ):
            self.face([
                (-0.06, y, 0.045),
                (0.06, y, 0.045),
                (0.06, y + 2.6, 0.045),
                (-0.06, y + 2.6, 0.045)
            ], (0.96, 0.84, 0.52))

    def draw_player(self):
        bob = 0.0

        if self.jump:
            bob = math.sin(
                math.pi * min(1, self.jump_t / 0.72)
            ) * 1.35

        x, y = self.px, self.py

        # Badan
        self.draw_box({
            "x": x, "y": y, "z": 0.32 + bob,
            "w": 0.52, "d": 0.34, "h": 0.72,
            "c": (0.10, 0.28, 0.72), "k": "player"
        })

        # Kepala
        self.draw_box({
            "x": x, "y": y, "z": 1.08 + bob,
            "w": 0.34, "d": 0.31, "h": 0.34,
            "c": (0.68, 0.45, 0.30), "k": "head"
        })

        # Kaki
        for offset in (-0.14, 0.14):
            self.draw_box({
                "x": x + offset, "y": y,
                "z": 0.02 + bob,
                "w": 0.17, "d": 0.22, "h": 0.32,
                "c": (0.09, 0.10, 0.12), "k": "leg"
            })

    def notify(self, message):
        self.toast = message
        self.toast_t = 2.0

    def shoot(self):
        if self.drive:
            self.notify("KELUAR DARI KENDARAAN UNTUK MENEMBAK")
            return

        if self.ammo[self.weapon] <= 0:
            self.notify("AMUNISI HABIS")
            return

        self.ammo[self.weapon] -= 1

        a = self.player_yaw

        self.shots.append([
            self.px, self.py, 1.1,
            math.sin(a) * 24,
            math.cos(a) * 24,
            1.1
        ])

        self.notify(
            self.weapons[self.weapon]
            + " • AMMO "
            + str(self.ammo[self.weapon])
        )

    def change_weapon(self):
        self.weapon = (self.weapon + 1) % len(self.weapons)
        self.notify("SENJATA: " + self.weapons[self.weapon])

    def do_jump(self):
        if not self.drive and not self.jump:
            self.jump = True
            self.jump_t = 0.0

    def toggle_drive(self):
        self.drive = not self.drive
        self.car_heading = self.player_yaw
        self.car_speed = 0.0

        self.notify(
            "MODE MENGEMUDI"
            if self.drive else
            "KELUAR KENDARAAN"
        )

    def joy(self, touch):
        dx = touch.x - self.joy_origin[0]
        dy = touch.y - self.joy_origin[1]

        radius = dp(42)
        length = math.hypot(dx, dy)

        if length > radius:
            dx = dx * radius / length
            dy = dy * radius / length

        self.joy_knob = (
            self.joy_origin[0] + dx,
            self.joy_origin[1] + dy
        )

        self.mx = dx / radius
        self.my = dy / radius

        if abs(self.mx) < 0.1:
            self.mx = 0.0

        if abs(self.my) < 0.1:
            self.my = 0.0

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        # Joystick kiri bawah
        if (
            touch.x < self.x + self.width * 0.34
            and touch.y < self.y + self.height * 0.42
        ):
            self.joy_id = touch.uid
            self.joy_origin = touch.pos
            self.joy_knob = touch.pos
            touch.grab(self)
            self.joy(touch)
            return True

        # Geser layar kanan untuk mengubah arah kamera
        if touch.x > self.x + self.width * 0.36:
            self.look_id = touch.uid
            self.look_last = touch.pos
            touch.grab(self)
            return True

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_move(touch)

        if touch.uid == self.joy_id:
            self.joy(touch)
            return True

        if touch.uid == self.look_id and self.look_last:
            delta_x = touch.x - self.look_last[0]

            # Sensitivitas kamera rendah
            self.yaw += delta_x * 0.0038

            self.look_last = touch.pos
            return True

        return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)

        if touch.uid == self.joy_id:
            self.joy_id = None
            self.mx = 0.0
            self.my = 0.0
            return True

        if touch.uid == self.look_id:
            self.look_id = None
            self.look_last = None
            return True

        return super().on_touch_up(touch)

    def tick(self, dt):
        dt = min(dt, 0.05)

        if self.drive:
            if self.my > 0:
                self.car_speed += 2.8 * dt
            elif self.my < 0:
                self.car_speed -= 5.0 * dt
            else:
                self.car_speed -= 1.1 * dt

            self.car_speed = max(0, min(12, self.car_speed))

            self.car_heading += self.steer * dt * 1.7

            self.px += math.sin(self.car_heading) * self.car_speed * dt
            self.py += math.cos(self.car_heading) * self.car_speed * dt

            self.yaw = self.car_heading
            self.player_yaw = self.car_heading

        else:
            speed = 7.2 if self.run else 4.0

            dx = (
                math.sin(self.yaw) * self.my
                + math.cos(self.yaw) * self.mx
            )

            dy = (
                math.cos(self.yaw) * self.my
                - math.sin(self.yaw) * self.mx
            )

            magnitude = math.hypot(dx, dy)

            if magnitude > 1:
                dx /= magnitude
                dy /= magnitude

            if magnitude > 0.1:
                nx = self.px + dx * speed * dt

                # Membatasi karakter agar tidak keluar
                # dari area jalan pada prototipe awal.
                if abs(nx) < 4.65:
                    self.px = nx

                self.py += dy * speed * dt

                self.player_yaw = math.atan2(dx, dy)

        if self.jump:
            self.jump_t += dt

            if self.jump_t >= 0.72:
                self.jump = False
                self.jump_t = 0.0

        for shot in self.shots:
            shot[0] += shot[3] * dt
            shot[1] += shot[4] * dt
            shot[5] -= dt

        self.shots = [
            shot for shot in self.shots
            if shot[5] > 0
        ]

        self.toast_t = max(0.0, self.toast_t - dt)

        self.draw()

    def draw(self):
        self.canvas.clear()

        with self.canvas:
            Color(0.39, 0.68, 0.84)
            Rectangle(pos=self.pos, size=self.size)

            self.ground()

            visible = []

            for obj in self.objs:
                distance = math.hypot(
                    obj["x"] - self.px,
                    obj["y"] - self.py
                )

                if distance < 62:
                    visible.append((distance, obj))

            # Gambar objek jauh terlebih dahulu
            visible.sort(key=lambda item: item[0], reverse=True)

            for _, obj in visible:
                self.draw_box(obj)

            for shot in self.shots:
                p = self.project(shot[0], shot[1], shot[2])

                if p:
                    Color(1.0, 0.76, 0.12)
                    Ellipse(
                        pos=(p[0] - dp(3), p[1] - dp(3)),
                        size=(dp(6), dp(6))
                    )

            self.draw_player()

            # Joystick
            if self.joy_id is not None:
                jx, jy = self.joy_origin
                kx, ky = self.joy_knob
            else:
                jx = self.x + dp(76)
                jy = self.y + dp(76)
                kx, ky = jx, jy

            Color(1, 1, 1, 0.18)
            Ellipse(
                pos=(jx - dp(42), jy - dp(42)),
                size=(dp(84), dp(84))
            )

            Color(1, 1, 1, 0.52)
            Ellipse(
                pos=(kx - dp(15), ky - dp(15)),
                size=(dp(30), dp(30))
            )

            # Penanda tengah layar
            Color(1, 1, 1, 0.7)

            Line(points=[
                self.cx - dp(8), self.cy,
                self.cx + dp(8), self.cy
            ])

            Line(points=[
                self.cx, self.cy - dp(8),
                self.cx, self.cy + dp(8)
            ])


class Game(App):
    def build(self):
        Window.clearcolor = (0.39, 0.68, 0.84, 1)

        self.rootbox = FloatLayout()
        self.w = World()

        self.rootbox.add_widget(self.w)

        self.label(
            "[b]KOTA NUSANTARA[/b]  [size=10]PROTOTYPE 0.4[/size]",
            {"x": 0.02, "top": 0.985},
            (dp(280), dp(34)),
            "left"
        )

        self.stats = self.label(
            "",
            {"x": 0.02, "top": 0.925},
            (dp(260), dp(72)),
            "left"
        )

        # Peta mini sederhana sebagai placeholder
        self.label(
            "[b]MAP[/b]\n[ size=12 ] ● ─ ─ [ /size ]",
            {"x": 0.02, "top": 0.80},
            (dp(105), dp(50)),
            "left"
        )

        self.btn(
            "⚙",
            {"right": 0.97, "top": 0.97},
            (dp(48), dp(42)),
            self.settings
        )

        self.buttons = {}

        self.buttons["weapon"] = self.btn(
            "PILIH SENJATA",
            {"right": 0.97, "y": 0.43},
            (dp(100), dp(42)),
            lambda *_: self.w.change_weapon()
        )

        self.buttons["jump"] = self.btn(
            "LOMPAT",
            {"right": 0.97, "y": 0.32},
            (dp(100), dp(42)),
            lambda *_: self.w.do_jump()
        )

        self.buttons["shoot"] = self.btn(
            "TEMBAK",
            {"right": 0.97, "y": 0.21},
            (dp(100), dp(42)),
            lambda *_: self.w.shoot()
        )

        self.buttons["run"] = self.btn(
            "LARI CEPAT",
            {"right": 0.86, "y": 0.09},
            (dp(100), dp(42)),
            self.run_down,
            self.run_up
        )

        self.buttons["drive"] = self.btn(
            "MENGEMUDI",
            {"right": 0.97, "y": 0.09},
            (dp(104), dp(42)),
            self.toggle_drive
        )

        self.buttons["left"] = self.btn(
            "◀",
            {"right": 0.97, "y": 0.31},
            (dp(65), dp(52)),
            lambda *_: self.steer(-1),
            lambda *_: self.steer(0)
        )

        self.buttons["right"] = self.btn(
            "▶",
            {"right": 0.86, "y": 0.31},
            (dp(65), dp(52)),
            lambda *_: self.steer(1),
            lambda *_: self.steer(0)
        )

        self.toast = self.label(
            "",
            {"center_x": 0.5, "y": 0.12},
            (dp(430), dp(36)),
            "center"
        )

        Clock.schedule_interval(self.refresh, 0.15)

        self.update_buttons()

        return self.rootbox

    def label(self, text, pos, size, align):
        label = Label(
            text=text,
            markup=True,
            size_hint=(None, None),
            size=size,
            pos_hint=pos,
            color=(1, 1, 1, 1),
            halign=align,
            valign="middle"
        )

        label.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        self.rootbox.add_widget(label)
        return label

    def btn(self, text, pos, size, press, release=None):
        button = Button(
            text=text,
            size_hint=(None, None),
            size=size,
            pos_hint=pos,
            background_normal="",
            background_down="",
            background_color=(0.035, 0.16, 0.27, 0.88),
            color=(1, 1, 1, 1),
            font_size=dp(11)
        )

        button.bind(on_press=press)

        if release:
            button.bind(on_release=release)

        self.rootbox.add_widget(button)
        return button

    def run_down(self, *_):
        self.w.run = True

    def run_up(self, *_):
        self.w.run = False

    def steer(self, value, *_):
        self.w.steer = value

    def toggle_drive(self, *_):
        self.w.toggle_drive()
        self.update_buttons()

    def update_buttons(self):
        driving = self.w.drive

        for key in ("weapon", "jump", "shoot", "run"):
            self.buttons[key].opacity = 0 if driving else 1
            self.buttons[key].disabled = driving

        for key in ("left", "right"):
            self.buttons[key].opacity = 1 if driving else 0
            self.buttons[key].disabled = not driving

        self.buttons["drive"].text = (
            "KELUAR" if driving else "MENGEMUDI"
        )

    def settings(self, *_):
        box = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        box.add_widget(
            Label(text="KOTA NUSANTARA • PENGATURAN")
        )

        reset_button = Button(
            text="KEMBALI KE POSISI AWAL",
            size_hint_y=None,
            height=dp(42)
        )

        close_button = Button(
            text="TUTUP",
            size_hint_y=None,
            height=dp(42)
        )

        box.add_widget(reset_button)
        box.add_widget(close_button)

        popup = Popup(
            title="Pengaturan",
            content=box,
            size_hint=(0.72, 0.55)
        )

        reset_button.bind(
            on_release=lambda *_: self.reset()
        )

        close_button.bind(on_release=popup.dismiss)

        popup.open()

    def reset(self):
        self.w.px = 0.0
        self.w.py = 0.0
        self.w.yaw = 0.0
        self.w.player_yaw = 0.0
        self.w.car_speed = 0.0

    def refresh(self, dt):
        w = self.w

        if w.drive:
            speed = int(w.car_speed * 3.6)
        else:
            movement = math.hypot(w.mx, w.my)
            base_speed = 7.2 if w.run else 4.0
            speed = int(base_speed * movement * 3.6)

        self.stats.text = (
            f"♥ {w.health}/100     $ {w.money}\n"
            f"{w.weapons[w.weapon]} • AMMO {w.ammo[w.weapon]}\n"
            f"KECEPATAN {speed} km/jam"
        )

        self.toast.text = (
            w.toast if w.toast_t > 0 else ""
        )

        self.update_buttons()


if __name__ == "__main__":
    Game().run()
