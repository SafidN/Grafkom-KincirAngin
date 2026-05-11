# Quick Reference Guide - Windmill Farm v2.0

## 🎮 Kontrol Keyboard

### Waktu
| Tombol | Fungsi |
|--------|--------|
| **T** | Toggle waktu (cycle melalui 4 periode) |
| **1** | Pagi (07:00) - Domba berkeliaran |
| **2** | Jam Makan (10:00) - Domba makan di trough |
| **3** | Malam (19:00) - Domba masuk kandang |
| **4** | Tengah Malam (23:00) - Serigala muncul |

### Kamera
| Tombol | Fungsi |
|--------|--------|
| **+** atau **=** | Zoom in |
| **-** atau **_** | Zoom out |
| **Arrow Keys** | Rotasi kamera (mode custom) |
| **Mouse Drag** | Rotasi kamera bebas |
| **Mouse Scroll** | Zoom in/out |
| **Right Click** | Menu view preset |

---

## 🕐 Periode Waktu

### 1️⃣ Pagi (07:00)
- ☀️ Langit cerah biru
- 🌅 Matahari terbit dengan sinar
- 🐑 Domba berkeliaran bebas
- 💡 Pencahayaan terang

### 2️⃣ Jam Makan (10:00)
- ☁️ Langit sedikit lebih gelap
- 🌾 Domba menuju hay bale (jerami)
- 🐑 Berkumpul di sekitar hay bale
- 👇 Kepala menunduk (makan jerami)
- 📍 Domba 0 → Hay bale kiri
- 📍 Domba 1 → Hay bale tengah-kiri
- 📍 Domba 2 → Hay bale kanan-atas

### 3️⃣ Malam (19:00)
- 🌙 Bulan muncul
- 🌃 Langit gelap
- 🏠 Domba berjalan ke pintu barn (smooth)
- 🚪 Domba masuk ke dalam dan hilang
- 🔦 Pencahayaan redup
- ✅ Tidak ada domba stuck!

### 4️⃣ Tengah Malam (23:00)
- 🌕 Bulan penuh
- 🌌 Sangat gelap
- 🐺 **SERIGALA MUNCUL!**
- 👀 Mata serigala menyala merah
- 🐑 Domba bersembunyi

---

## 📍 Lokasi Penting

### Objek Utama
- **Kincir Angin**: Tengah-kiri scene
- **Kandang Barn**: Kanan scene (dengan atap gable roof klasik)
- **Hay Bale 1**: Kiri (-8.8, -6.9)
- **Hay Bale 2**: Tengah-kiri (-6.0, -6.9)
- **Hay Bale 3**: Kanan-atas (8.4, 6.1)
- **Serigala**: Luar pagar kiri (-12.5, 5.0)

### Patch Rumput (9 lokasi)
1. Sekitar hay bale kiri
2. Sekitar hay bale tengah
3. Sekitar hay bale kanan
4. Dekat trough kiri
5. Dekat trough kanan
6. Area kosong tengah
7. Area depan
8. Area kiri tengah
9. Area kanan depan

---

## 🎨 UI Elements

### Jam Digital (Kiri Atas)
```
┌──────────┐
│  07:00   │  ← Format HH:MM
└──────────┘
```
- Background: Gelap semi-transparan
- Warna teks: Kuning cerah
- Update: Real-time sesuai currentTime

### Panel Instruksi (Kiri Bawah)
```
┌─────────────────────────┐
│ T : Toggle waktu        │
│ 1 : Siang (07:00)       │
│ 2 : Jam makan (10:00)   │
│ 3 : Malam (19:00)       │
│ 4 : Tengah malam (23:00)│
└─────────────────────────┘
```
- Background: Gelap semi-transparan
- Border: Putih
- Warna teks: Putih

---

## 🐑 Perilaku Domba

### Pagi (07:00)
- Berkeliaran dalam pola elips
- 3 domba dengan path berbeda
- Body bobbing saat berjalan
- Heading mengikuti arah gerakan

### Jam Makan (10:00)
- Berjalan ke hay bale terdekat
- Domba 0 & 1 → Hay bale kiri area
- Domba 2 → Hay bale kanan atas
- Posisi melingkar (120° interval)
- Kepala menunduk (y = 0.55)
- Menghadap ke hay bale

### Malam (19:00)
- **Fase 1**: Berjalan ke pintu kandang (smooth)
- **Fase 2**: Masuk ke dalam + mengecil
- Scale mengecil saat masuk
- Hilang sepenuhnya saat di dalam
- **Tidak stuck!**

### Tengah Malam (23:00)
- Bersembunyi di dalam kandang
- Tidak terlihat (scale = 0)

