# Sumber aset eksternal yang disarankan

Aset model di bawah ini berasal dari kreator eksternal. **Aset-aset eksternal tersebut tidak disertakan di ZIP ini** karena lingkungan pembuatan paket ini tidak berhasil mengunduh arsipnya. Gunakan tautan resmi berikut untuk memperoleh paket aslinya, lalu taruh model yang dipilih di `assets/models/` dan tekstur di `assets/textures/`.

| Kebutuhan | Sumber | Lisensi / catatan |
|---|---|---|
| Rumah, bangunan pinggiran kota, pagar, pohon | https://kenney.nl/assets/city-kit-suburban | Halaman resmi menyatakan CC0 |
| Bangunan komersial/kota | https://kenney.nl/assets/city-kit-commercial | CC0; bangunan kota |
| Potongan jalan, trotoar, persimpangan | https://kenney.nl/assets/city-kit-roads | CC0; cocok untuk blok kota |
| Bangunan industri | https://kenney.nl/assets/city-kit-industrial | CC0 |
| Kendaraan mobil | https://quaternius.com/packs/cars.html | CC0; 8 model mobil, FBX/OBJ/Blend |
| Lingkungan alam | https://quaternius.com/ | Pilih paket dan verifikasi lisensi pada halaman paket |
| Tekstur PBR | https://ambientcg.com/ | Umumnya CC0; periksa ketentuan setiap aset |

## Catatan integrasi
- Godot 4 mendukung impor model 3D GLB/glTF dan OBJ. Untuk karakter beranimasi, prioritaskan GLB/glTF dengan rig/skeleton dan animasi.
- Setelah mengunduh, simpan salinan lisensi atau `LICENSE.txt` tiap paket di `assets/licenses/`.
- Pastikan skala model masuk akal: karakter sekitar 1.7–1.9 m, mobil sekitar 4 m panjang, lebar jalan utama 8–12 m.
- Untuk tampilan semi-realistis, pilih model PBR bertekstur, normal map, roughness map, dan ambient occlusion bila tersedia. Paket demo ini belum mengandung tekstur PBR eksternal.
