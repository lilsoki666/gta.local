import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, Ellipse
import random

class GameWorld(Widget):
    def __init__(self, **kwargs):
        super(GameWorld, self).__init__(**kwargs)
        self.player_x = 0
        self.player_y = 0
        self.player_speed = 4
        self.is_running = False
        self.is_jumping = False
        self.jump_offset = 0
        self.jump_vel = 0
        
        self.health = 100
        self.money = 50000
        self.speed_kmh = 0
        self.in_vehicle = False
        self.steering = 0 
        self.move_dir = 0 
        
        self.npcs = []
        self.vehicles = []
        
        # Penundaan spawn entity aman setelah ukuran layar siap
        Clock.schedule_once(lambda dt: self.spawn_world_entities(), 0.5)

    def spawn_world_entities(self):
        for i in range(5):
            self.npcs.append({
                'x': random.randint(-200, 200),
                'y': random.randint(100, 800),
                'state': 'walking',
                'dir': random.choice([-1, 1]),
                'timer': 100
            })
            
        for i in range(2):
            self.vehicles.append({
                'x': random.choice([-60, 60]),
                'y': random.randint(200, 600),
                'color': (random.random(), random.random(), random.random(), 1)
            })

    def update(self, dt):
        if self.in_vehicle:
            self.speed_kmh = 60
            self.player_x += self.steering * 3
            self.player_y += self.speed_kmh / 15
        else:
            spd = self.player_speed * 1.5 if self.is_running else self.player_speed
            self.player_y += self.move_dir * spd
            
        if self.is_jumping:
            self.jump_offset += self.jump_vel
            self.jump_vel -= 0.6
            if self.jump_offset <= 0:
                self.jump_offset = 0
                self.is_jumping = False

        self.redraw()

    def redraw(self):
        self.canvas.clear()
        w = self.width if self.width > 100 else 800
        h = self.height if self.height > 100 else 600
        
        with self.canvas:
            # Langit
            Color(0.35, 0.55, 0.75, 1)
            Rectangle(pos=(0, h*0.4), size=(w, h*0.6))
            
            # Tanah
            Color(0.22, 0.45, 0.22, 1)
            Rectangle(pos=(0, 0), size=(w, h*0.4))

            # Jalan Raya
            Color(0.2, 0.2, 0.2, 1)
            center_x = w / 2 + self.player_x
            road_bottom_w = 260
            road_top_w = 60
            road_h = h * 0.4
            
            Line(points=[center_x - road_bottom_w/2, 0, center_x - road_top_w/2, road_h, 
                         center_x + road_top_w/2, road_h, center_x + road_bottom_w/2, 0], width=2)

            # Karakter Pemain di bawah tengah
            p_x = w / 2 - 12
            p_y = 20 + self.jump_offset
            Color(0.9, 0.7, 0.5, 1)
            Ellipse(pos=(p_x + 4, p_y + 24, 16, 16))
            Color(0.1, 0.3, 0.8, 1)
            Rectangle(pos=(p_x, p_y + 8, 24, 18))

class KotaNusantaraApp(App):
    def build(self):
        root = FloatLayout()
        
        self.game_world = GameWorld()
        root.add_widget(self.game_world)
        
        # UI Kiri Atas (Status)
        self.health_lbl = Label(text="DARAH: 100% | $50,000", font_size='12sp', bold=True, pos=(20, 530), size_hint=(None, None), size=(200, 30))
        root.add_widget(self.health_lbl)
        
        # Kecepatan
        self.speed_lbl = Label(text="KECEPATAN: 0 km/jam", font_size='14sp', bold=True, pos=(550, 530), size_hint=(None, None), size=(200, 30))
        root.add_widget(self.speed_lbl)

        # Tombol Gerak Kiri Bawah
        btn_up = Button(text="▲", size_hint=(None, None), size=(50, 50), pos=(70, 80))
        btn_up.bind(press=lambda x: setattr(self.game_world, 'move_dir', 1), release=lambda x: setattr(self.game_world, 'move_dir', 0))
        
        btn_down = Button(text="▼", size_hint=(None, None), size=(50, 50), pos=(70, 20))
        btn_down.bind(press=lambda x: setattr(self.game_world, 'move_dir', -1), release=lambda x: setattr(self.game_world, 'move_dir', 0))
        
        root.add_widget(btn_up)
        root.add_widget(btn_down)

        # Tombol Aksi Kanan Bawah
        self.btn_jump = Button(text="LOMPAT", size_hint=(None, None), size=(80, 45), pos=(520, 20))
        self.btn_jump.bind(on_press=self.player_jump)
        root.add_widget(self.btn_jump)

        self.btn_sprint = Button(text="LARI", size_hint=(None, None), size=(80, 45), pos=(610, 20))
        self.btn_sprint.bind(press=lambda x: setattr(self.game_world, 'is_running', True), release=lambda x: setattr(self.game_world, 'is_running', False))
        root.add_widget(self.btn_sprint)

        self.btn_drive = Button(text="MOBIL", size_hint=(None, None), size=(90, 45), pos=(700, 20))
        self.btn_drive.bind(on_press=self.toggle_driving)
        root.add_widget(self.btn_drive)

        # Jadwal perulangan render game yang aman
        Clock.schedule_interval(self.game_world.update, 1.0 / 30.0)
        return root

    def player_jump(self, instance):
        if not self.game_world.is_jumping:
            self.game_world.is_jumping = True
            self.game_world.jump_vel = 10

    def toggle_driving(self, instance):
        self.game_world.in_vehicle = not self.game_world.in_vehicle
        self.btn_drive.text = "KELUAR" if self.game_world.in_vehicle else "MOBIL"

if __name__ == '__main__':
    KotaNusantaraApp().run()
