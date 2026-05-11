# Dokumentasi Modifikasi Proyek Kincir Angin

## Ringkasan Perubahan

Proyek grafika komputer 3D "Windmill Farm" telah dimodifikasi dengan menambahkan 7 fitur baru sesuai permintaan.

---

## Fitur Baru yang Ditambahkan

### 1. ✅ Tampilan Jam Digital (Kiri Atas)
- **Lokasi**: Pojok kiri atas layar
- **Format**: HH:MM (contoh: 07:00, 10:00, 19:00, 23:00)
- **Implementasi**: Menggunakan `glutStrokeCharacter` dengan overlay 2D
- **Warna**: Kuning cerah dengan background gelap semi-transparan
- **Fungsi**: `draw_time_display()`

### 2. ✅ Panel Instruksi Kontrol (Kiri Bawah)
- **Lokasi**: Pojok kiri bawah layar
- **Konten**:
  - T : Toggle waktu
  - 1 : Siang (07:00)
  - 2 : Jam makan (10:00)
  - 3 : Malam (19:00)
  - 4 : Tengah malam (23:00)
- **Style**: Teks putih dengan background gelap semi-transparan dan border
- **Fungsi**: `draw_instructions_panel()`

### 3. ✅ Sistem Waktu 4 Periode
Sistem siang-malam telah diubah menjadi 4 periode waktu yang berbeda:

#### **Periode 1: Pagi (07:00)**
- Langit cerah biru
- Matahari terbit dengan sinar
- Domba berkeliaran bebas di peternakan
- Pencahayaan terang

#### **Periode 2: Jam Makan (10:00)**
- Langit sedikit lebih gelap
- Ketiga domba menuju tempat makan (trough)
- Domba berkumpul di sekitar trough
- Animasi kepala menunduk (makan)

#### **Periode 3: Malam (19:00)**
- Langit gelap
- Bulan muncul dengan kawah
- Domba masuk ke dalam kandang
- Pencahayaan redup

#### **Periode 4: Tengah Malam (23:00)**
- Langit sangat gelap
- Bulan penuh
- Domba bersembunyi di dalam kandang
- **Serigala muncul di luar pagar**
- Pencahayaan minimal

**Variabel Global Baru**:
- `currentTime`: Menyimpan waktu saat ini (0-3)
- `TIME_CONFIGS`: Dictionary konfigurasi untuk setiap periode

### 4. ✅ Animasi Jam Makan (10:00)
- Ketiga domba berjalan menuju trough terdekat
- Posisi domba tersebar di sekitar trough (120° interval)
- Kepala domba menunduk (y_pos = 0.58)
- Transisi smooth menggunakan interpolasi
- **Fungsi**: Modifikasi pada `draw_goat()`

### 5. ✅ Serigala Mengintai (23:00)
Model serigala 3D yang muncul di tengah malam:
- **Posisi**: Di luar pagar (-12.5, 0.5, 5.0)
- **Warna**: Abu-abu gelap (0.15, 0.15, 0.18)
- **Fitur**:
  - Body, head, snout (moncong)
  - Telinga tegak
  - 4 kaki
  - Ekor
  - **Mata menyala** (glowing red eyes) tanpa lighting
- **Pose**: Menghadap ke arah kandang (45°)
- **Fungsi**: `draw_wolf()`

### 6. ✅ Rumput Lebat
Patch rumput lebat ditambahkan di 9 lokasi berbeda:
- Di sekitar hay bales (3 lokasi)
- Dekat trough (2 lokasi)
- Area kosong di farm plot (4 lokasi)
- **Implementasi**: Menggunakan `GL_LINES` untuk blade rumput
- **Variasi**:
  - Warna hijau bervariasi (hijau tua - hijau muda)
  - Tinggi rumput random (0.15 - 0.35)
  - Density: 18-25 blade per patch
  - Posisi random dalam area patch
- **Fungsi**: `draw_grass_patch(x, z, density, size)`

### 7. ✅ Perbaikan Atap Kandang
Detail atap barn yang ditingkatkan:

#### **Shingles/Genteng**
- 18 garis horizontal sebagai tekstur genteng
- Warna: Merah muda gelap (0.75, 0.55, 0.52)
- Menggunakan `GL_LINES` dengan line width 1.5
- Mengikuti kemiringan atap

#### **Ridge Cap (Bubungan)**
- Balok di puncak atap
- Warna: Coklat gelap (0.72, 0.42, 0.28)
- Dimensi: 10.2 x 0.15 x 0.25

#### **Overhang/Tritisan**
- Tritisan depan dan belakang
- Warna: Merah muda terang (0.85, 0.65, 0.58)
- Lebih menonjol dari atap utama
- Dimensi: 10.3 x 0.08 x 0.35

---

## Kontrol Keyboard