---

## 🐺 Serigala

### Karakteristik
- **Warna**: Abu-abu gelap
- **Mata**: Merah menyala (glowing)
- **Posisi**: Di luar pagar kiri
- **Pose**: Menghadap kandang (45°)
- **Muncul**: Hanya saat jam 23:00

### Anatomi
- Body: Kotak besar
- Head: Kotak sedang
- Snout: Kotak kecil (moncong)
- Ears: 2 kotak vertikal
- Eyes: 2 sphere merah menyala
- Legs: 4 kotak vertikal
- Tail: Kotak horizontal miring

---

## 🌾 Rumput

### Spesifikasi
- **Jumlah lokasi**: 9 patch
- **Density**: 18-25 blade per patch
- **Tinggi**: 0.15 - 0.35 (random)
- **Warna**: Hijau tua - hijau muda (variasi)
- **Render**: GL_LINES dengan line width 1.5

### Lokasi Strategis
- Sekitar hay bales (dekorasi)
- Dekat trough (area makan)
- Area kosong (fill empty space)

---

## 🏠 Detail Atap Barn

### Komponen Baru

#### 1. Shingles/Genteng
- 18 garis horizontal
- Warna: Merah muda gelap
- Mengikuti kemiringan atap

#### 2. Ridge Cap (Bubungan)
- Balok di puncak atap
- Warna: Coklat gelap
- Dimensi: 10.2 x 0.15 x 0.25

#### 3. Overhang (Tritisan)
- Depan dan belakang
- Warna: Merah muda terang
- Menonjol dari atap utama

---

## 🎯 Tips & Tricks

### Untuk Presentasi
1. Mulai dari **Pagi (1)** - tunjukkan domba berkeliaran
2. Pindah ke **Jam Makan (2)** - tunjukkan feeding behavior
3. Lanjut ke **Malam (3)** - tunjukkan domba masuk kandang
4. Akhiri dengan **Tengah Malam (4)** - tunjukkan serigala!

### Untuk Eksplorasi
- Gunakan **Mouse Drag** untuk rotasi bebas
- Gunakan **Scroll** untuk zoom optimal
- Tekan **T** untuk cycle cepat melalui waktu
- Perhatikan detail rumput dan atap saat zoom in

### Untuk Demo Fitur
- **UI**: Lihat kiri atas dan kiri bawah
- **Animasi**: Perhatikan transisi smooth antar waktu
- **Domba**: Ikuti pergerakan saat feeding time
- **Serigala**: Zoom ke luar pagar saat tengah malam
- **Rumput**: Zoom in ke area hay bales
- **Atap**: Zoom ke barn untuk lihat detail genteng

---

## 🔧 Troubleshooting

### Teks tidak muncul?
- Pastikan GLUT terinstall lengkap
- Coba restart program

### Rumput tidak terlihat?
- Zoom in lebih dekat
- Periksa GL_LINES support

### Serigala tidak muncul?
- Tekan tombol **4**
- Pastikan di waktu 23:00
- Zoom ke area luar pagar kiri

### Animasi lag?
- Kurangi density rumput
- Close aplikasi lain
- Update driver GPU

---

## 📊 Statistik Scene

| Item | Jumlah |
|------|--------|
| Periode Waktu | 4 |
| Domba | 3 |
| Serigala | 1 (saat tengah malam) |
| Trough | 2 |
| Hay Bales | 5 |
| Box Stacks | 2 |
| Patch Rumput | 9 |
| Blade Rumput | ~180 (total) |
| Pagar Segments | 6 |
| UI Elements | 2 |

---

## 🎓 Untuk Nilai Tambah

### Poin Presentasi
1. ✅ Sistem waktu kompleks (4 periode)
2. ✅ AI behavior (domba feeding, shelter)
3. ✅ Dynamic lighting (berubah per waktu)
4. ✅ UI informatif (jam + instruksi)
5. ✅ Detail visual (rumput, atap)
6. ✅ Easter egg (serigala tengah malam)
7. ✅ Smooth animations (interpolasi)
8. ✅ User-friendly controls

### Highlight Teknis
- Vertex arrays untuk baling-baling
- Interpolasi smooth untuk transisi
- State machine untuk perilaku domba
- Overlay 2D untuk UI
- Blending untuk transparansi
- Random seed konsisten untuk performa
- Modular code structure

---

## 📞 Support

Jika ada pertanyaan atau bug:
1. Cek README_MODIFIKASI.md untuk detail
2. Cek CHANGELOG.md untuk history
3. Lihat kode inline comments

**Good luck dengan presentasi! 🎉**
