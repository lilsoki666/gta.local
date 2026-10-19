# Kota Nusantara 3D — Prototype 0.2

Paket ini berisi `main.py` yang memperbaiki beberapa masalah input dan tata letak dari prototype 0.1.

## Perubahan
- Kamera dipisahkan dari arah hadap karakter.
- Sensitivitas kamera diturunkan menjadi 0.0015 radian per piksel.
- Delta sentuhan kamera dibatasi agar gerakan tidak melonjak.
- Joystick diberi dead zone.
- Pergerakan mengikuti arah kamera.
- Tanah, jalan, dan trotoar memakai koordinat dunia yang sama.
- Bangunan ditempatkan di luar trotoar dan tabrakan dasar dipertahankan.

## Cara memakai
1. Ekstrak ZIP.
2. Salin `main.py` ke root repository GitHub, menggantikan file lama.
3. Commit perubahan ke branch `main`.
4. Jalankan GitHub Actions untuk membangun APK debug.
5. Instal APK baru dan uji kontrol di perangkat Android.

## Dependensi
`requirements.txt`:
    kivy==2.3.1

Buildozer:
    requirements = python3,kivy==2.3.1

## Catatan teknis
Renderer ini masih menggunakan proyeksi perspektif manual melalui Kivy canvas. Kivy canvas tidak menyediakan depth buffer 3D untuk kode ini, sehingga pengurutan bidang yang saling tumpang tindih belum sempurna. Paket ini adalah perbaikan prototype, bukan engine 3D komersial penuh.
