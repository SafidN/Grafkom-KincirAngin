# Changelog - Modifikasi Kincir Angin

## [2.0.0] - 2026-05-11

### ✨ Fitur Baru

#### 1. Sistem Waktu 4 Periode
- **Added**: Sistem waktu dengan 4 periode berbeda (07:00, 10:00, 19:00, 23:00)
- **Added**: Variabel global `currentTime` untuk tracking waktu
- **Added**: Dictionary `TIME_CONFIGS` untuk konfigurasi setiap periode
- **Changed**: Sistem siang-malam sederhana menjadi sistem 4 periode kompleks

#### 2. UI Overlay
- **Added**: Display jam digital di pojok kiri atas
- **Added**: Panel instruksi kontrol di pojok kiri bawah
- **Added**: Fungsi `draw_text_stroke()` untuk render teks
- **Added**: Fungsi `draw_time_display()` untuk jam digital
- **Added**: Fungsi `draw_instructions_panel()` untuk panel instruksi
- **Added**: Blending support untuk transparansi UI

#### 3. Animasi Domba
- **Added**: Perilaku feeding time saat jam 10:00
- **Added**: Domba mengerumuni trough saat jam makan
- **Added**: Animasi kepala menunduk saat makan
- **Changed**: Logika `draw_goat()` untuk mendukung 4 periode waktu
- **Added**: Konstanta `TROUGH_POSITIONS` untuk posisi feeding

#### 4. Serigala
- **Added**: Model serigala 3D yang muncul di tengah malam
- **Added**: Fungsi `draw_wolf()` untuk render serigala
- **Added**: Mata menyala (glowing eyes) dengan efek tanpa lighting
- **Added**: Pose mengintai di luar pagar

#### 5. Vegetasi
- **Added**: 9 patch rumput lebat di berbagai lokasi
- **Added**: Fungsi `draw_grass_patch()` dengan parameter density dan size
- **Added**: Variasi warna hijau (tua dan muda)
- **Added**: Tinggi rumput random untuk realisme
- **Added**: Seed random konsisten untuk performa

#### 6. Detail Atap Barn
- **Added**: 18 garis horizontal sebagai tekstur shingles/genteng
- **Added**: Ridge cap (bubungan) di puncak atap
- **Added**: Overhang/tritisan yang lebih jelas di depan dan belakang
- **Added**: Fascia board detail di tepi atap
- **Improved**: Visual atap barn menjadi lebih realistis

### 🎮 Kontrol Baru

- **Added**: Tombol `T` untuk toggle waktu (cycle 0→1→2→3→0)
- **Added**: Tombol `1` untuk set ke Pagi (07:00)
- **Added**: Tombol `2` untuk set ke Jam Makan (10:00)
- **Added**: Tombol `3` untuk set ke Malam (19:00)
- **Added**: Tombol `4` untuk set ke Tengah Malam (23:00)
- **Changed**: Keyboard handler untuk mendukung sistem waktu baru

### 🔧 Perubahan Teknis

#### Variabel Global
```python
+ currentTime = 0
+ targetTime = 0
+ timeBlend = 0.0
```

#### Konstanta
```python
+ TIME_CONFIGS = {...}
+ TROUGH_POSITIONS = [...]
```

#### Fungsi Baru
- `draw_text_stroke(x, y, text, scale)`
- `draw_time_display()`
- `draw_instructions_panel()`
- `draw_grass_patch(x, z, density, size)`
- `draw_wolf()`

#### Fungsi Dimodifikasi
- `init()` - Enable blending
- `draw_goat()` - Logika 4 periode
- `draw_farm_plot()` - Tambah rumput
- `draw_barn()` - Detail atap
- `draw_scene()` - Wolf + UI
- `timer()` - Sistem waktu baru
- `keyboard()` - Handler baru

### 📊 Statistik

- **Baris kode ditambahkan**: ~300 baris
- **Fungsi baru**: 5 fungsi
- **Fungsi dimodifikasi**: 7 fungsi
- **Objek 3D baru**: 1 (serigala)
- **UI elements**: 2 (jam + panel)
- **Patch rumput**: 9 lokasi
- **Periode waktu**: 4 periode

### 🐛 Bug Fixes

- **Fixed**: Domba tidak smooth saat transisi malam
- **Fixed**: Lighting tidak konsisten antar periode
- **Improved**: Interpolasi movement domba

### 🎨 Visual Improvements

- **Improved**: Atap barn dengan detail genteng
- **Improved**: Lingkungan lebih hidup dengan rumput
- **Improved**: Atmosfer tengah malam dengan serigala
- **Added**: UI informatif untuk user experience

### 📝 Dokumentasi

- **Added**: README_MODIFIKASI.md dengan dokumentasi lengkap
- **Added**: CHANGELOG.md untuk tracking perubahan
- **Added**: Komentar inline untuk kode baru

---

## [1.0.0] - Original

### Fitur Original
- Kincir angin dengan 3 baling-baling berputar
- Kandang barn dengan pintu dan jendela
- 3 domba yang berkeliaran
- Sistem siang-malam sederhana
- Pagar, hay bales, trough, box stacks
- Kontrol kamera dan zoom
- Menu view preset
- Lighting dan fog effects

---

## Roadmap Future

### [2.1.0] - Planned
- [ ] Suara ambient (burung, serigala)
- [ ] Partikel debu saat domba berjalan
- [ ] Animasi kincir berdasarkan waktu
- [ ] Weather system (hujan, awan)

### [2.2.0] - Planned
- [ ] Shadow mapping
- [ ] Texture mapping untuk barn
- [ ] More animals (ayam, sapi)
- [ ] Day-night cycle otomatis

### [3.0.0] - Planned
- [ ] VR support
- [ ] Multiplayer mode
- [ ] Quest system
- [ ] Save/Load state