### Kontrol Baru:
- **T**: Toggle waktu (cycle: 07:00 → 10:00 → 19:00 → 23:00 → 07:00)
- **1**: Set ke Pagi (07:00)
- **2**: Set ke Jam Makan (10:00)
- **3**: Set ke Malam (19:00)
- **4**: Set ke Tengah Malam (23:00)

### Kontrol Lama (Tetap Ada):
- **+/=**: Zoom in
- **-/_**: Zoom out
- **Arrow Keys**: Rotasi kamera (mode custom)
- **Mouse Drag**: Rotasi kamera bebas
- **Mouse Scroll**: Zoom in/out
- **Right Click**: Menu view preset

---

## Perubahan Teknis

### Variabel Global Baru:
```python
currentTime = 0          # Waktu saat ini (0-3)
targetTime = 0           # Target waktu untuk transisi
timeBlend = 0.0          # Blend factor untuk transisi
```

### Konstanta Baru:
```python
TIME_CONFIGS = {
    0: {"hour": 7, "minute": 0, "name": "Pagi", "sky_blend": 0.0},
    1: {"hour": 10, "minute": 0, "name": "Siang", "sky_blend": 0.15},
    2: {"hour": 19, "minute": 0, "name": "Sore", "sky_blend": 0.75},
    3: {"hour": 23, "minute": 0, "name": "Malam", "sky_blend": 1.0},
}

TROUGH_POSITIONS = [
    {"x": -10.0, "z": 1.6},
    {"x": 9.5, "z": 0.8},
]
```

### Fungsi Baru:
1. `draw_text_stroke(x, y, text, scale)` - Render teks stroke
2. `draw_time_display()` - Display jam digital
3. `draw_instructions_panel()` - Panel instruksi
4. `draw_grass_patch(x, z, density, size)` - Rumput lebat
5. `draw_wolf()` - Model serigala

### Fungsi yang Dimodifikasi:
1. `init()` - Tambah blending untuk transparansi UI
2. `draw_goat()` - Tambah logika feeding time dan shelter
3. `draw_farm_plot()` - Tambah 9 patch rumput
4. `draw_barn()` - Tambah detail atap (shingles, ridge cap, overhang)
5. `draw_scene()` - Tambah wolf dan UI overlay
6. `timer()` - Update sistem waktu baru
7. `keyboard()` - Handler untuk tombol 1, 2, 3, 4, T

---

## Cara Menjalankan

```bash
cd "d:\ngodingan\smt 4\uas grafkom\Grafkom-KincirAngin"
python kincir.py
```

### Dependencies:
- PyOpenGL
- PyOpenGL-accelerate (opsional)
- NumPy

---

## Screenshot Fitur

### Periode Waktu:
1. **07:00 (Pagi)**: Domba berkeliaran, langit cerah
2. **10:00 (Jam Makan)**: Domba berkumpul di trough
3. **19:00 (Malam)**: Domba masuk kandang, bulan muncul
4. **23:00 (Tengah Malam)**: Serigala mengintai, sangat gelap

### UI Elements:
- Jam digital di kiri atas dengan background gelap
- Panel instruksi di kiri bawah dengan border putih

### Visual Improvements:
- Rumput lebat di 9 lokasi
- Atap barn dengan detail genteng, bubungan, dan tritisan
- Serigala dengan mata menyala merah

---

## Catatan Pengembangan

### Smooth Transitions:
- Semua transisi waktu menggunakan interpolasi smooth
- `dayNightBlend` berubah secara bertahap (step = 0.012)
- Domba berjalan dengan smooth interpolation

### Performance:
- Rumput menggunakan seed random yang konsisten untuk performa
- Serigala hanya di-render saat currentTime == 3
- UI overlay menggunakan orthographic projection terpisah

### Future Improvements:
- Tambah suara ambient (burung di pagi, serigala di malam)
- Animasi kincir lebih realistis berdasarkan waktu
- Partikel debu saat domba berjalan
- Shadow mapping untuk bayangan realistis

---

## Credits

**Original Project**: Windmill Farm - Day Night Barn Scene  
**Modified By**: [Your Name]  
**Date**: 2026  
**Course**: Grafika Komputer - UAS  

---

## Troubleshooting

### Jika teks tidak muncul:
- Pastikan GLUT sudah terinstall dengan benar
- `glutStrokeCharacter` memerlukan GLUT yang lengkap

### Jika rumput tidak terlihat:
- Periksa apakah `GL_LINES` di-support
- Coba tingkatkan `glLineWidth`

### Jika serigala tidak muncul:
- Tekan tombol **4** untuk set ke tengah malam
- Pastikan currentTime == 3

### Jika animasi patah-patah:
- Kurangi density rumput
- Pastikan timer interval 16ms (60 FPS)
