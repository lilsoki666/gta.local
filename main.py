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
        self.player_speed = 5
        self.is_running = False
        self.is_jumping = False
        self.jump_offset = 0
        self.jump_vel = 0
        
        # Status Game
        self.health = 100
        self.money = 50000
        self.speed_kmh = 0
        
        # State Kendaraan & Kontrol
        self.in_vehicle = False
        self.steering = 0 # -1 untuk kiri, 1 untuk kanan, 0 lurus
        self.move_dir = 0 # Kontrol dari tombol arah bawah/atas
        
        # Daftar NPC dan Kendaraan di Dunia Game
        self.npcs = []
        self.vehicles = []
        self.spawn_world_entities()

    def spawn_world_entities(self):
        # Spawn NPC dengan aktivitas random
        for i in range(8):
            self.npcs.append({
                'x': random.randint(-300, 300),
                'y': random.randint(100, 1500),
                'state': random.choice(['walking', 'standing', 'shopping']),
                'dir': random.choice([-1, 1]),
                'timer': random.randint(50, 200)
            })
            
        # Spawn Kendaraan di sepanjang jalan
        for i in range(4):
            self.vehicles.append({
                'x': random.choice([-80, 80]),
                'y': random.randint(300, 1200),
                'type': random.choice(['Sedan', 'SUV', 'Sport Car']),
                'color': (random.random(), random.random(), random.random(), 1)
            })

    def update(self, dt):
        # Perbarui posisi pemain berdasarkan input tombol
        if self.in_vehicle:
            self.speed_kmh = 80 if self.speed_kmh == 0 else self.speed_kmh
            self.player_x += self.steering * 4
            self.player_y += self.speed_kmh / 10
        else:
            spd = self.player_speed * 1.8 if self.is_running else self.player_speed
            self.player_y += self.move_dir * spd
            
        # Logika Fisika Lompat
        if self.is_jumping:
            self.jump_offset += self.jump_vel
            self.jump_vel -= 0.8
            if self.jump_offset <= 0:
                self.jump_offset = 0
                self.is_jumping = False

        # Perbarui Aktivitas NPC
        for npc in self.npcs:
            npc['timer'] -= 1
            if npc['timer'] <= 0:
                npc['state'] = random.choice(['walking', 'standing', 'shopping'])
                npc['dir'] = random.choice([-1, 1])
                npc['timer'] = random.randint(100, 300)
            if npc['state'] == 'walking':
                npc['x'] += npc['dir'] * 0.5

        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # --- Lingkungan & Latar Belakang Realistis ---
            # Langit
            Color(0.35, 0.55, 0.75, 1)
            Rectangle(pos=(0, self.height*0.4), size=(self.width, self.height*0.6))
            
            # Matahari
            Color(1, 0.95, 0.8, 1)
            Ellipse(pos=(self.width - 120, self.height - 120), size=(80, 80))

            # Tanah / Rumput
            Color(0.22, 0.45, 0.22, 1)
            Rectangle(pos=(0, 0), size=(self.width, self.height*0.4))

            # Jalan Raya Perspektif 3D
            Color(0.2, 0.2, 0.2, 1)
            center_x = self.width / 2 + self.player_x
            road_bottom_w = 300
            road_top_w = 80
            road_h = self.height * 0.4
            
            Line(points=[center_x - road_bottom_w/2, 0, center_x - road_top_w/2, road_h, 
                         center_x + road_top_w/2, road_h, center_x + road_bottom_w/2, 0], width=2)
            
            # Garis Tengah Jalan
            Color(1, 1, 1, 0.8)
            for i in range(10):
                y_pos = i * (road_h / 10)
                w_factor = 1 - (y_pos / road_h) * 0.7
                Line(points=[center_x, y_pos, center_x, y_pos + 15 * w_factor], width=2)

            # --- Render Kendaraan ---
            for v in self.vehicles:
                v_screen_x = center_x + v['x'] * (1 - v['y']/2000)
                v_screen_y = (v['y'] / 2000) * road_h
                Color(*v['color'])
                Rectangle(pos=(v_screen_x - 15, v_screen_y, 30, 18))

            # --- Render NPC ---
            for npc in self.npcs:
                npc_screen_x = center_x + npc['x'] * (1 - npc['y']/2000)
                npc_screen_y = (npc['y'] / 2000) * road_h
                Color(0.8, 0.6, 0.4, 1)
                Ellipse(pos=(npc_screen_x - 6, npc_screen_y + 10 + self.jump_offset, 12, 12))
                Color(0.2, 0.3, 0.7, 1)
                Rectangle(pos=(npc_screen_x - 5, npc_screen_y + self.jump_offset, 10, 12))

            # --- Render Pemain (Karakter Utama) ---
            p_x = self.width / 2 - 12
            p_y = 20 + self.jump_offset
            Color(0.9, 0.7, 0.5, 1)
            Ellipse(pos=(p_x + 4, p_y + 24, 16, 16))
            Color(0.1, 0.3, 0.8, 1)
            Rectangle(pos=(p_x, p_y + 8, 24, 18))
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(pos=(p_x + 3, p_y, 18, 10))

