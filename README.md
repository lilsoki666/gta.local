# Kota Nusantara 3D — Starter Project

Paket starter 3D berbasis **Godot 4.x** yang memindahkan kebutuhan visual Prototype 0.4 ke renderer 3D sungguhan. Paket ini bukan salinan aset GTA; model kota awal dibuat dari mesh sederhana di dalam proyek, supaya langsung terbuka tanpa unduhan aset tambahan.

## Isi paket
- Kota demo: persimpangan, marka jalan, trotoar, bangunan, pohon, dan satu mobil.
- Karakter 3D sederhana, kamera third-person mengikuti pemain.
- HUD HP/uang, minimap bulat, joystick sentuh, tombol aksi bulat untuk senjata, lompat, tembak, sprint, dan mode kendaraan.
- File model OBJ contoh di `assets/models/` yang dapat diganti dengan model eksternal.
- `docs/ASSET_SOURCES.md`: sumber aset 3D CC0 dan lisensinya.

## Membuka proyek
1. Instal Godot 4.x di PC/laptop atau gunakan Godot Android Editor jika perangkat mendukungnya.
2. Ekstrak ZIP.
3. Buka folder `Kota_Nusantara_3D_Starter` sebagai proyek Godot (pilih `project.godot`).
4. Tekan Play / F6 untuk menjalankan scene utama.

## Android
Atur Android export templates dan Android SDK/JDK di Godot, lalu gunakan **Project → Export → Android**. Gunakan renderer Compatibility (sudah disetel) untuk target perangkat Android yang lebih luas. Pengaturan SDK dan proses signing masih perlu disesuaikan di mesin build milik Anda.

## Kontrol
- Sentuh dan geser joystick kiri untuk berjalan.
- Tombol ↑ untuk lompat.
- ⚡ untuk sprint.
- ● untuk aksi tembak prototipe.
- CAR mengubah label ke mode kendaraan prototipe.
- Di keyboard: Space = lompat, Shift = sprint.

## Batas prototipe yang perlu diketahui
- Ini paket dasar yang bisa dibuka dan dikembangkan, belum game open-world siap rilis.
- Tombol kendaraan saat ini menandai mode; sistem masuk/keluar mobil, steering, traffic AI, NPC, senjata fisik, misi, save game, dan peta minimap dinamis belum diimplementasikan.
- Model karakter/kendaraan/bangunan di paket adalah mesh awal sederhana, bukan model semi-realistis bertekstur PBR.
- Jangan menganggap paket CC0 eksternal sudah berada di proyek. Sumber yang disarankan ada di `docs/ASSET_SOURCES.md`; unduh dari halaman resmi, periksa lisensi/format dan impor modelnya.
