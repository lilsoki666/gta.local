# Kota Nusantara 3D — Prototype 0.4 (Kivy)

Proyek ini tetap menggunakan Python + Kivy + Buildozer. Tidak menggunakan Godot.

## Perubahan 0.4
- Memperbaiki kontrol joystick sentuh kiri agar mengubah arah gerak.
- Menambahkan kontrol kamera sentuh di sisi kanan (geser horizontal untuk putar kamera, vertikal untuk mengatur sudut).
- Menambahkan detail fasad ruko berupa bidang jendela dan papan nama berwarna.
- Menambahkan tiang lampu dan lampu jalan di sepanjang jalan.
- Memperluas sedikit area gerak agar pemain dapat mendekati objek tepi jalan.
- Tombol AKSI menampilkan respons saat pemain dekat objek area kota.
- Menyesuaikan label versi dan nama artifact build.

## Kontrol
- Joystick kiri: bergerak.
- Geser sisi kanan layar: putar kamera dan ubah sudut pandang.
- LARI: tekan dan tahan.
- LOMPAT: tekan.
- SENJATA: proyektil arcade sederhana.
- AKSI: pesan interaksi area kota.

## Build APK melalui GitHub
1. Commit isi proyek ke branch `main`.
2. Buka tab **Actions**.
3. Pilih **Build Kota Nusantara 3D APK**, lalu tekan **Run workflow**.
4. Setelah selesai, unduh artifact `kota-nusantara-3d-v04-debug`.

## Batasan yang masih ada
Ini adalah prototipe perspektif 3D berbasis poligon Kivy, bukan engine 3D dengan depth buffer. Detail ruko, lampu, dan pohon masih dibentuk dari poligon/box; belum menggunakan model 3D PBR, tekstur gambar, kendaraan yang dapat dikendarai, atau NPC dengan AI. Arsip ZIP yang diberikan untuk revisi ini tidak memuat file gambar aset di folder `assets/`, jadi tidak ada tekstur eksternal yang dapat dipakai tanpa menambahkannya terlebih dahulu.
