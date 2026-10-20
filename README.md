# Kota Nusantara 3D — Prototype 0.3

## Perubahan dari 0.2
- Koreksi tanda proyeksi vertikal agar tanah jauh bergerak menuju horizon dan tanah dekat menuju bawah layar.
- Jalan, trotoar, dan tanah berada pada koordinat dunia yang sama.
- Bangunan low-poly memiliki beberapa bidang sisi dan atap.
- Kamera tetap menggunakan kontrol sentuh yang lebih lambat.
- Tombol LOMPAT, SENJATA (proyektil arcade non-grafis), AKSI, dan LARI.
- Kontrol gerak joystick kiri dan kamera dengan geseran sisi kanan.

## File
- `main.py`: kode game
- `buildozer.spec`: konfigurasi APK
- `requirements.txt`: dependensi Python
- `.github/workflows/build-apk.yml`: build APK otomatis

## Build
Commit file ke branch `main`, buka Actions, jalankan workflow, lalu unduh artifact `kota-nusantara-3d-v03-debug`.

## Catatan
Ini tetap renderer polygon/proyeksi perspektif manual berbasis Kivy, bukan engine 3D sejati dengan depth buffer. Karakter dan bangunan dibuat dari balok low-poly yang diproyeksikan ke layar. Sistem senjata saat ini hanya menampilkan proyektil arcade; belum ada damage, musuh, atau animasi senjata. Tombol AKSI masih berupa placeholder. Untuk game open-world 3D yang lebih kompleks, renderer/engine 3D khusus akan lebih tepat.
