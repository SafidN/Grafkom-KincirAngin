# 🌾 Windmill Farm - Day Night Cycle Simulation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![OpenGL](https://img.shields.io/badge/OpenGL-PyOpenGL-green.svg)](https://pyopengl.sourceforge.net/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Proyek Grafika Komputer 3D interaktif yang menampilkan scene peternakan dengan kincir angin, sistem waktu 4 periode, animasi domba, dan serigala yang mengintai di malam hari.

![Windmill Farm](https://img.shields.io/badge/Status-Complete-success)

---

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Screenshot](#-screenshot)
- [Instalasi](#-instalasi)
- [Cara Menggunakan](#-cara-menggunakan)
- [Kontrol](#-kontrol)
- [Sistem Waktu](#-sistem-waktu)
- [Teknologi](#-teknologi)
- [Dokumentasi](#-dokumentasi)
- [Kontributor](#-kontributor)

---

## ✨ Fitur Utama

### 🎬 Animasi & Interaktivitas
- **4 Periode Waktu**: Pagi (07:00), Jam Makan (10:00), Malam (19:00), Tengah Malam (23:00)
- **Kincir Angin Berputar**: Animasi baling-baling yang smooth
- **3 Domba Interaktif**: 
  - Berkeliaran di pagi hari
  - Makan di hay bale saat jam 10:00 dengan transisi smooth
  - Masuk kandang saat malam
- **Serigala Berpatroli**: Muncul di tengah malam dengan 4 jenis animasi
  - Patrol movement (pola elips)
  - Body bobbing
  - Leg animation
  - Tail swing

### 🌅 Sistem Siang-Malam Dinamis
- Transisi warna langit yang smooth
- Matahari dengan sinar di siang hari
- Bulan dengan kawah di malam hari
- Dynamic lighting yang berubah sesuai waktu
- Efek fog yang menyesuaikan

### 🎨 Detail Visual
- **Barn** dengan pintu ganda dan jendela
- **Pagar kayu** mengelilingi peternakan
- **Hay bales** (bal jerami) untuk domba makan
- **Trough** (tempat minum)
- **Rumput lebat** di 9 lokasi berbeda
- **Ground dengan sediment layers**

### 🎮 UI & Kontrol
- Jam digital di kiri atas
- Panel instruksi di kiri bawah
- Kontrol kamera bebas (mouse drag & zoom)
- Keyboard shortcuts untuk toggle waktu

---

## 📸 Screenshot

### Pagi (07:00)
Domba berkeliaran bebas, langit cerah, matahari terbit.

### Jam Makan (10:00)
Domba berkumpul di hay bale untuk makan dengan transisi smooth.

### Malam (19:00)
Domba masuk kandang, bulan muncul, langit gelap.

### Tengah Malam (23:00)
Serigala berpatroli di luar pagar dengan mata menyala!

---

## 🚀 Instalasi

### Prerequisites
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Langkah Instalasi

1. **Clone repository**
```bash
git clone https://github.com/SafidN/Grafkom-KincirAngin.git
cd Grafkom-KincirAngin
```

2. **Install dependencies**
```bash
pip install PyOpenGL PyOpenGL-accelerate numpy
```

3. **Jalankan program**
```bash
python kincir.py
```

---

## 🎮 Cara Menggunakan

### Quick Start
1. Jalankan `python kincir.py`
2. Gunakan mouse untuk rotasi kamera
3. Tekan tombol angka untuk mengubah waktu
4. Nikmati animasi!

### Tips
- Mulai dari **Pagi (1)** untuk melihat domba berkeliaran
- Toggle ke **Jam Makan (2)** untuk melihat transisi smooth domba ke hay bale
- Coba **Tengah Malam (4)** untuk melihat serigala berpatroli!
- Gunakan **scroll** untuk zoom in/out
- **Drag mouse** untuk rotasi kamera bebas

---

## ⌨️ Kontrol

### Keyboard

| Tombol | Fungsi |
|--------|--------|
| **T** | Toggle waktu (cycle: 07:00 → 10:00 → 19:00 → 23:00) |
| **1** | Pagi (07:00) - Domba berkeliaran |
| **2** | Jam Makan (10:00) - Domba makan di hay bale |
| **3** | Malam (19:00) - Domba masuk kandang |
| **4** | Tengah Malam (23:00) - Serigala muncul! |
| **+** / **=** | Zoom in |
| **-** / **_** | Zoom out |
| **Arrow Keys** | Rotasi kamera (mode custom) |

### Mouse

| Aksi | Fungsi |
|------|--------|
| **Left Click + Drag** | Rotasi kamera bebas |
| **Scroll Up** | Zoom in |
| **Scroll Down** | Zoom out |
| **Right Click** | Menu view preset |

---

## 🕐 Sistem Waktu

### Periode 1: Pagi (07:00)
- ☀️ Langit cerah biru
- 🌅 Matahari terbit dengan sinar
- 🐑 Domba berkeliaran bebas
- 💡 Pencahayaan terang

### Periode 2: Jam Makan (10:00)
- ☁️ Langit sedikit lebih gelap
- 🌾 Domba berjalan smooth ke hay bale
- 🐑 Berkumpul dan makan jerami
- 👇 Kepala menunduk

### Periode 3: Malam (19:00)
- 🌙 Bulan muncul dengan kawah
- 🌃 Langit gelap
- 🏠 Domba masuk kandang dengan smooth transition
- 🔦 Pencahayaan redup

### Periode 4: Tengah Malam (23:00)
- 🌕 Bulan penuh
- 🌌 Sangat gelap
- 🐺 **Serigala berpatroli di luar pagar!**
- 👀 Mata serigala menyala merah
- 🐑 Domba aman di dalam kandang

---

## 🛠️ Teknologi

### Libraries
- **PyOpenGL**: Rendering 3D
- **PyOpenGL-accelerate**: Optimasi performa
- **NumPy**: Matematika dan array operations
- **GLUT**: Window management dan input handling

### Teknik Grafika Komputer
- ✅ Transformasi 3D (translate, rotate, scale)
- ✅ Lighting & Material (ambient, diffuse, specular)
- ✅ Fog effects
- ✅ Vertex arrays
- ✅ Smooth interpolation
- ✅ State machine untuk AI behavior
- ✅ 2D overlay untuk UI
- ✅ Blending untuk transparansi

### Animasi
- ✅ Keyframe animation
- ✅ Procedural animation (sin/cos waves)
- ✅ Interpolasi linear (lerp)
- ✅ Smooth transitions
- ✅ Phase-based animation

---

## 📚 Dokumentasi

Proyek ini dilengkapi dengan dokumentasi lengkap:

- **[README_MODIFIKASI.md](README_MODIFIKASI.md)** - Dokumentasi lengkap semua fitur
- **[CHANGELOG.md](CHANGELOG.md)** - History perubahan versi
- **[QUICK_GUIDE.md](QUICK_GUIDE.md)** - Panduan cepat untuk presentasi
- **[PRESENTATION_NOTES.md](PRESENTATION_NOTES.md)** - Script presentasi detail
- **[UPDATE_FIXES.md](UPDATE_FIXES.md)** - Bug fixes dan improvements
- **[ANIMATION_UPDATE.md](ANIMATION_UPDATE.md)** - Dokumentasi sistem animasi
- **[ROOF_FIX.md](ROOF_FIX.md)** - Detail perbaikan atap barn

---

## 📊 Statistik Proyek

| Metric | Value |
|--------|-------|
| Total Lines of Code | ~1,400 |
| 3D Objects | 15+ types |
| Animations | 8 different |
| Time Periods | 4 |
| Sheep Behaviors | 3 states |
| Wolf Animations | 4 types |
| Grass Patches | 9 locations |
| Frame Rate | 60 FPS |
| Documentation Files | 7 |

---

## 🎯 Fitur Teknis

### Performance Optimizations
- Pseudo-random untuk grass (menghindari import random di render loop)
- Efficient geometry rendering
- Proper culling
- Optimized interpolation

### AI Behaviors
- **Domba**: State machine (roaming → feeding → sheltering)
- **Serigala**: Patrol pattern dengan elips equation
- **Smooth transitions**: Interpolasi untuk semua movement

### Visual Effects
- Dynamic sky color blending
- Fog density adjustment
- Light position & intensity changes
- Glowing eyes (serigala)
- Body bobbing (walking animation)

---

## 🤝 Kontributor

- **SafidN** - Developer & Designer
- **Kiro AI** - Code Assistant & Documentation

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- PyOpenGL community
- OpenGL documentation
- Computer Graphics course materials
- Inspiration from classic farm simulation games

---

## 📞 Contact

- **GitHub**: [@SafidN](https://github.com/SafidN)
- **Repository**: [Grafkom-KincirAngin](https://github.com/SafidN/Grafkom-KincirAngin)

---

## 🌟 Star History

Jika proyek ini membantu Anda, jangan lupa beri ⭐ di GitHub!

---

**Made with ❤️ for Computer Graphics Course**

**Status**: ✅ Complete & Ready for Presentation

**Version**: 2.2 (Final)

---

## 🚀 Future Enhancements (Ideas)

- [ ] Suara ambient (burung, serigala howl)
- [ ] Partikel debu saat domba berjalan
- [ ] Weather system (hujan, awan)
- [ ] Shadow mapping
- [ ] Texture mapping
- [ ] More animals (ayam, sapi)
- [ ] VR support
- [ ] Auto day-night cycle

---

**Happy Coding! 🎉**