class GTAKotaNusantaraApp(App):
    def build(self):
        root = FloatLayout()
        
        self.game_world = GameWorld()
        root.add_widget(self.game_world)
        
        # --- UI Sesuai Konsep Kertas ---
        
        # 1. Kiri Atas: Map, Darah, Uang
        ui_top_left = FloatLayout(size_hint=(None, None), size=(300, 100), pos=(10, 500))
        with ui_top_left.canvas:
            Color(0, 0, 0, 0.5)
            Rectangle(pos=(0, 0), size=(300, 100))
            
        self.map_lbl = Label(text="[MAP KOTA]", font_size='12sp', pos=(10, 40), size_hint=(None, None), size=(80, 50))
        ui_top_left.add_widget(self.map_lbl)
        
        self.health_lbl = Label(text="DARAH: 100%", font_size='13sp', bold=True, pos=(100, 60), size_hint=(None, None), size=(180, 30))
        self.money_lbl = Label(text="$ 50,000", font_size='15sp', color=(0.2, 1, 0.2, 1), bold=True, pos=(100, 20), size_hint=(None, None), size=(180, 30))
        ui_top_left.add_widget(self.health_lbl)
        ui_top_left.add_widget(self.money_lbl)
        root.add_widget(ui_top_left)

        # 2. Kanan Atas: Pengaturan & Kecepatan
        self.settings_btn = Button(text="⚙️", size_hint=(None, None), size=(50, 50), pos=(730, 530), background_color=(0.2, 0.2, 0.2, 0.8))
        root.add_widget(self.settings_btn)
        
        self.speed_lbl = Label(text="KECEPATAN: 0 km/jam", font_size='16sp', bold=True, pos=(500, 540), size_hint=(None, None), size=(200, 30))
        root.add_widget(self.speed_lbl)

        # 3. Kiri Bawah: Tombol Gerak (D-Pad)
        joystick_layout = FloatLayout(size_hint=(None, None), size=(140, 140), pos=(20, 20))
        with joystick_layout.canvas:
            Color(1, 1, 1, 0.2)
            Ellipse(pos=(0, 0), size=(140, 140))
            
        btn_up = Button(text="▲", size_hint=(None, None), size=(45, 45), pos=(47, 90), background_color=(0.3, 0.3, 0.3, 0.8))
        btn_up.bind(press=lambda x: setattr(self.game_world, 'move_dir', 1), release=lambda x: setattr(self.game_world, 'move_dir', 0))
        
        btn_down = Button(text="▼", size_hint=(None, None), size=(45, 45), pos=(47, 5), background_color=(0.3, 0.3, 0.3, 0.8))
        btn_down.bind(press=lambda x: setattr(self.game_world, 'move_dir', -1), release=lambda x: setattr(self.game_world, 'move_dir', 0))
        
        joystick_layout.add_widget(btn_up)
        joystick_layout.add_widget(btn_down)
        root.add_widget(joystick_layout)

        # 4. Kanan Bawah: Tombol Aksi (Senjata, Lompat, Kendaraan, Lari, Tembak)
        self.right_actions_layout = FloatLayout(size_hint=(None, None), size=(260, 200), pos=(520, 20))
        
        self.btn_weapon = Button(text="SENJATA", size_hint=(None, None), size=(75, 45), pos=(90, 140))
        self.btn_jump = Button(text="LOMPAT", size_hint=(None, None), size=(75, 45), pos=(10, 95))
        self.btn_drive = Button(text="KENDARAAN", size_hint=(None, None), size=(90, 45), pos=(90, 95))
        self.btn_sprint = Button(text="LARI", size_hint=(None, None), size=(75, 45), pos=(185, 95))
        self.btn_shoot = Button(text="TEMBAK", size_hint=(None, None), size=(85, 65), pos=(175, 20))
        
        self.btn_jump.bind(on_press=self.player_jump)
        self.btn_sprint.bind(press=lambda x: setattr(self.game_world, 'is_running', True), release=lambda x: setattr(self.game_world, 'is_running', False))
        self.btn_drive.bind(on_press=self.toggle_driving_mode)
        self.btn_weapon.bind(on_press=self.cycle_weapon)
        
        self.right_actions_layout.add_widget(self.btn_weapon)
        self.right_actions_layout.add_widget(self.btn_jump)
        self.right_actions_layout.add_widget(self.btn_drive)
        self.right_actions_layout.add_widget(self.btn_sprint)
        self.right_actions_layout.add_widget(self.btn_shoot)
        
        root.add_widget(self.right_actions_layout)

        Clock.schedule_interval(self.game_world.update, 1.0 / 60.0)
        Clock.schedule_interval(self.update_ui, 0.1)

        return root

    def player_jump(self, instance):
        if not self.game_world.is_jumping:
            self.game_world.is_jumping = True
            self.game_world.jump_vel = 12

    def cycle_weapon(self, instance):
        self.btn_weapon.text = "PISTOL" if self.btn_weapon.text == "SENJATA" else ("RIFLE" if self.btn_weapon.text == "PISTOL" else "SENJATA")

    def toggle_driving_mode(self, instance):
        self.game_world.in_vehicle = not self.game_world.in_vehicle
        self.right_actions_layout.clear_widgets()
        
        if self.game_world.in_vehicle:
            # Mode Mengemudi: Tombol kanan berubah jadi panah kiri/kanan
            self.btn_steer_left = Button(text="◀ KIRI", size_hint=(None, None), size=(100, 60), pos=(20, 50))
            self.btn_steer_left.bind(press=lambda x: setattr(self.game_world, 'steering', -1), release=lambda x: setattr(self.game_world, 'steering', 0))
            
            self.btn_steer_right = Button(text="KANAN ▶", size_hint=(None, None), size=(100, 60), pos=(140, 50))
            self.btn_steer_right.bind(press=lambda x: setattr(self.game_world, 'steering', 1), release=lambda x: setattr(self.game_world, 'steering', 0))
            
            self.btn_exit_car = Button(text="KELUAR KENDARAAN", size_hint=(None, None), size=(220, 45), pos=(20, 130))
            self.btn_exit_car.bind(on_press=self.toggle_driving_mode)
            
            self.right_actions_layout.add_widget(self.btn_steer_left)
            self.right_actions_layout.add_widget(self.btn_steer_right)
            self.right_actions_layout.add_widget(self.btn_exit_car)
            self.btn_drive.text = "KELUAR"
        else:
            # Kembali ke Mode Jalan Kaki
            self.right_actions_layout.add_widget(self.btn_weapon)
            self.right_actions_layout.add_widget(self.btn_jump)
            self.right_actions_layout.add_widget(self.btn_drive)
            self.right_actions_layout.add_widget(self.btn_sprint)
            self.right_actions_layout.add_widget(self.btn_shoot)
            self.btn_drive.text = "KENDARAAN"
            self.game_world.speed_kmh = 0
            self.game_world.steering = 0

    def update_ui(self, dt):
        self.speed_lbl.text = f"KECEPATAN: {int(self.game_world.speed_kmh)} km/jam"

if __name__ == '__main__':
    GTAKotaNusantaraApp().run()
