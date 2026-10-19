
[app]

title = Kota Nusantara 3D
package.name = kotanusantara
package.domain = id.nusantara.game

source.dir = .
source.include_exts = py,kv,png,jpg,atlas,json,txt

version = 0.1.0

requirements = python3,kivy==2.3.1

orientation = landscape
fullscreen = 1

# Tidak menggunakan jaringan untuk prototype offline.
android.permissions =

# Fokus pada perangkat Android 64-bit.
android.archs = arm64-v8a

# Pengaturan Android SDK/NDK mengikuti default
# yang disediakan oleh versi Buildozer terpasang.

[buildozer]

log_level = 2
warn_on_root = 1
