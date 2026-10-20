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
        
        # Status Game sesuai Konsep Kertas
        self.health = 100
        self.money = 50000
        self.speed_kmh = 0
        self.in_vehicle = False
        self.steering = 0
        self.move_dir = 0
        
        self.npcs = []
        self.vehicles = []
        Clock.schedule_once(lambda dt: self.spawn_world_entities(), 0.5)

    def spawn_world_entities(self):
        for i in range(6):
            self.npcs.append({
                'x': random.randint(-250, 250),
                'y': random.randint(100, 1000),
                'state': random.choice(['walking', 'standing']),
                'dir': random.choice([-1, 1]),
                'timer': random.randint(50, 150)
            })
            
        for i in range(3):
            self.vehicles.append({
                'x': random.choice([-70, 70]),
                'y': random.randint(200, 800),
                'color': (random.random(), random.random(), random.random(), 1)
            })

    def update(self, dt):
        if self.in_vehicle:
            self.speed_kmh = 70
            self.player_x += self.steering * 3.5
            self.player_y += self.speed_kmh / 12
        else:
            spd = self.player_speed * 1.6 if self.is_running else self.player_speed
            self.player_y += self.move_dir * spd
            
        if self.is_jumping:
            self.jump_offset += self.jump_vel
            self.jump_vel -= 0.7
            if self.jump_offset <= 0:
                self.jump_offset = 0
                self.is_jumping = False

        for npc in self.npcs:
            npc['timer'] -= 1
            if npc['timer'] <= 0:
                npc['state'] = random.choice(['walking', 'standing'])
                npc['dir'] = random.choice([-1, 1])
                npc['timer'] = random.randint(100, 250)
            if npc['state'] == 'walking':
                npc['x'] += npc['dir'] * 0.4

        self.redraw()

    def redraw(self):
        self.canvas.clear()
        # Ambil ukuran layar aman untuk mencegah crash awal
        w = self.width if self.width > 100 else 800
        h = self.height if self.height > 100 else 600
        
        with self.canvas:
            # Langit
            Color(0.35, 0.55, 0.75, 1)
            Rectangle(pos=(0, h*0.4), size=(w, h*0.6))
            
            # Tanah / Rumput
            Color(0.22, 0.45, 0.22, 1)
            Rectangle(pos=(0, 0), size=(w, h*0.4))

            # Jalan Raya Perspektif
            Color(0.2, 0.2, 0.2, 1)
            center_x = w / 2 + self.player_x
            road_bottom_w = 280
            road_top_w = 70
            road_h = h * 0.4
            
            Line(points=[center_x - road_bottom_w/2, 0, center_x - road_top_w/2, road_h, 
                         center_x + road_top_w/2, road_h, center_x + road_bottom_w/2, 0], width=2)

            # Render Kendaraan
            for v in self.vehicles:
                v_sx = center_x + v['x'] * (1 - v['y']/1500)
                v_sy = (v['y'] / 1500) * road_h
                Color(*v['color'])
                Rectangle(pos=(v_sx - 15, v_sy, 30, 16))

            # Render NPC
            for npc in self.npcs:
                n_sx = center_x + npc['x'] * (1 - npc['y']/1500)
                n_sy = (npc['y'] / 1500) * road_h
                Color(0.8, 0.6, 0.4, 1)
                Ellipse(pos=(n_sx - 5, n_sy + 8, 10, 10))
                Color(0.3, 0.3, 0.8, 1)
                Rectangle(pos=(n_sx - 4, n_sy, 8, 10))

            # Render Karakter Pemain di Bawah Tengah
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
        
        # --- UI KIRI ATAS: Map, Darah, Uang ---
        self.map_lbl = Label(text="🗺️ [MAP]", font_size='11sp', bold=True, pos=(15, 535), size_hint=(None, None), size=(80, 40))
        root.add_widget(self.map_lbl)
        
        self.health_lbl = Label(text="DARAH: 100%", font_size='12sp', bold=True, pos=(110, 545), size_hint=(None, None), size=(150, 25))
        root.add_widget(self.health_lbl)
        
        self.money_lbl = Label(text="$ 50,000", font_size='14sp', color=(0.2, 1, 0.2, 1), bold=True, pos=(110, 520), size_hint=(None, None), size=(150, 25))
        root.add_widget(self.money_lbl)

        # --- UI KANAN ATAS: Pengaturan & Kecepatan ---
        self.settings_btn = Button(text="⚙️", size_hint=(None, None), size=(45, 45), pos=(735, 530), background_color=(0.2, 0.2, 0.2, 0.8))
        root.add_widget(self.settings_btn)
        
        self.speed_lbl = Label(text="KECEPATAN: 0 km/jam", font_size='14sp', bold=True, pos=(510, 535), size_hint=(None, None), size=(200, 30))
        root.add_widget(self.speed_lbl)

        # --- UI KIRI BAWAH: Tombol Gerak (D-Pad Atas/Bawah) ---
        btn_up = Button(text="▲", size_hint=(None, None), size=(50, 50), pos=(70, 80), background_color=(0.3, 0.3, 0.3, 0.8))
        btn_up.bind(press=lambda x: setattr(self.game_world, 'move_dir', 1), release=lambda x: setattr(self.game_world, 'move_dir', 0))
        
        btn_down = Button(text="▼", size_hint=(None, None), size=(50, 50), pos=(70, 20), background_color=(0.3, 0.3, 0.3, 0.8))
        btn_down.bind(press=lambda x: setattr(self.game_world, 'move_dir', -1), release=lambda x: setattr(self.game_world, 'move_dir', 0))
        
        root.add_widget(btn_up)
        root.add_widget(btn_down)

        # --- UI KANAN BAWAH: Tombol Aksi Lengkap ---
        self.right_actions_layout = FloatLayout(size_hint=(None, None), size=(260, 200), pos=(520, 10))
        
        self.btn_weapon = Button(text="SENJATA", size_hint=(None, None), size=(75, 45), pos=(90, 140))
        self.btn_jump = Button(text="LOMPAT", size_hint=(None, None), size=(75, 45), pos=(10, 95))
        self.btn_drive = Button(text="KENDARAAN", size_hint=(None, None), size=(90, 45), pos=(90, 95))
        self.btn_sprint = Button(text="LARI", size_hint=(None, None), size=(75, 45), pos=(185, 95))
        self.btn_shoot = Button(text="TEMBAK", size_hint=(None, None), size=(85, 65), pos=(175, 20))
        
        self.btn_jump.bind(on_press=self.player_jump)
        self.btn_sprint.bind(press=lambda x: setattr(self.game_world, 'is_running', True), release=lambda x: setattr(self.game_world, 'is_running', False))
        self.btn_drive.bind(on_press=self.toggle_driving_mode)
        
        self.right_actions_layout.add_widget(self.btn_weapon)
        self.right_actions_layout.add_widget(self.btn_jump)
        self.right_actions_layout.add_widget(self.btn_drive)
        self.right_actions_layout.add_widget(self.btn_sprint)
        self.right_actions_layout.add_widget(self.btn_shoot)
        
        root.add_widget(self.right_actions_layout)

        Clock.schedule_interval(self.game_world.update, 1.0 / 30.0)
        Clock.schedule_interval(self.update_ui, 0.1)

        return root

    def player_jump(self, instance):
        if not self.game_world.is_jumping:
            self.game_world.is_jumping = True
            self.game_world.jump_vel = 10

    def toggle_driving_mode(self, instance):
        self.game_world.in_vehicle = not self.game_world.in_vehicle
        self.right_actions_layout.clear_widgets()
        
        if self.game_world.in_vehicle:
            self.btn_steer_left = Button(text="◀ KIRI", size_hint=(None, None), size=(100, 55), pos=(20, 50))
            self.btn_steer_left.bind(press=lambda x: setattr(self.game_world, 'steering', -1), release=lambda x: setattr(self.game_world, 'steering', 0))
            
            self.btn_steer_right = Button(text="KANAN ▶", size_hint=(None, None), size=(100, 55), pos=(135, 50))
            self.btn_steer_right.bind(press=lambda x: setattr(self.game_world, 'steering', 1), release=lambda x: setattr(self.game_world, 'steering', 0))
            
            self.btn_exit_car = Button(text="KELUAR KENDARAAN", size_hint=(None, None), size=(215, 45), pos=(20, 115))
            self.btn_exit_car.bind(on_press=self.toggle_driving_mode)
            
            self.right_actions_layout.add_widget(self.btn_steer_left)
            self.right_actions_layout.add_widget(self.btn_steer_right)
            self.right_actions_layout.add_widget(self.btn_exit_car)
        else:
            self.right_actions_layout.add_widget(self.btn_weapon)
            self.right_actions_layout.add_widget(self.btn_jump)
            self.right_actions_layout.add_widget(self.btn_drive)
            self.right_actions_layout.add_widget(self.btn_sprint)
            self.right_actions_layout.add_widget(self.btn_shoot)
            self.game_world.speed_kmh = 0
            self.game_world.steering = 0

    def update_ui(self, dt):
        self.speed_lbl.text = f"KECEPATAN: {int(self.game_world.speed_kmh)} km/jam"

if __name__ == '__main__':
    KotaNusantaraApp().run()
