from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import numpy as np

# Variabel global
angleBlade = 0.0
goatWalkPhase = 0.0
dayNightTarget = 0.0
dayNightBlend = 0.0
viewAngleX = 12.0
viewAngleY = -18.0
viewMode = 5
zoomDistance = -22.0

isDragging = False
lastMouseX = 0
lastMouseY = 0

# Sistem waktu baru (0=07:00, 1=10:00, 2=19:00, 3=23:00)
currentTime = 0
targetTime = 0
timeBlend = 0.0
previousTime = 0  # Untuk tracking transisi
transitionStartBlend = 0.0  # Blend saat transisi dimulai

# Animasi serigala
wolfWalkPhase = 0.0

# Animasi peternak (farmer)
farmerWalkPhase = 0.0
farmerArmSwing = 0.0

# Animasi sungai
riverFlowPhase = 0.0

# Animasi awan
cloudPhase = 0.0

GOAT_CONFIGS = [
    {"index": 0, "base_x": -5.8, "base_z": 3.2, "scale": 0.8, "radius_x": 0.8, "radius_z": 0.5, "phase": 0.0},
    {"index": 1, "base_x": -1.8, "base_z": 4.8, "scale": 0.75, "radius_x": 0.6, "radius_z": 0.45, "phase": 1.8},
    {"index": 2, "base_x": 2.8, "base_z": 2.7, "scale": 0.82, "radius_x": 0.7, "radius_z": 0.55, "phase": 3.1},
]

SHEEP_BARN_SPOTS = [
    {"door_x": 2.55, "door_z": 1.5, "inside_x": 3.1, "inside_z": 0.45},
    {"door_x": 3.1, "door_z": 1.0, "inside_x": 3.45, "inside_z": 0.0},
    {"door_x": 3.62, "door_z": 0.55, "inside_x": 3.85, "inside_z": -0.35},
]

DAY_SKY_COLOR = (0.48, 0.75, 1.0, 1.0)
NIGHT_SKY_COLOR = (0.05, 0.08, 0.18, 1.0)

# Konfigurasi waktu untuk 4 periode
TIME_CONFIGS = {
    0: {"hour": 7, "minute": 0, "name": "Pagi", "sky_blend": 0.0},      # 07:00 Pagi
    1: {"hour": 10, "minute": 0, "name": "Siang", "sky_blend": 0.15},   # 10:00 Jam Makan
    2: {"hour": 19, "minute": 0, "name": "Sore", "sky_blend": 0.75},    # 19:00 Malam
    3: {"hour": 23, "minute": 0, "name": "Malam", "sky_blend": 1.0},    # 23:00 Tengah Malam
}

# Posisi hay bale untuk feeding time
HAY_BALE_POSITIONS = [
    {"x": -8.8, "z": -6.9},  # Hay bale kiri
    {"x": -6.0, "z": -6.9},  # Hay bale tengah kiri
    {"x": 8.4, "z": 6.1},    # Hay bale kanan atas
]


def create_blade_vertices():
    blade_vertices = []
    blade_indices = []
    blade_length = 3.5
    num_sections = 16
    blade_width = 0.15
    blade_thickness = 0.05
    pitch_angle = 20.0
    twist_angle = -10.0

    for i in range(num_sections):
        p = float(i) / (num_sections - 1)
        t = pitch_angle + p * twist_angle
        w = blade_width * (1.0 - p * 0.7)
        th = blade_thickness * (1.0 - p * 0.9)
        rad_twist = np.radians(t)

        x1, z1 = 0.0, -th / 2
        blade_vertices.append([x1 * np.cos(rad_twist) - z1 * np.sin(rad_twist), p * blade_length, x1 * np.sin(rad_twist) + z1 * np.cos(rad_twist)])
        x2, z2 = 0.0, th / 2
        blade_vertices.append([x2 * np.cos(rad_twist) - z2 * np.sin(rad_twist), p * blade_length, x2 * np.sin(rad_twist) + z2 * np.cos(rad_twist)])
        x3, z3 = w, th / 2
        blade_vertices.append([x3 * np.cos(rad_twist) - z3 * np.sin(rad_twist), p * blade_length, x3 * np.sin(rad_twist) + z3 * np.cos(rad_twist)])
        x4, z4 = w, -th / 2
        blade_vertices.append([x4 * np.cos(rad_twist) - z4 * np.sin(rad_twist), p * blade_length, x4 * np.sin(rad_twist) + z4 * np.cos(rad_twist)])

    for i in range(num_sections - 1):
        for j in range(4):
            v0 = i * 4 + j
            v1 = (i + 1) * 4 + j
            v2 = (i + 1) * 4 + (j + 1) % 4
            v3 = i * 4 + (j + 1) % 4
            blade_indices.extend([v0, v1, v2, v3])

    return np.array(blade_vertices, dtype=np.float32), np.array(blade_indices, dtype=np.uint32)


BLADE_VERTICES, BLADE_INDICES = create_blade_vertices()


def init():
    sky_color = DAY_SKY_COLOR
    glClearColor(sky_color[0], sky_color[1], sky_color[2], sky_color[3])
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    light_pos = [10.0, 18.0, 6.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.95, 0.95, 0.9, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.4, 0.4, 0.4, 1.0])

    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogfv(GL_FOG_COLOR, sky_color)
    glFogf(GL_FOG_DENSITY, 0.016)
    glHint(GL_FOG_HINT, GL_NICEST)
    
    # Enable blending untuk transparansi UI
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t):
    t = clamp(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def mix_color(color_a, color_b, t):
    return tuple(lerp(a, b, t) for a, b in zip(color_a, color_b))


def apply_environment_colors():
    sky = mix_color(DAY_SKY_COLOR, NIGHT_SKY_COLOR, dayNightBlend)
    fog_density = lerp(0.016, 0.03, dayNightBlend)
    glClearColor(sky[0], sky[1], sky[2], sky[3])
    glFogfv(GL_FOG_COLOR, sky)
    glFogf(GL_FOG_DENSITY, fog_density)


def apply_environment_lighting():
    light_pos = [
        lerp(10.0, -8.0, dayNightBlend),
        lerp(18.0, 13.0, dayNightBlend),
        lerp(6.0, -6.0, dayNightBlend),
        1.0,
    ]
    diffuse = [
        lerp(0.95, 0.25, dayNightBlend),
        lerp(0.95, 0.3, dayNightBlend),
        lerp(0.9, 0.45, dayNightBlend),
        1.0,
    ]
    specular = [
        lerp(0.3, 0.12, dayNightBlend),
        lerp(0.3, 0.14, dayNightBlend),
        lerp(0.3, 0.18, dayNightBlend),
        1.0,
    ]
    ambient = [
        lerp(0.4, 0.16, dayNightBlend),
        lerp(0.4, 0.17, dayNightBlend),
        lerp(0.4, 0.24, dayNightBlend),
        1.0,
    ]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient)


def draw_text_stroke(x, y, text, scale=0.15):
    """Menggambar teks menggunakan GLUT stroke characters"""
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(scale, scale, scale)
    for char in text:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))
    glPopMatrix()


def draw_time_display():
    """Menampilkan jam digital di kiri atas"""
    time_config = TIME_CONFIGS[currentTime]
    time_str = f"{time_config['hour']:02d}:{time_config['minute']:02d}"
    
    # Simpan state
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 900, 0, 650, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Background panel
    glColor4f(0.1, 0.1, 0.1, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(10, 600)
    glVertex2f(150, 600)
    glVertex2f(150, 640)
    glVertex2f(10, 640)
    glEnd()
    
    # Teks jam
    glColor3f(1.0, 1.0, 0.3)
    glLineWidth(2.5)
    draw_text_stroke(20, 610, time_str, 0.18)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    # Restore state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_instructions_panel():
    """Menampilkan panel instruksi dengan tombol untuk mobile"""
    
    # Simpan state
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 900, 0, 650, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Background panel
    glColor4f(0.1, 0.1, 0.1, 0.75)
    glBegin(GL_QUADS)
    glVertex2f(10, 10)
    glVertex2f(280, 10)
    glVertex2f(280, 200)
    glVertex2f(10, 200)
    glEnd()
    
    # Border
    glColor3f(0.8, 0.8, 0.8)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(10, 10)
    glVertex2f(280, 10)
    glVertex2f(280, 200)
    glVertex2f(10, 200)
    glEnd()
    
    # Tombol-tombol dengan simbol
    buttons = [
        {"key": "T", "label": "T : untuk toggle waktu.", "y": 170, "icon": "T"},
        {"key": "1", "label": "1: untuk pagi (07:00)", "y": 135, "icon": "1"},
        {"key": "2", "label": "2: untuk siang (10:00)", "y": 100, "icon": "2"},
    ]
    
    for btn in buttons:
        # Tombol background
        if btn["key"] == str(currentTime + 1) or (btn["key"] == "T"):
            # Highlight tombol aktif
            glColor4f(0.3, 0.5, 0.7, 0.8)
        else:
            glColor4f(0.2, 0.2, 0.2, 0.8)
        
        # Kotak tombol
        btn_x = 20
        btn_y = btn["y"]
        btn_size = 25
        
        glBegin(GL_QUADS)
        glVertex2f(btn_x, btn_y)
        glVertex2f(btn_x + btn_size, btn_y)
        glVertex2f(btn_x + btn_size, btn_y + btn_size)
        glVertex2f(btn_x, btn_y + btn_size)
        glEnd()
        
        # Border tombol
        glColor3f(0.9, 0.9, 0.9)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex2f(btn_x, btn_y)
        glVertex2f(btn_x + btn_size, btn_y)
        glVertex2f(btn_x + btn_size, btn_y + btn_size)
        glVertex2f(btn_x, btn_y + btn_size)
        glEnd()
        
        # Icon/simbol di tombol
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        draw_text_stroke(btn_x + 5, btn_y + 5, btn["icon"], 0.12)
        
        # Label teks
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(1.5)
        draw_text_stroke(btn_x + btn_size + 10, btn_y + 5, btn["label"], 0.08)
    
    # Tambahan info untuk jam 3 dan 4
    extra_info = [
        {"label": "3: untuk malam (19:00)", "y": 65},
        {"label": "4: untuk tengah malam (23:00)", "y": 30},
    ]
    
    for info in extra_info:
        # Tombol kecil
        btn_x = 20
        btn_y = info["y"]
        btn_size = 25
        btn_num = "3" if info["y"] == 65 else "4"
        
        if btn_num == str(currentTime + 1):
            glColor4f(0.3, 0.5, 0.7, 0.8)
        else:
            glColor4f(0.2, 0.2, 0.2, 0.8)
        
        glBegin(GL_QUADS)
        glVertex2f(btn_x, btn_y)
        glVertex2f(btn_x + btn_size, btn_y)
        glVertex2f(btn_x + btn_size, btn_y + btn_size)
        glVertex2f(btn_x, btn_y + btn_size)
        glEnd()
        
        glColor3f(0.9, 0.9, 0.9)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex2f(btn_x, btn_y)
        glVertex2f(btn_x + btn_size, btn_y)
        glVertex2f(btn_x + btn_size, btn_y + btn_size)
        glVertex2f(btn_x, btn_y + btn_size)
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        draw_text_stroke(btn_x + 5, btn_y + 5, btn_num, 0.12)
        
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(1.5)
        draw_text_stroke(btn_x + btn_size + 10, btn_y + 5, info["label"], 0.08)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    # Restore state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_grass_patch(x, z, density=20, size=1.5):
    """Menggambar patch rumput lebat"""
    glDisable(GL_LIGHTING)
    
    # Gunakan seed berbasis posisi untuk konsistensi tanpa import random setiap frame
    seed_val = int(x * 100 + z * 100)
    
    for i in range(density):
        # Pseudo-random menggunakan sin/cos untuk menghindari import random
        t = (seed_val + i * 137.508) % 360  # Golden angle
        offset_x = np.sin(np.radians(t)) * size/2
        offset_z = np.cos(np.radians(t * 1.618)) * size/2
        height = 0.15 + (np.sin(np.radians(t * 2.5)) + 1) * 0.1
        
        # Variasi warna hijau
        green_var = (np.sin(np.radians(t * 3)) + 1) * 0.1
        glColor3f(0.2 + green_var, 0.5 + green_var, 0.15 + green_var)
        
        # Gambar blade rumput sebagai garis
        glLineWidth(1.5)
        glBegin(GL_LINES)
        glVertex3f(x + offset_x, 0.04, z + offset_z)
        tip_x = x + offset_x + np.sin(np.radians(t * 5)) * 0.05
        tip_z = z + offset_z + np.cos(np.radians(t * 5)) * 0.05
        glVertex3f(tip_x, 0.04 + height, tip_z)
        glEnd()
    
    glEnable(GL_LIGHTING)


def draw_tree(x, z, height=3.5, trunk_radius=0.25, canopy_radius=1.2):
    """Menggambar pohon dengan batang dan kanopi"""
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    
    # Trunk (batang pohon)
    glColor3f(0.4, 0.26, 0.13)  # Coklat
    glPushMatrix()
    glTranslatef(0.0, height/2, 0.0)
    glScalef(trunk_radius, height, trunk_radius)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Canopy (daun) - 3 layer untuk tampilan lebih penuh
    # Layer bawah (paling besar)
    glColor3f(0.15, 0.5, 0.15)  # Hijau gelap
    glPushMatrix()
    glTranslatef(0.0, height * 0.7, 0.0)
    glutSolidSphere(canopy_radius * 1.2, 12, 12)
    glPopMatrix()
    
    # Layer tengah
    glColor3f(0.2, 0.6, 0.2)  # Hijau sedang
    glPushMatrix()
    glTranslatef(0.0, height * 0.85, 0.0)
    glutSolidSphere(canopy_radius, 12, 12)
    glPopMatrix()
    
    # Layer atas (paling kecil)
    glColor3f(0.25, 0.65, 0.25)  # Hijau terang
    glPushMatrix()
    glTranslatef(0.0, height, 0.0)
    glutSolidSphere(canopy_radius * 0.7, 12, 12)
    glPopMatrix()
    
    glPopMatrix()


def draw_pine_tree(x, z, height=4.0, base_radius=1.0):
    """Menggambar pohon pinus (cone shape)"""
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    
    # Trunk
    glColor3f(0.35, 0.22, 0.12)  # Coklat gelap
    glPushMatrix()
    glTranslatef(0.0, height * 0.25, 0.0)
    glScalef(0.2, height * 0.5, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Pine canopy - 3 cone layers
    cone_colors = [
        (0.12, 0.45, 0.12),  # Hijau gelap
        (0.15, 0.5, 0.15),   # Hijau sedang
        (0.18, 0.55, 0.18),  # Hijau terang
    ]
    
    for i, color in enumerate(cone_colors):
        glColor3f(*color)
        glPushMatrix()
        y_offset = height * 0.4 + i * height * 0.2
        glTranslatef(0.0, y_offset, 0.0)
        glRotatef(-90, 1, 0, 0)
        radius = base_radius * (1.0 - i * 0.25)
        cone_height = height * 0.35
        glutSolidCone(radius, cone_height, 12, 8)
        glPopMatrix()
    
    glPopMatrix()


def draw_river():
    """Menggambar sungai dengan animasi arus"""
    # Sungai mengalir dari kiri belakang ke kanan belakang (di belakang barn)
    river_start_x = -16.0
    river_end_x = 14.0
    river_z = -9.5  # Di belakang barn
    river_width = 2.5
    
    # Base sungai (air)
    glColor3f(0.2, 0.4, 0.7)  # Biru air
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(river_start_x, 0.01, river_z - river_width/2)
    glVertex3f(river_end_x, 0.01, river_z - river_width/2)
    glVertex3f(river_end_x, 0.01, river_z + river_width/2)
    glVertex3f(river_start_x, 0.01, river_z + river_width/2)
    glEnd()
    
    # Animasi arus air (gelombang bergerak)
    glDisable(GL_LIGHTING)
    num_waves = 15
    wave_length = (river_end_x - river_start_x) / num_waves
    
    for i in range(num_waves):
        # Hitung posisi gelombang dengan offset animasi
        wave_offset = (riverFlowPhase + i * 0.4) % (np.pi * 2)
        wave_x = river_start_x + i * wave_length + np.sin(wave_offset) * 0.3
        wave_amplitude = 0.15 + np.sin(wave_offset) * 0.08
        
        # Warna gelombang (lebih terang dari air)
        wave_brightness = 0.5 + np.sin(wave_offset) * 0.2
        glColor3f(0.3 + wave_brightness * 0.2, 0.5 + wave_brightness * 0.2, 0.8 + wave_brightness * 0.1)
        
        # Gambar gelombang sebagai garis melengkung
        glLineWidth(2.0)
        glBegin(GL_LINE_STRIP)
        for j in range(8):
            t = j / 7.0
            x = wave_x + t * wave_length * 0.6
            z = river_z - river_width/2 + t * river_width
            y = 0.02 + np.sin(t * np.pi) * wave_amplitude * 0.1
            glVertex3f(x, y, z)
        glEnd()
    
    glEnable(GL_LIGHTING)
    
    # Tepi sungai (tanah/rumput)
    glColor3f(0.3, 0.5, 0.2)  # Hijau gelap
    
    # Tepi kiri
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(river_start_x, 0.01, river_z - river_width/2 - 0.5)
    glVertex3f(river_end_x, 0.01, river_z - river_width/2 - 0.5)
    glVertex3f(river_end_x, 0.01, river_z - river_width/2)
    glVertex3f(river_start_x, 0.01, river_z - river_width/2)
    glEnd()
    
    # Tepi kanan
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(river_start_x, 0.01, river_z + river_width/2)
    glVertex3f(river_end_x, 0.01, river_z + river_width/2)
    glVertex3f(river_end_x, 0.01, river_z + river_width/2 + 0.5)
    glVertex3f(river_start_x, 0.01, river_z + river_width/2 + 0.5)
    glEnd()


def draw_farmer():
    """Menggambar peternak (farmer) dengan animasi dan transisi lengkap"""
    
    # Hitung posisi dan alpha berdasarkan waktu
    farmer_alpha = 0.0
    farmer_x = 0.0
    farmer_z = 0.0
    farmer_heading = 0.0
    farmer_action = None  # 'entering', 'herding', 'exiting'
    
    gate_x = 2.85  # Posisi gerbang
    gate_z = 8.5
    center_x = 0.0  # Posisi tengah (jam 10)
    center_z = 3.0
    door_x = 2.2  # Posisi depan pintu barn (jam 19)
    door_z = 1.8
    
    is_transitioning = (previousTime != currentTime)
    
    # ===== JAM 7 (PAGI) - TIDAK ADA PETERNAK =====
    if currentTime == 0:
        if is_transitioning and previousTime == 1:
            # Transisi dari jam 10 ke jam 7 - peternak keluar
            transition_progress = 1.0 - (abs(dayNightBlend - TIME_CONFIGS[0]["sky_blend"]) / abs(TIME_CONFIGS[1]["sky_blend"] - TIME_CONFIGS[0]["sky_blend"]))
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            # Fade out sambil jalan ke gerbang
            farmer_alpha = 1.0 - transition_progress
            farmer_x = lerp(center_x, gate_x, transition_progress)
            farmer_z = lerp(center_z, gate_z, transition_progress)
            farmer_heading = 0.0  # Menghadap gerbang
            farmer_action = 'exiting'
        
        elif is_transitioning and previousTime == 2:
            # Transisi dari jam 19 ke jam 7 - peternak keluar dari pintu
            transition_progress = 1.0 - (abs(dayNightBlend - TIME_CONFIGS[0]["sky_blend"]) / abs(TIME_CONFIGS[2]["sky_blend"] - TIME_CONFIGS[0]["sky_blend"]))
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            # Fade out sambil jalan ke gerbang
            farmer_alpha = 1.0 - transition_progress
            farmer_x = lerp(door_x, gate_x, transition_progress)
            farmer_z = lerp(door_z, gate_z, transition_progress)
            farmer_heading = 0.0
            farmer_action = 'exiting'
        
        elif is_transitioning and previousTime == 3:
            # Transisi dari jam 23 ke jam 7 - sudah keluar, tidak render
            return
        else:
            # Tidak ada peternak di jam 7
            return
    
    # ===== JAM 10 (JAM MAKAN) - PETERNAK DI TENGAH =====
    elif currentTime == 1:
        if is_transitioning and previousTime == 0:
            # Transisi dari jam 7 ke jam 10 - peternak masuk
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[0]["sky_blend"]) / abs(TIME_CONFIGS[1]["sky_blend"] - TIME_CONFIGS[0]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            # Fade in sambil jalan dari gerbang ke tengah
            if transition_progress < 0.3:
                farmer_alpha = transition_progress / 0.3
            else:
                farmer_alpha = 1.0
            
            farmer_x = lerp(gate_x, center_x, transition_progress)
            farmer_z = lerp(gate_z, center_z, transition_progress)
            farmer_heading = 180.0  # Menghadap ke dalam
            farmer_action = 'entering'
        
        elif is_transitioning and previousTime == 2:
            # Transisi dari jam 19 ke jam 10 - peternak jalan dari pintu ke tengah
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[2]["sky_blend"]) / abs(TIME_CONFIGS[1]["sky_blend"] - TIME_CONFIGS[2]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            farmer_alpha = 1.0
            farmer_x = lerp(door_x, center_x, transition_progress)
            farmer_z = lerp(door_z, center_z, transition_progress)
            farmer_heading = 180.0
            farmer_action = 'entering'
        
        elif is_transitioning and previousTime == 3:
            # Transisi dari jam 23 ke jam 10 - peternak masuk dari gerbang
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[3]["sky_blend"]) / abs(TIME_CONFIGS[1]["sky_blend"] - TIME_CONFIGS[3]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            if transition_progress < 0.3:
                farmer_alpha = transition_progress / 0.3
            else:
                farmer_alpha = 1.0
            
            farmer_x = lerp(gate_x, center_x, transition_progress)
            farmer_z = lerp(gate_z, center_z, transition_progress)
            farmer_heading = 180.0
            farmer_action = 'entering'
        
        else:
            # Sudah di posisi, berdiri di tengah
            farmer_alpha = 1.0
            farmer_x = center_x
            farmer_z = center_z
            farmer_heading = 180.0
            farmer_action = 'herding'
    
    # ===== JAM 19 (MALAM) - PETERNAK DI PINTU BARN =====
    elif currentTime == 2:
        if is_transitioning and previousTime == 0:
            # Transisi dari jam 7 ke jam 19 - peternak masuk ke pintu
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[0]["sky_blend"]) / abs(TIME_CONFIGS[2]["sky_blend"] - TIME_CONFIGS[0]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            if transition_progress < 0.3:
                farmer_alpha = transition_progress / 0.3
            else:
                farmer_alpha = 1.0
            
            # Jalan dari gerbang ke pintu
            if transition_progress < 0.5:
                # Fase 1: Gerbang ke tengah
                phase1 = transition_progress / 0.5
                farmer_x = lerp(gate_x, center_x, phase1)
                farmer_z = lerp(gate_z, center_z, phase1)
            else:
                # Fase 2: Tengah ke pintu
                phase2 = (transition_progress - 0.5) / 0.5
                farmer_x = lerp(center_x, door_x, phase2)
                farmer_z = lerp(center_z, door_z, phase2)
            
            farmer_heading = 90.0
            farmer_action = 'entering'
        
        elif is_transitioning and previousTime == 1:
            # Transisi dari jam 10 ke jam 19 - peternak jalan dari tengah ke pintu
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[1]["sky_blend"]) / abs(TIME_CONFIGS[2]["sky_blend"] - TIME_CONFIGS[1]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            farmer_alpha = 1.0
            farmer_x = lerp(center_x, door_x, transition_progress)
            farmer_z = lerp(center_z, door_z, transition_progress)
            farmer_heading = 90.0
            farmer_action = 'entering'
        
        elif is_transitioning and previousTime == 3:
            # Transisi dari jam 23 ke jam 19 - peternak masuk dari gerbang ke pintu
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[3]["sky_blend"]) / abs(TIME_CONFIGS[2]["sky_blend"] - TIME_CONFIGS[3]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            if transition_progress < 0.3:
                farmer_alpha = transition_progress / 0.3
            else:
                farmer_alpha = 1.0
            
            # Jalan dari gerbang ke pintu
            if transition_progress < 0.5:
                phase1 = transition_progress / 0.5
                farmer_x = lerp(gate_x, center_x, phase1)
                farmer_z = lerp(gate_z, center_z, phase1)
            else:
                phase2 = (transition_progress - 0.5) / 0.5
                farmer_x = lerp(center_x, door_x, phase2)
                farmer_z = lerp(center_z, door_z, phase2)
            
            farmer_heading = 90.0
            farmer_action = 'entering'
        
        else:
            # Sudah di posisi, berdiri di pintu
            farmer_alpha = 1.0
            farmer_x = door_x
            farmer_z = door_z
            farmer_heading = 90.0
            farmer_action = 'herding'
    
    # ===== JAM 23 (TENGAH MALAM) - PETERNAK KELUAR =====
    elif currentTime == 3:
        if is_transitioning and previousTime == 1:
            # Transisi dari jam 10 ke jam 23 - peternak keluar dari tengah
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[1]["sky_blend"]) / abs(TIME_CONFIGS[3]["sky_blend"] - TIME_CONFIGS[1]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            # Fade out sambil jalan ke gerbang
            farmer_alpha = 1.0 - transition_progress
            farmer_x = lerp(center_x, gate_x, transition_progress)
            farmer_z = lerp(center_z, gate_z, transition_progress)
            farmer_heading = 0.0
            farmer_action = 'exiting'
        
        elif is_transitioning and previousTime == 2:
            # Transisi dari jam 19 ke jam 23 - peternak keluar dari pintu
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[2]["sky_blend"]) / abs(TIME_CONFIGS[3]["sky_blend"] - TIME_CONFIGS[2]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            # Fade out sambil jalan ke gerbang
            farmer_alpha = 1.0 - transition_progress
            farmer_x = lerp(door_x, gate_x, transition_progress)
            farmer_z = lerp(door_z, gate_z, transition_progress)
            farmer_heading = 0.0
            farmer_action = 'exiting'
        
        elif is_transitioning and previousTime == 0:
            # Transisi dari jam 7 ke jam 23 - tidak ada peternak
            return
        
        else:
            # Sudah keluar, tidak render
            return
    
    # Jika alpha terlalu kecil, tidak render
    if farmer_alpha < 0.01:
        return
    
    # Animasi berjalan
    if farmer_action in ['entering', 'exiting']:
        leg_swing = np.sin(farmerWalkPhase * 4.0) * 20.0
        arm_swing = np.sin(farmerWalkPhase * 4.0) * 15.0
        body_bob = abs(np.sin(farmerWalkPhase * 4.0)) * 0.05
    else:
        # Berdiri, animasi subtle
        leg_swing = 0.0
        arm_swing = np.sin(farmerArmSwing) * 10.0  # Lambaian tangan
        body_bob = 0.0
    
    glPushMatrix()
    glTranslatef(farmer_x, 0.0, farmer_z)
    glRotatef(farmer_heading, 0, 1, 0)
    
    # Body
    glColor4f(0.2, 0.3, 0.6, farmer_alpha)  # Baju biru
    glPushMatrix()
    glTranslatef(0.0, 1.2 + body_bob, 0.0)
    glScalef(0.6, 0.8, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Head
    glColor4f(0.9, 0.7, 0.6, farmer_alpha)  # Kulit
    glPushMatrix()
    glTranslatef(0.0, 1.9 + body_bob, 0.0)
    glutSolidSphere(0.25, 12, 12)
    glPopMatrix()
    
    # Hat (topi)
    glColor4f(0.6, 0.4, 0.2, farmer_alpha)  # Coklat
    glPushMatrix()
    glTranslatef(0.0, 2.15 + body_bob, 0.0)
    glScalef(0.35, 0.15, 0.35)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0.0, 2.25 + body_bob, 0.0)
    glScalef(0.25, 0.2, 0.25)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Arms
    glColor4f(0.2, 0.3, 0.6, farmer_alpha)
    
    # Left arm
    glPushMatrix()
    glTranslatef(-0.4, 1.3 + body_bob, 0.0)
    glRotatef(arm_swing, 1, 0, 0)
    glTranslatef(0.0, -0.25, 0.0)
    glScalef(0.15, 0.5, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Right arm
    glPushMatrix()
    glTranslatef(0.4, 1.3 + body_bob, 0.0)
    glRotatef(-arm_swing, 1, 0, 0)
    glTranslatef(0.0, -0.25, 0.0)
    glScalef(0.15, 0.5, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Legs
    glColor4f(0.3, 0.2, 0.1, farmer_alpha)  # Celana coklat
    
    # Left leg
    glPushMatrix()
    glTranslatef(-0.15, 0.6, 0.0)
    glRotatef(leg_swing, 1, 0, 0)
    glTranslatef(0.0, -0.3, 0.0)
    glScalef(0.18, 0.6, 0.18)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Right leg
    glPushMatrix()
    glTranslatef(0.15, 0.6, 0.0)
    glRotatef(-leg_swing, 1, 0, 0)
    glTranslatef(0.0, -0.3, 0.0)
    glScalef(0.18, 0.6, 0.18)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Boots
    glColor4f(0.2, 0.15, 0.1, farmer_alpha)
    for boot_x in (-0.15, 0.15):
        glPushMatrix()
        glTranslatef(boot_x, 0.1, 0.05)
        glScalef(0.2, 0.15, 0.25)
        glutSolidCube(1.0)
        glPopMatrix()
    
    glPopMatrix()


def draw_wolf():
    """Menggambar serigala yang mengintai dengan animasi jalan-jalan"""
    
    wolf_alpha = 0.0
    
    # Logika fade in/out berdasarkan transisi waktu
    if currentTime == 3:
        # Jam 23:00 - serigala muncul
        if previousTime != 3:
            # Baru masuk ke jam 23:00 - fade in
            # dayNightBlend akan naik dari transitionStartBlend ke 1.0
            if dayNightBlend < 1.0:
                # Hitung progress fade in (0.0 to 1.0)
                fade_range = 1.0 - transitionStartBlend
                if fade_range > 0.01:
                    fade_progress = (dayNightBlend - transitionStartBlend) / fade_range
                    wolf_alpha = clamp(fade_progress, 0.0, 1.0)
                else:
                    wolf_alpha = 1.0
            else:
                wolf_alpha = 1.0
        else:
            # Sudah di jam 23:00 dari sebelumnya
            wolf_alpha = 1.0
    else:
        # Bukan jam 23:00
        if previousTime == 3:
            # Baru keluar dari jam 23:00 - fade out
            # dayNightBlend akan turun dari 1.0 ke target blend
            target_blend = TIME_CONFIGS[currentTime]["sky_blend"]
            if dayNightBlend > target_blend:
                # Hitung progress fade out (1.0 to 0.0)
                fade_range = 1.0 - target_blend
                if fade_range > 0.01:
                    fade_progress = (dayNightBlend - target_blend) / fade_range
                    wolf_alpha = clamp(fade_progress, 0.0, 1.0)
                else:
                    wolf_alpha = 0.0
            else:
                wolf_alpha = 0.0
        else:
            # Tidak di jam 23:00 dan tidak baru keluar
            return
    
    # Jika alpha terlalu kecil, tidak perlu render
    if wolf_alpha < 0.01:
        return
    
    # Animasi jalan-jalan dalam pola elips (sama seperti domba tapi lebih cepat)
    # Pagar kiri di x = -11.0, jadi serigala patrol di luar dengan jarak aman
    patrol_radius_x = 1.2
    patrol_radius_z = 2.5
    base_x = -14.0
    base_z = 2.0
    
    # Posisi serigala berdasarkan fase animasi (sama seperti domba)
    orbit_x = np.cos(wolfWalkPhase) * patrol_radius_x
    orbit_z = np.sin(wolfWalkPhase * 0.85) * patrol_radius_z
    wolf_x = base_x + orbit_x
    wolf_z = base_z + orbit_z
    
    # Heading calculation (sama seperti domba)
    heading_x = -np.sin(wolfWalkPhase) * patrol_radius_x
    heading_z = np.cos(wolfWalkPhase * 0.85) * patrol_radius_z * 0.85
    heading = -np.degrees(np.arctan2(heading_z, heading_x))
    
    # Body bobbing saat berjalan
    body_bob = 0.03 * abs(np.sin(wolfWalkPhase * 4.0))
    
    glPushMatrix()
    glTranslatef(wolf_x, 0.35 + body_bob, wolf_z)  # Turunkan dari 0.5 ke 0.35 agar lebih menjorok ke tanah
    glRotatef(heading, 0, 1, 0)
    
    # Body (gelap) dengan alpha
    glColor4f(0.15, 0.15, 0.18, wolf_alpha)
    glPushMatrix()
    glScalef(1.2, 0.7, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(0.7, 0.2, 0.0)
    glScalef(0.6, 0.5, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Snout
    glColor4f(0.12, 0.12, 0.15, wolf_alpha)
    glPushMatrix()
    glTranslatef(1.0, 0.1, 0.0)
    glScalef(0.3, 0.2, 0.25)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Ears
    glColor4f(0.15, 0.15, 0.18, wolf_alpha)
    for ear_z in (-0.15, 0.15):
        glPushMatrix()
        glTranslatef(0.7, 0.5, ear_z)
        glScalef(0.15, 0.3, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()
    
    # Glowing eyes (merah menyala) dengan alpha
    glDisable(GL_LIGHTING)
    glColor4f(1.0, 0.2, 0.0, wolf_alpha)
    for eye_z in (-0.12, 0.12):
        glPushMatrix()
        glTranslatef(0.95, 0.25, eye_z)
        glutSolidSphere(0.08, 10, 10)
        glPopMatrix()
    glEnable(GL_LIGHTING)
    
    # Legs dengan animasi berjalan dengan alpha
    glColor4f(0.12, 0.12, 0.15, wolf_alpha)
    leg_positions = [(-0.3, 0.2), (-0.3, -0.2), (0.3, 0.2), (0.3, -0.2)]
    for i, (leg_x, leg_z) in enumerate(leg_positions):
        # Animasi kaki: kaki depan dan belakang bergantian
        leg_swing = 0.0
        if i < 2:  # Kaki belakang
            leg_swing = np.sin(wolfWalkPhase * 4.0) * 0.08
        else:  # Kaki depan
            leg_swing = np.sin(wolfWalkPhase * 4.0 + np.pi) * 0.08
        
        glPushMatrix()
        glTranslatef(leg_x, -0.35 + abs(leg_swing), leg_z)
        glScalef(0.15, 0.5 - abs(leg_swing), 0.15)
        glutSolidCube(1.0)
        glPopMatrix()
    
    # Tail dengan animasi dan alpha
    glColor4f(0.15, 0.15, 0.18, wolf_alpha)
    tail_swing = np.sin(wolfWalkPhase * 3.0) * 15
    glPushMatrix()
    glTranslatef(-0.7, 0.1, 0.0)
    glRotatef(-30 + tail_swing, 0, 0, 1)
    glScalef(0.5, 0.15, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()


def draw_celestial_body():
    glDisable(GL_LIGHTING)

    # Posisi matahari/bulan berdasarkan waktu
    # Jam 07:00 (currentTime=0): Matahari di timur (kiri)
    # Jam 10:00 (currentTime=1): Matahari hampir di atas (90 derajat)
    # Jam 19:00 (currentTime=2): Bulan di timur (kiri)
    # Jam 23:00 (currentTime=3): Bulan hampir di atas (90 derajat)
    
    if dayNightBlend < 0.55:
        # Matahari (siang)
        sun_t = 1.0 - smoothstep(dayNightBlend / 0.55)
        
        # Hitung posisi berdasarkan currentTime
        if currentTime == 0:
            # Jam 07:00 - Matahari di timur (kiri, rendah)
            sun_x = -8.0
            sun_y = 8.0
            sun_z = -10.0
        elif currentTime == 1:
            # Jam 10:00 - Matahari hampir di atas (tengah, tinggi)
            sun_x = 2.0
            sun_y = 14.0
            sun_z = -10.0
        else:
            # Transisi atau malam - posisi default
            sun_x = 9.0
            sun_y = 13.2
            sun_z = -10.0
        
        glColor3f(1.0, 0.88, 0.28)
        glPushMatrix()
        glTranslatef(sun_x, sun_y, sun_z)
        glutSolidSphere(0.95 + sun_t * 0.08, 20, 20)
        glPopMatrix()

        # Sinar matahari
        glColor3f(1.0, 0.78, 0.2)
        for angle in range(0, 360, 45):
            glPushMatrix()
            glTranslatef(sun_x, sun_y, sun_z)
            glRotatef(float(angle), 0.0, 0.0, 1.0)
            glTranslatef(0.0, 1.35, 0.0)
            glScalef(0.12, 0.5, 0.12)
            glutSolidCube(1.0)
            glPopMatrix()

    if dayNightBlend > 0.2:
        # Bulan (malam)
        moon_t = smoothstep((dayNightBlend - 0.2) / 0.8)
        
        # Hitung posisi berdasarkan currentTime
        if currentTime == 2:
            # Jam 19:00 - Bulan di timur (kiri, rendah)
            moon_x = -8.5
            moon_y = 8.5
            moon_z = -9.5
        elif currentTime == 3:
            # Jam 23:00 - Bulan hampir di atas (tengah, tinggi)
            moon_x = 0.0
            moon_y = 14.0
            moon_z = -9.5
        else:
            # Transisi atau siang - posisi default
            moon_x = -9.5
            moon_y = 12.2
            moon_z = -9.5
        
        glColor3f(0.92, 0.93, 1.0)
        glPushMatrix()
        glTranslatef(moon_x, moon_y, moon_z)
        glutSolidSphere(0.8 + moon_t * 0.05, 20, 20)
        
        # Kawah bulan
        glColor3f(0.76, 0.8, 0.92)
        glPushMatrix()
        glTranslatef(-0.18, 0.16, 0.54)
        glutSolidSphere(0.18, 12, 12)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.2, -0.12, 0.48)
        glutSolidSphere(0.12, 10, 10)
        glPopMatrix()
        glPopMatrix()

    glEnable(GL_LIGHTING)


def draw_gable_roof(width, height, depth):
    hw = width / 2.0
    hd = depth / 2.0

    glBegin(GL_QUADS)
    glNormal3f(-0.7, 0.7, 0.0)
    glVertex3f(-hw, 0.0, -hd)
    glVertex3f(0.0, height, -hd)
    glVertex3f(0.0, height, hd)
    glVertex3f(-hw, 0.0, hd)

    glNormal3f(0.7, 0.7, 0.0)
    glVertex3f(0.0, height, -hd)
    glVertex3f(hw, 0.0, -hd)
    glVertex3f(hw, 0.0, hd)
    glVertex3f(0.0, height, hd)
    glEnd()

    glBegin(GL_TRIANGLES)
    glNormal3f(0.0, 0.45, 1.0)
    glVertex3f(-hw, 0.0, hd)
    glVertex3f(hw, 0.0, hd)
    glVertex3f(0.0, height, hd)

    glNormal3f(0.0, 0.45, -1.0)
    glVertex3f(hw, 0.0, -hd)
    glVertex3f(-hw, 0.0, -hd)
    glVertex3f(0.0, height, -hd)
    glEnd()


def draw_shed_roof(width, front_height, back_height, depth):
    hw = width / 2.0
    hd = depth / 2.0

    glBegin(GL_QUADS)
    glNormal3f(0.18, 0.98, 0.0)
    glVertex3f(-hw, front_height, -hd)
    glVertex3f(hw, back_height, -hd)
    glVertex3f(hw, back_height, hd)
    glVertex3f(-hw, front_height, hd)

    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-hw, 0.0, hd)
    glVertex3f(hw, 0.0, hd)
    glVertex3f(hw, back_height, hd)
    glVertex3f(-hw, front_height, hd)

    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(hw, 0.0, -hd)
    glVertex3f(-hw, 0.0, -hd)
    glVertex3f(-hw, front_height, -hd)
    glVertex3f(hw, back_height, -hd)

    # Close the underside so the inside of the barn is not visible from outside.
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-hw, 0.0, -hd)
    glVertex3f(hw, 0.0, -hd)
    glVertex3f(hw, 0.0, hd)
    glVertex3f(-hw, 0.0, hd)
    glEnd()

    glBegin(GL_TRIANGLES)
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-hw, 0.0, -hd)
    glVertex3f(-hw, front_height, -hd)
    glVertex3f(-hw, 0.0, hd)
    glVertex3f(-hw, 0.0, hd)
    glVertex3f(-hw, front_height, -hd)
    glVertex3f(-hw, front_height, hd)

    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(hw, 0.0, hd)
    glVertex3f(hw, back_height, -hd)
    glVertex3f(hw, 0.0, -hd)
    glVertex3f(hw, 0.0, hd)
    glVertex3f(hw, back_height, hd)
    glVertex3f(hw, back_height, -hd)
    glEnd()


def draw_cylinder(bottom_radius, top_radius, height, slices=24, stacks=8):
    quad = gluNewQuadric()
    glPushMatrix()
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    gluCylinder(quad, bottom_radius, top_radius, height, slices, stacks)
    glPopMatrix()
    gluDeleteQuadric(quad)


def draw_blade():
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, BLADE_VERTICES)
    glDrawElements(GL_QUADS, len(BLADE_INDICES), GL_UNSIGNED_INT, BLADE_INDICES)
    glDisableClientState(GL_VERTEX_ARRAY)


def draw_ground_patch():
    # Perluas tanah ke kiri untuk area serigala
    left = -16.5  # Diperluas dari -13.8 ke -16.5 (tambah 2.7 unit)
    right = 13.8
    front = 11.2
    back = -11.2
    top_y = -0.03
    bottom_y = -2.35

    glColor3f(0.36, 0.68, 0.25)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(left, top_y, front)
    glVertex3f(right, top_y, front)
    glVertex3f(right, top_y, back)
    glVertex3f(left, top_y, back)
    glEnd()

    sediment_layers = [
        (top_y, -0.38, (0.59, 0.45, 0.25), 0.00),
        (-0.38, -0.92, (0.52, 0.39, 0.21), 0.12),
        (-0.92, -1.55, (0.45, 0.33, 0.18), 0.24),
        (-1.55, bottom_y, (0.37, 0.27, 0.15), 0.36),
    ]

    for y_top, y_bottom, color, spread in sediment_layers:
        # Perluas layer tanah ke kiri juga
        layer_left = left - spread
        layer_right = right + spread
        layer_front = front + spread
        layer_back = back - spread

        glColor3f(*color)
        glBegin(GL_QUADS)

        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(layer_left, y_top, layer_front)
        glVertex3f(layer_right, y_top, layer_front)
        glVertex3f(layer_right, y_bottom, layer_front)
        glVertex3f(layer_left, y_bottom, layer_front)

        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(layer_right, y_top, layer_back)
        glVertex3f(layer_left, y_top, layer_back)
        glVertex3f(layer_left, y_bottom, layer_back)
        glVertex3f(layer_right, y_bottom, layer_back)

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(layer_left, y_top, layer_back)
        glVertex3f(layer_left, y_top, layer_front)
        glVertex3f(layer_left, y_bottom, layer_front)
        glVertex3f(layer_left, y_bottom, layer_back)

        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(layer_right, y_top, layer_front)
        glVertex3f(layer_right, y_top, layer_back)
        glVertex3f(layer_right, y_bottom, layer_back)
        glVertex3f(layer_right, y_bottom, layer_front)

        glEnd()

    glColor3f(0.29, 0.2, 0.12)
    glBegin(GL_QUADS)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(left - 0.36, bottom_y, back - 0.36)
    glVertex3f(right + 0.36, bottom_y, back - 0.36)
    glVertex3f(right + 0.36, bottom_y, front + 0.36)
    glVertex3f(left - 0.36, bottom_y, front + 0.36)
    glEnd()


def draw_fence_post(x, z, height=0.95):
    glPushMatrix()
    glTranslatef(x, height / 2.0, z)
    glScalef(0.2, height, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_fence_segment(x1, z1, x2, z2, spacing=2.25, post_height=0.95):
    glColor3f(0.64, 0.45, 0.22)

    dx = x2 - x1
    dz = z2 - z1
    length = float(np.hypot(dx, dz))
    if length <= 0.01:
        return

    count = max(1, int(round(length / spacing)))

    for i in range(count + 1):
        t = i / count
        draw_fence_post(x1 + dx * t, z1 + dz * t, post_height)

    angle = np.degrees(np.arctan2(dx, dz))
    for rail_y in (0.33, 0.56):
        glPushMatrix()
        glTranslatef((x1 + x2) / 2.0, rail_y, (z1 + z2) / 2.0)
        glRotatef(angle, 0.0, 1.0, 0.0)
        glScalef(0.1, 0.08, length)
        glutSolidCube(1.0)
        glPopMatrix()


def draw_gate(center_x, z_pos, width):
    glColor3f(0.64, 0.45, 0.22)
    half_width = width / 2.0
    left_post_x = center_x - half_width
    right_post_x = center_x + half_width
    draw_fence_post(left_post_x, z_pos, 1.02)
    draw_fence_post(right_post_x, z_pos, 1.02)
    leaf_width = width * 0.46
    for hinge_x, angle, direction in (
        (left_post_x + 0.02, -34.0, 1.0),
        (right_post_x - 0.02, 34.0, -1.0),
    ):
        for rail_y in (0.33, 0.56):
            glPushMatrix()
            glTranslatef(hinge_x, rail_y, z_pos)
            glRotatef(angle, 0.0, 1.0, 0.0)
            glTranslatef(direction * leaf_width / 2.0, 0.0, 0.0)
            glScalef(leaf_width, 0.07, 0.09)
            glutSolidCube(1.0)
            glPopMatrix()


def draw_hay_bale(x, z, scale=1.0, rot_y=0.0):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glRotatef(rot_y, 0.0, 1.0, 0.0)

    glPushMatrix()
    glTranslatef(0.0, 0.28 * scale, 0.0)
    glColor3f(0.83, 0.75, 0.42)
    glScalef(1.1 * scale, 0.55 * scale, 0.75 * scale)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.71, 0.6, 0.28)
    for offset in (-0.18, 0.0, 0.18):
        glPushMatrix()
        glTranslatef(0.0, 0.28 * scale, offset * scale)
        glScalef(1.02 * scale, 0.05 * scale, 0.04 * scale)
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()


def draw_trough(x, z, scale=1.0, rot_y=0.0):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glRotatef(rot_y, 0.0, 1.0, 0.0)

    glPushMatrix()
    glTranslatef(0.0, 0.16 * scale, 0.0)
    glColor3f(0.36, 0.39, 0.44)
    glScalef(1.25 * scale, 0.22 * scale, 0.55 * scale)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, 0.24 * scale, 0.0)
    glColor3f(0.53, 0.82, 0.9)
    glScalef(1.02 * scale, 0.05 * scale, 0.36 * scale)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.29, 0.26, 0.24)
    for leg_x, leg_z in ((-0.48, -0.18), (-0.48, 0.18), (0.48, -0.18), (0.48, 0.18)):
        glPushMatrix()
        glTranslatef(leg_x * scale, 0.08 * scale, leg_z * scale)
        glScalef(0.12 * scale, 0.16 * scale, 0.12 * scale)
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()


def draw_box_stack(x, z, layers=2, scale=1.0):
    box_color = (0.67, 0.48, 0.28)
    edge_color = (0.54, 0.37, 0.2)

    for layer in range(layers):
        y = 0.18 * scale + layer * 0.34 * scale
        count = 2 if layer == 0 else 1
        for i in range(count):
            offset_x = (i - (count - 1) / 2.0) * 0.5 * scale
            glColor3f(*box_color)
            glPushMatrix()
            glTranslatef(x + offset_x, y, z)
            glScalef(0.46 * scale, 0.32 * scale, 0.42 * scale)
            glutSolidCube(1.0)
            glPopMatrix()

            glColor3f(*edge_color)
            glPushMatrix()
            glTranslatef(x + offset_x, y + 0.02 * scale, z)
            glScalef(0.5 * scale, 0.03 * scale, 0.03 * scale)
            glutSolidCube(1.0)
            glPopMatrix()


def draw_farm_plot():
    draw_ground_patch()

    glPushMatrix()
    glTranslatef(0.0, 0.02, 0.0)
    glColor3f(0.42, 0.76, 0.28)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-11.5, 0.0, 9.0)
    glVertex3f(11.5, 0.0, 9.0)
    glVertex3f(11.5, 0.0, -9.0)
    glVertex3f(-11.5, 0.0, -9.0)
    glEnd()
    glPopMatrix()

    glColor3f(0.64, 0.52, 0.33)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(1.5, 0.03, 8.8)
    glVertex3f(4.1, 0.03, 8.8)
    glVertex3f(4.1, 0.03, -2.5)
    glVertex3f(1.5, 0.03, -2.5)
    glEnd()

    glColor3f(0.8, 0.74, 0.58)
    for x in (-9.5, -6.0, 6.5, 9.0):
        glPushMatrix()
        glTranslatef(x, 0.05, -6.8)
        glScalef(1.6, 0.12, 1.6)
        glutSolidCube(1.0)
        glPopMatrix()

    draw_fence_segment(-11.0, 8.5, 0.9, 8.5)
    draw_fence_segment(4.9, 8.5, 11.0, 8.5)
    draw_gate(2.85, 8.5, 2.9)
    draw_fence_segment(-11.0, -8.5, 11.0, -8.5)
    draw_fence_segment(-11.0, -8.5, -11.0, 8.5)
    draw_fence_segment(11.0, -8.5, 11.0, 8.5)

    # Pagar pendek di belakang barn supaya area belakang terasa lebih rapi dan bertingkat.
    draw_fence_segment(1.4, -5.2, 10.4, -5.2)

    draw_hay_bale(-8.8, -6.9, 1.05, 8.0)
    draw_hay_bale(-6.0, -6.9, 0.92, -10.0)
    draw_hay_bale(8.4, 6.1, 0.9, 12.0)
    draw_trough(-10.0, 1.6, 0.95, 90.0)
    draw_trough(9.5, 0.8, 0.9, -90.0)
    draw_hay_bale(7.8, -6.4, 0.95, 0.0)
    draw_hay_bale(9.0, -6.1, 0.88, 10.0)
    draw_box_stack(5.6, -6.3, 2, 1.0)
    draw_box_stack(6.9, -6.0, 2, 0.9)
    
    # Tambahkan rumput lebat di berbagai lokasi
    draw_grass_patch(-8.8, -6.9, 25, 1.8)  # Di sekitar hay bale
    draw_grass_patch(-6.0, -6.9, 20, 1.5)
    draw_grass_patch(8.4, 6.1, 22, 1.6)
    draw_grass_patch(-10.5, 1.6, 18, 1.3)  # Dekat trough
    draw_grass_patch(10.0, 0.8, 18, 1.3)
    draw_grass_patch(-4.0, 4.0, 20, 1.4)   # Area kosong
    draw_grass_patch(0.0, 5.5, 25, 2.0)
    draw_grass_patch(-7.0, 2.0, 20, 1.5)
    draw_grass_patch(4.0, 4.5, 18, 1.4)
    
    # Rumput di area serigala (kiri luar pagar)
    draw_grass_patch(-14.0, 2.0, 22, 1.6)  # Area patrol serigala
    draw_grass_patch(-13.5, 4.5, 18, 1.4)
    draw_grass_patch(-14.5, -0.5, 20, 1.5)
    
    # Tambahkan pohon untuk tampilan realistik
    # Pohon di pojok kiri belakang (dekat area serigala)
    draw_tree(-14.5, -8.0, 3.2, 0.22, 1.0)
    draw_pine_tree(-15.2, -5.5, 3.8, 0.9)
    
    # Pohon di pojok kiri depan
    draw_tree(-12.5, 7.5, 3.5, 0.25, 1.1)
    draw_tree(-14.0, 9.0, 3.0, 0.2, 0.95)
    
    # Pohon di pojok kanan belakang
    draw_pine_tree(12.0, -8.5, 4.0, 1.0)
    draw_tree(13.5, -6.5, 3.3, 0.23, 1.05)
    
    # Pohon di pojok kanan depan
    draw_tree(11.5, 8.0, 3.4, 0.24, 1.08)
    draw_pine_tree(13.0, 9.5, 3.6, 0.85)
    
    # Pohon tambahan di belakang barn untuk depth
    draw_tree(8.0, -8.0, 2.8, 0.18, 0.9)
    draw_tree(9.5, -7.5, 3.0, 0.2, 0.95)


def draw_barn_slats(center_x, center_y, width, height, z_pos, count, color):
    glColor3f(*color)
    start_y = center_y - height / 2.0 + 0.22
    for i in range(count):
        glPushMatrix()
        glTranslatef(center_x, start_y + i * (height / count), z_pos)
        glScalef(width * 0.96, 0.05, 0.08)
        glutSolidCube(1.0)
        glPopMatrix()


def draw_double_barn_door(center_x, center_y, z_pos):
    trim_color = (0.98, 0.94, 0.82)
    panel_color = (0.88, 0.28, 0.27)

    glColor3f(*trim_color)
    glPushMatrix()
    glTranslatef(center_x, center_y, z_pos)
    glScalef(2.7, 2.6, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    for panel_offset in (-0.67, 0.67):
        glColor3f(*panel_color)
        glPushMatrix()
        glTranslatef(center_x + panel_offset, center_y, z_pos + 0.01)
        glScalef(1.18, 2.34, 0.06)
        glutSolidCube(1.0)
        glPopMatrix()

        glColor3f(*trim_color)
        glPushMatrix()
        glTranslatef(center_x + panel_offset, center_y, z_pos + 0.03)
        glScalef(0.12, 2.2, 0.07)
        glutSolidCube(1.0)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(center_x + panel_offset, center_y, z_pos + 0.03)
        glScalef(1.0, 0.12, 0.07)
        glutSolidCube(1.0)
        glPopMatrix()

        for angle in (55.0, -55.0):
            glPushMatrix()
            glTranslatef(center_x + panel_offset, center_y, z_pos + 0.04)
            glRotatef(angle, 0.0, 0.0, 1.0)
            glScalef(1.45, 0.1, 0.07)
            glutSolidCube(1.0)
            glPopMatrix()

    glPushMatrix()
    glTranslatef(center_x, center_y, z_pos + 0.04)
    glScalef(0.12, 2.36, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_triangle_panel(center_x, center_y, z_pos, width, height, outer_color, inner_color):
    half_w = width / 2.0

    glColor3f(*outer_color)
    glBegin(GL_TRIANGLES)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(center_x - half_w, center_y - height / 2.0, z_pos)
    glVertex3f(center_x + half_w, center_y - height / 2.0, z_pos)
    glVertex3f(center_x, center_y + height / 2.0, z_pos)
    glEnd()

    glColor3f(*inner_color)
    glBegin(GL_TRIANGLES)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(center_x - half_w * 0.68, center_y - height * 0.26, z_pos + 0.01)
    glVertex3f(center_x + half_w * 0.68, center_y - height * 0.26, z_pos + 0.01)
    glVertex3f(center_x, center_y + height * 0.22, z_pos + 0.01)
    glEnd()


def draw_barn_window(center_x, center_y, z_pos):
    frame_color = (0.98, 0.9, 0.82)
    glass_color = mix_color((0.42, 0.18, 0.17), (1.0, 0.88, 0.52), dayNightBlend)

    glColor3f(*frame_color)
    glPushMatrix()
    glTranslatef(center_x, center_y, z_pos)
    glScalef(1.34, 0.92, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(*glass_color)
    glPushMatrix()
    glTranslatef(center_x, center_y, z_pos + 0.02)
    glScalef(0.9, 0.54, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()

    if dayNightBlend > 0.05:
        glow_color = mix_color((0.55, 0.2, 0.15), (1.0, 0.94, 0.72), dayNightBlend)
        glDisable(GL_LIGHTING)
        glColor3f(*glow_color)
        glPushMatrix()
        glTranslatef(center_x, center_y, z_pos + 0.065)
        glScalef(0.98, 0.62, 0.02)
        glutSolidCube(1.0)
        glPopMatrix()
        glEnable(GL_LIGHTING)


def draw_barn():
    glPushMatrix()
    glTranslatef(5.2, 0.0, -1.6)

    base_red = (0.82, 0.2, 0.23)
    trim = (0.98, 0.94, 0.82)
    roof_main = (0.92, 0.72, 0.68)
    roof_edge = (0.81, 0.52, 0.34)
    sill = (0.44, 0.25, 0.2)
    slat_color = (0.9, 0.36, 0.33)

    glColor3f(*sill)
    glPushMatrix()
    glTranslatef(0.8, 0.05, 0.0)
    glScalef(9.3, 0.1, 4.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(*base_red)
    glPushMatrix()
    glTranslatef(-2.0, 1.7, 0.0)
    glScalef(3.6, 3.4, 3.3)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(2.15, 1.5, 0.0)
    glScalef(5.9, 3.02, 3.3)
    glutSolidCube(1.0)
    glPopMatrix()

    draw_barn_slats(-2.0, 1.7, 3.46, 3.18, 1.69, 11, slat_color)
    draw_barn_slats(2.15, 1.5, 5.76, 2.78, 1.69, 10, slat_color)

    glColor3f(base_red[0] * 0.92, base_red[1] * 0.92, base_red[2] * 0.92)
    glPushMatrix()
    glTranslatef(5.1, 1.5, 0.0)
    glScalef(0.14, 3.0, 3.3)
    glutSolidCube(1.0)
    glPopMatrix()

    # Front gable facade, flush with the front wall instead of a separate roof block.
    glColor3f(base_red[0] * 0.9, base_red[1] * 0.9, base_red[2] * 0.9)
    glBegin(GL_TRIANGLES)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-3.8, 3.4, 1.66)
    glVertex3f(-0.2, 3.4, 1.66)
    glVertex3f(-2.0, 4.72, 1.66)
    glEnd()

    glColor3f(*roof_main)
    glPushMatrix()
    glTranslatef(0.76, 2.84, -0.32)
    draw_shed_roof(10.0, 2.02, 1.34, 4.95)
    glPopMatrix()

    # Front fascia that visually joins the decorative gable and the main roof.
    glColor3f(*roof_edge)
    glPushMatrix()
    glTranslatef(0.76, 3.0, 2.28)
    glScalef(10.05, 0.12, 0.16)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.76, 3.0, -2.56)
    glScalef(10.05, 0.12, 0.16)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-4.08, 3.0, -0.18)
    glScalef(0.16, 0.12, 4.92)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(5.72, 3.0, -0.18)
    glScalef(0.16, 0.12, 4.92)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(*trim)
    for post_x, post_y, post_h in (
        (-3.78, 1.7, 3.4), (-0.22, 1.7, 3.4), (-0.74, 1.5, 3.0), (5.02, 1.5, 3.0)
    ):
        glPushMatrix()
        glTranslatef(post_x, post_y, 1.76)
        glScalef(0.18, post_h, 0.14)
        glutSolidCube(1.0)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(0.62, 0.1, 1.76)
    glScalef(8.88, 0.1, 0.12)
    glutSolidCube(1.0)
    glPopMatrix()

    draw_double_barn_door(-2.0, 1.42, 1.77)
    draw_triangle_panel(-2.0, 3.16, 1.78, 1.28, 0.9, trim, (0.47, 0.25, 0.25))
    draw_barn_window(0.95, 1.58, 1.77)
    draw_barn_window(3.18, 1.58, 1.77)

    glColor3f(*trim)
    glPushMatrix()
    glTranslatef(-2.0, 4.1, 0.0)
    glScalef(0.18, 0.16, 3.42)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()


def draw_goat_body():
    # Warna domba sederhana
    wool = (0.95, 0.95, 0.95)  # Putih untuk badan
    face = (0.2, 0.2, 0.2)  # Abu-abu gelap untuk wajah dan kaki

    # Body utama (badan oval)
    glColor3f(*wool)
    glPushMatrix()
    glScalef(1.0, 0.8, 0.7)
    glutSolidSphere(0.5, 16, 16)
    glPopMatrix()

    # Head (kepala abu-abu)
    glColor3f(*face)
    glPushMatrix()
    glTranslatef(0.5, 0.1, 0.0)
    glutSolidSphere(0.25, 16, 16)
    glPopMatrix()

    # Ears (telinga)
    for ear_z in (-0.15, 0.15):
        glPushMatrix()
        glTranslatef(0.5, 0.25, ear_z)
        glScalef(0.1, 0.2, 0.05)
        glutSolidSphere(0.5, 12, 12)
        glPopMatrix()

    # Eyes (mata hitam)
    glColor3f(0.0, 0.0, 0.0)
    for eye_z in (-0.1, 0.1):
        glPushMatrix()
        glTranslatef(0.65, 0.15, eye_z)
        glutSolidSphere(0.04, 8, 8)
        glPopMatrix()

    # Legs (kaki abu-abu)
    glColor3f(*face)
    leg_positions = [(-0.2, 0.15), (-0.2, -0.15), (0.15, 0.15), (0.15, -0.15)]
    for leg_x, leg_z in leg_positions:
        glPushMatrix()
        glTranslatef(leg_x, -0.4, leg_z)
        glScalef(0.1, 0.4, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()

    # Tail (ekor putih pendek)
    glColor3f(*wool)
    glPushMatrix()
    glTranslatef(-0.5, 0.0, 0.0)
    glScalef(0.08, 0.15, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()


def get_roaming_sheep_state(config):
    base_x = config["base_x"]
    base_z = config["base_z"]
    radius_x = config["radius_x"]
    radius_z = config["radius_z"]
    phase = config["phase"]

    orbit_x = np.cos(goatWalkPhase + phase) * radius_x
    orbit_z = np.sin(goatWalkPhase * 0.85 + phase) * radius_z
    heading_x = -np.sin(goatWalkPhase + phase) * radius_x
    heading_z = np.cos(goatWalkPhase * 0.85 + phase) * radius_z * 0.85
    heading = -np.degrees(np.arctan2(heading_z, heading_x))
    body_bob = 0.05 * abs(np.sin(goatWalkPhase * 3.0 + phase))
    return base_x + orbit_x, base_z + orbit_z, heading, body_bob


def draw_goat(config):
    roam_x, roam_z, roam_heading, body_bob = get_roaming_sheep_state(config)
    
    scale_factor = config["scale"]
    
    # Posisi hay bale untuk jam makan
    hay_idx = config["index"] % 3
    hay_target_x = HAY_BALE_POSITIONS[hay_idx]["x"]
    hay_target_z = HAY_BALE_POSITIONS[hay_idx]["z"]
    angle_offset = config["index"] * 120
    hay_target_x += np.cos(np.radians(angle_offset)) * 1.2
    hay_target_z += np.sin(np.radians(angle_offset)) * 1.2
    
    # Posisi barn untuk malam
    spot = SHEEP_BARN_SPOTS[config["index"]]
    
    # Deteksi transisi berdasarkan previousTime dan currentTime
    is_transitioning = (previousTime != currentTime)
    
    # Default values
    x_pos = roam_x
    z_pos = roam_z
    y_pos = 0.62 + body_bob
    heading = roam_heading
    
    # ===== LOGIKA POSISI BERDASARKAN WAKTU DAN TRANSISI =====
    
    if currentTime == 0:  # Jam 07:00 - Pagi (Roaming)
        if is_transitioning and previousTime >= 2:
            # Transisi dari malam (19:00 atau 23:00) ke pagi - keluar dari barn
            exit_progress = 1.0 - (dayNightBlend / TIME_CONFIGS[previousTime]["sky_blend"])
            exit_progress = clamp(exit_progress, 0.0, 1.0)
            
            if exit_progress < 0.4:
                # Fase 1: Keluar dari dalam ke pintu
                inside_to_door = exit_progress / 0.4
                x_pos = lerp(spot["inside_x"], spot["door_x"], inside_to_door)
                z_pos = lerp(spot["inside_z"], spot["door_z"], inside_to_door)
                scale_factor = config["scale"] * max(inside_to_door, 0.1)
            else:
                # Fase 2: Dari pintu ke roaming
                door_to_roam = (exit_progress - 0.4) / 0.6
                x_pos = lerp(spot["door_x"], roam_x, door_to_roam)
                z_pos = lerp(spot["door_z"], roam_z, door_to_roam)
                scale_factor = config["scale"]
            
            y_pos = 0.62
            # Heading ke arah keluar
            path_dx = roam_x - spot["inside_x"]
            path_dz = roam_z - spot["inside_z"]
            heading = -np.degrees(np.arctan2(path_dz, path_dx))
            
        elif is_transitioning and previousTime == 1:
            # Transisi dari jam makan (10:00) ke pagi - dari hay bale ke roaming
            transition_progress = 1.0 - (abs(dayNightBlend - TIME_CONFIGS[0]["sky_blend"]) / abs(TIME_CONFIGS[1]["sky_blend"] - TIME_CONFIGS[0]["sky_blend"]))
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            x_pos = lerp(hay_target_x, roam_x, transition_progress)
            z_pos = lerp(hay_target_z, roam_z, transition_progress)
            y_pos = lerp(0.55, 0.62 + body_bob, transition_progress)
            
            # Heading ke arah roaming
            path_dx = roam_x - hay_target_x
            path_dz = roam_z - hay_target_z
            heading = -np.degrees(np.arctan2(path_dz, path_dx))
        else:
            # Normal roaming
            x_pos = roam_x
            z_pos = roam_z
            y_pos = 0.62 + body_bob
            heading = roam_heading
    
    elif currentTime == 1:  # Jam 10:00 - Jam Makan (Hay Bale)
        if is_transitioning and previousTime == 0:
            # Transisi dari pagi ke jam makan - roaming ke hay bale
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[0]["sky_blend"]) / abs(TIME_CONFIGS[1]["sky_blend"] - TIME_CONFIGS[0]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            x_pos = lerp(roam_x, hay_target_x, transition_progress)
            z_pos = lerp(roam_z, hay_target_z, transition_progress)
            y_pos = lerp(0.62 + body_bob, 0.55, transition_progress)
            
            # Heading ke hay bale
            path_dx = hay_target_x - roam_x
            path_dz = hay_target_z - roam_z
            heading = -np.degrees(np.arctan2(path_dz, path_dx))
            
        elif is_transitioning and previousTime >= 2:
            # Transisi dari malam (19:00 atau 23:00) ke jam makan - barn ke hay bale
            transition_progress = 1.0 - (dayNightBlend / TIME_CONFIGS[previousTime]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            if transition_progress < 0.4:
                # Fase 1: Keluar dari barn ke pintu
                inside_to_door = transition_progress / 0.4
                x_pos = lerp(spot["inside_x"], spot["door_x"], inside_to_door)
                z_pos = lerp(spot["inside_z"], spot["door_z"], inside_to_door)
                scale_factor = config["scale"] * max(inside_to_door, 0.1)
            else:
                # Fase 2: Dari pintu ke hay bale
                door_to_hay = (transition_progress - 0.4) / 0.6
                x_pos = lerp(spot["door_x"], hay_target_x, door_to_hay)
                z_pos = lerp(spot["door_z"], hay_target_z, door_to_hay)
                scale_factor = config["scale"]
            
            y_pos = lerp(0.62, 0.55, transition_progress)
            
            # Heading ke hay bale
            path_dx = hay_target_x - spot["inside_x"]
            path_dz = hay_target_z - spot["inside_z"]
            heading = -np.degrees(np.arctan2(path_dz, path_dx))
        else:
            # Normal makan di hay bale
            x_pos = hay_target_x
            z_pos = hay_target_z
            y_pos = 0.55
            
            # Heading ke hay bale center
            path_dx = HAY_BALE_POSITIONS[hay_idx]["x"] - x_pos
            path_dz = HAY_BALE_POSITIONS[hay_idx]["z"] - z_pos
            heading = -np.degrees(np.arctan2(path_dz, path_dx))
    
    elif currentTime >= 2:  # Jam 19:00 atau 23:00 - Malam (Barn)
        if is_transitioning and previousTime == 0:
            # Transisi dari pagi ke malam - roaming ke barn
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[0]["sky_blend"]) / abs(TIME_CONFIGS[currentTime]["sky_blend"] - TIME_CONFIGS[0]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            if transition_progress < 0.6:
                # Fase 1: Roaming ke pintu
                walk_progress = transition_progress / 0.6
                x_pos = lerp(roam_x, spot["door_x"], walk_progress)
                z_pos = lerp(roam_z, spot["door_z"], walk_progress)
                scale_factor = config["scale"]
            else:
                # Fase 2: Pintu ke dalam barn
                hide_progress = (transition_progress - 0.6) / 0.4
                x_pos = lerp(spot["door_x"], spot["inside_x"], hide_progress)
                z_pos = lerp(spot["door_z"], spot["inside_z"], hide_progress)
                scale_factor = config["scale"] * (1.0 - hide_progress)
            
            y_pos = 0.62
            
            # Heading ke barn
            path_dx = spot["inside_x"] - roam_x
            path_dz = spot["inside_z"] - roam_z
            heading = -np.degrees(np.arctan2(path_dz, path_dx))
            
            # Jika sudah masuk sepenuhnya, jangan render
            if transition_progress >= 0.98:
                return
                
        elif is_transitioning and previousTime == 1:
            # Transisi dari jam makan ke malam - hay bale ke barn
            transition_progress = abs(dayNightBlend - TIME_CONFIGS[1]["sky_blend"]) / abs(TIME_CONFIGS[currentTime]["sky_blend"] - TIME_CONFIGS[1]["sky_blend"])
            transition_progress = clamp(transition_progress, 0.0, 1.0)
            
            if transition_progress < 0.6:
                # Fase 1: Hay bale ke pintu
                walk_progress = transition_progress / 0.6
                x_pos = lerp(hay_target_x, spot["door_x"], walk_progress)
                z_pos = lerp(hay_target_z, spot["door_z"], walk_progress)
                scale_factor = config["scale"]
            else:
                # Fase 2: Pintu ke dalam barn
                hide_progress = (transition_progress - 0.6) / 0.4
                x_pos = lerp(spot["door_x"], spot["inside_x"], hide_progress)
                z_pos = lerp(spot["door_z"], spot["inside_z"], hide_progress)
                scale_factor = config["scale"] * (1.0 - hide_progress)
            
            y_pos = lerp(0.55, 0.62, transition_progress)
            
            # Heading ke barn
            path_dx = spot["inside_x"] - hay_target_x
            path_dz = spot["inside_z"] - hay_target_z
            heading = -np.degrees(np.arctan2(path_dz, path_dx))
            
            # Jika sudah masuk sepenuhnya, jangan render
            if transition_progress >= 0.98:
                return
                
        elif is_transitioning and ((previousTime == 2 and currentTime == 3) or (previousTime == 3 and currentTime == 2)):
            # Transisi antara jam 19:00 dan 23:00 - tetap di barn (tidak perlu animasi)
            # Domba sudah di dalam, tidak perlu render
            return
        else:
            # Normal di dalam barn - tidak render
            return
    
    # Render domba
    glPushMatrix()
    glTranslatef(x_pos, y_pos, z_pos)
    glRotatef(heading, 0.0, 1.0, 0.0)
    glScalef(scale_factor, scale_factor, scale_factor)
    draw_goat_body()
    glPopMatrix()


def draw_windmill():
    glPushMatrix()
    glTranslatef(-3.2, 0.0, -0.4)

    glColor3f(0.9, 0.9, 0.92)
    draw_cylinder(0.4, 0.15, 6.0, 32, 24)

    glPushMatrix()
    glTranslatef(0.0, 5.8, 0.0)
    glColor3f(0.95, 0.95, 0.95)
    glPushMatrix()
    glTranslatef(0.0, 0.0, -0.6)
    quad = gluNewQuadric()
    gluCylinder(quad, 0.25, 0.2, 1.2, 32, 16)
    glutSolidSphere(0.25, 32, 16)
    gluDeleteQuadric(quad)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.3)
    glRotatef(angleBlade, 0.0, 0.0, 1.0)

    glColor3f(0.8, 0.8, 0.8)
    glutSolidSphere(0.3, 16, 16)

    glColor3f(0.95, 0.95, 0.95)
    for i in range(3):
        glPushMatrix()
        glRotatef(120.0 * i, 0.0, 0.0, 1.0)
        draw_blade()
        glPopMatrix()

    glPopMatrix()
    glPopMatrix()
    glPopMatrix()


def draw_cloud(x, y, z, scale=1.0, density=5):
    """Menggambar awan dengan beberapa sphere"""
    glDisable(GL_LIGHTING)
    
    # Warna awan berdasarkan waktu (putih di siang, abu-abu gelap di malam)
    cloud_brightness = 1.0 - (dayNightBlend * 0.6)
    glColor4f(cloud_brightness, cloud_brightness, cloud_brightness, 0.85)
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Awan terdiri dari beberapa sphere yang overlap
    # Sphere tengah (paling besar)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    glutSolidSphere(0.8 * scale, 12, 12)
    glPopMatrix()
    
    # Sphere kiri
    glPushMatrix()
    glTranslatef(-0.7 * scale, -0.1 * scale, 0.0)
    glutSolidSphere(0.6 * scale, 12, 12)
    glPopMatrix()
    
    # Sphere kanan
    glPushMatrix()
    glTranslatef(0.7 * scale, -0.1 * scale, 0.0)
    glutSolidSphere(0.65 * scale, 12, 12)
    glPopMatrix()
    
    # Sphere atas
    glPushMatrix()
    glTranslatef(0.0, 0.5 * scale, 0.0)
    glutSolidSphere(0.55 * scale, 12, 12)
    glPopMatrix()
    
    # Sphere kiri atas
    glPushMatrix()
    glTranslatef(-0.4 * scale, 0.3 * scale, 0.0)
    glutSolidSphere(0.5 * scale, 12, 12)
    glPopMatrix()
    
    # Sphere kanan atas
    glPushMatrix()
    glTranslatef(0.4 * scale, 0.3 * scale, 0.0)
    glutSolidSphere(0.5 * scale, 12, 12)
    glPopMatrix()
    
    glPopMatrix()
    glEnable(GL_LIGHTING)


def draw_clouds():
    """Menggambar beberapa awan yang bergerak melintas"""
    
    # Konfigurasi awan dengan posisi dan kecepatan berbeda
    clouds = [
        {"y": 12.0, "z": -15.0, "scale": 1.5, "speed": 1.0, "offset": 0.0},
        {"y": 14.0, "z": -18.0, "scale": 1.2, "speed": 0.7, "offset": 15.0},
        {"y": 11.5, "z": -12.0, "scale": 1.8, "speed": 0.9, "offset": 30.0},
        {"y": 13.5, "z": -20.0, "scale": 1.3, "speed": 0.8, "offset": 45.0},
        {"y": 15.0, "z": -16.0, "scale": 1.4, "speed": 1.1, "offset": 60.0},
    ]
    
    for cloud in clouds:
        # Hitung posisi X berdasarkan cloudPhase
        # Awan bergerak dari kiri ke kanan
        x_range = 50.0  # Total jarak pergerakan
        x_start = -25.0  # Posisi awal (kiri)
        
        # Posisi X dengan offset untuk setiap awan
        x_pos = x_start + ((cloudPhase * cloud["speed"] + cloud["offset"]) % x_range)
        
        draw_cloud(x_pos, cloud["y"], cloud["z"], cloud["scale"])


def draw_mountain_low_poly(x, z, base_width, height, style='peaked'):
    """Menggambar gunung low-poly dengan berbagai style"""
    
    # Warna gunung (coklat/abu-abu dengan variasi)
    rock_dark = (0.45, 0.38, 0.32)
    rock_mid = (0.52, 0.45, 0.38)
    rock_light = (0.58, 0.52, 0.45)
    snow_color = (0.95, 0.95, 0.98)
    grass_color = (0.55, 0.65, 0.35)
    
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    
    if style == 'peaked':
        # Gunung runcing dengan puncak salju
        # Base layer (gelap)
        glColor3f(*rock_dark)
        glBegin(GL_TRIANGLES)
        glNormal3f(0.0, 0.5, 0.8)
        glVertex3f(0.0, height, 0.0)  # Puncak
        glVertex3f(-base_width/2, 0.0, base_width/3)
        glVertex3f(base_width/2, 0.0, base_width/3)
        glEnd()
        
        # Side kiri
        glColor3f(*rock_mid)
        glBegin(GL_TRIANGLES)
        glNormal3f(-0.8, 0.5, 0.0)
        glVertex3f(0.0, height, 0.0)
        glVertex3f(-base_width/2, 0.0, -base_width/3)
        glVertex3f(-base_width/2, 0.0, base_width/3)
        glEnd()
        
        # Side kanan
        glColor3f(*rock_light)
        glBegin(GL_TRIANGLES)
        glNormal3f(0.8, 0.5, 0.0)
        glVertex3f(0.0, height, 0.0)
        glVertex3f(base_width/2, 0.0, base_width/3)
        glVertex3f(base_width/2, 0.0, -base_width/3)
        glEnd()
        
        # Back
        glColor3f(*rock_dark)
        glBegin(GL_TRIANGLES)
        glNormal3f(0.0, 0.5, -0.8)
        glVertex3f(0.0, height, 0.0)
        glVertex3f(base_width/2, 0.0, -base_width/3)
        glVertex3f(-base_width/2, 0.0, -base_width/3)
        glEnd()
        
        # Snow cap (puncak salju)
        snow_height = height * 0.3
        glColor3f(*snow_color)
        glBegin(GL_TRIANGLES)
        # Front snow
        glVertex3f(0.0, height, 0.0)
        glVertex3f(-base_width/6, height - snow_height, base_width/9)
        glVertex3f(base_width/6, height - snow_height, base_width/9)
        glEnd()
        
        glBegin(GL_TRIANGLES)
        # Left snow
        glVertex3f(0.0, height, 0.0)
        glVertex3f(-base_width/6, height - snow_height, -base_width/9)
        glVertex3f(-base_width/6, height - snow_height, base_width/9)
        glEnd()
        
        glBegin(GL_TRIANGLES)
        # Right snow
        glVertex3f(0.0, height, 0.0)
        glVertex3f(base_width/6, height - snow_height, base_width/9)
        glVertex3f(base_width/6, height - snow_height, -base_width/9)
        glEnd()
        
        glBegin(GL_TRIANGLES)
        # Back snow
        glVertex3f(0.0, height, 0.0)
        glVertex3f(base_width/6, height - snow_height, -base_width/9)
        glVertex3f(-base_width/6, height - snow_height, -base_width/9)
        glEnd()
        
    elif style == 'plateau':
        # Gunung dengan puncak datar (plateau)
        plateau_height = height * 0.85
        plateau_width = base_width * 0.4
        
        # Lower slopes
        glColor3f(*rock_dark)
        glBegin(GL_QUADS)
        # Front face
        glNormal3f(0.0, 0.5, 0.8)
        glVertex3f(-plateau_width/2, plateau_height, plateau_width/4)
        glVertex3f(plateau_width/2, plateau_height, plateau_width/4)
        glVertex3f(base_width/2, 0.0, base_width/3)
        glVertex3f(-base_width/2, 0.0, base_width/3)
        glEnd()
        
        # Plateau top with grass
        glColor3f(*grass_color)
        glBegin(GL_QUADS)
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-plateau_width/2, plateau_height, -plateau_width/4)
        glVertex3f(plateau_width/2, plateau_height, -plateau_width/4)
        glVertex3f(plateau_width/2, plateau_height, plateau_width/4)
        glVertex3f(-plateau_width/2, plateau_height, plateau_width/4)
        glEnd()
        
        # Side faces
        glColor3f(*rock_mid)
        glBegin(GL_QUADS)
        glNormal3f(-0.8, 0.5, 0.0)
        glVertex3f(-plateau_width/2, plateau_height, -plateau_width/4)
        glVertex3f(-plateau_width/2, plateau_height, plateau_width/4)
        glVertex3f(-base_width/2, 0.0, base_width/3)
        glVertex3f(-base_width/2, 0.0, -base_width/3)
        glEnd()
        
        glColor3f(*rock_light)
        glBegin(GL_QUADS)
        glNormal3f(0.8, 0.5, 0.0)
        glVertex3f(plateau_width/2, plateau_height, plateau_width/4)
        glVertex3f(plateau_width/2, plateau_height, -plateau_width/4)
        glVertex3f(base_width/2, 0.0, -base_width/3)
        glVertex3f(base_width/2, 0.0, base_width/3)
        glEnd()
        
    elif style == 'ridge':
        # Gunung dengan ridge (punggung)
        ridge_height = height * 0.9
        
        # Multi-faceted ridge
        segments = 5
        for i in range(segments):
            angle = (i / segments) * 180 - 90
            next_angle = ((i + 1) / segments) * 180 - 90
            
            x1 = np.cos(np.radians(angle)) * base_width/2
            z1 = np.sin(np.radians(angle)) * base_width/3
            x2 = np.cos(np.radians(next_angle)) * base_width/2
            z2 = np.sin(np.radians(next_angle)) * base_width/3
            
            # Alternate colors for facets
            if i % 2 == 0:
                glColor3f(*rock_dark)
            else:
                glColor3f(*rock_mid)
            
            glBegin(GL_TRIANGLES)
            glVertex3f(0.0, ridge_height, 0.0)
            glVertex3f(x1, 0.0, z1)
            glVertex3f(x2, 0.0, z2)
            glEnd()
    
    glPopMatrix()


def draw_mountain_range():
    """Menggambar rangkaian gunung di background"""
    
    # Layer paling belakang (paling jauh) - lebih gelap dan lebih tinggi
    far_mountains = [
        {"x": -25, "z": -35, "width": 12, "height": 14, "style": "peaked"},
        {"x": -10, "z": -38, "width": 15, "height": 16, "style": "peaked"},
        {"x": 8, "z": -36, "width": 13, "height": 15, "style": "peaked"},
        {"x": 25, "z": -34, "width": 11, "height": 13, "style": "peaked"},
    ]
    
    # Layer tengah - medium distance
    mid_mountains = [
        {"x": -30, "z": -28, "width": 10, "height": 11, "style": "ridge"},
        {"x": -15, "z": -30, "width": 11, "height": 12, "style": "plateau"},
        {"x": 0, "z": -32, "width": 14, "height": 13, "style": "peaked"},
        {"x": 18, "z": -29, "width": 10, "height": 11, "style": "ridge"},
        {"x": 32, "z": -27, "width": 9, "height": 10, "style": "plateau"},
    ]
    
    # Layer depan (lebih dekat) - lebih detail
    near_mountains = [
        {"x": -22, "z": -22, "width": 8, "height": 9, "style": "plateau"},
        {"x": -8, "z": -24, "width": 9, "height": 10, "style": "peaked"},
        {"x": 12, "z": -23, "width": 8, "height": 9, "style": "ridge"},
        {"x": 28, "z": -21, "width": 7, "height": 8, "style": "plateau"},
    ]
    
    # Gambar dari belakang ke depan untuk depth
    for mountain in far_mountains:
        draw_mountain_low_poly(mountain["x"], mountain["z"], mountain["width"], 
                              mountain["height"], mountain["style"])
    
    for mountain in mid_mountains:
        draw_mountain_low_poly(mountain["x"], mountain["z"], mountain["width"], 
                              mountain["height"], mountain["style"])
    
    for mountain in near_mountains:
        draw_mountain_low_poly(mountain["x"], mountain["z"], mountain["width"], 
                              mountain["height"], mountain["style"])


def draw_scene():
    # Gambar awan yang bergerak (menggantikan gunung)
    draw_clouds()
    
    draw_celestial_body()
    draw_farm_plot()
    draw_windmill()
    draw_barn()

    for goat in GOAT_CONFIGS:
        draw_goat(goat)
    
    # Tambahkan serigala di tengah malam
    draw_wolf()
    
    # Tambahkan peternak
    draw_farmer()
    
    # Tampilkan UI overlay
    draw_time_display()
    draw_instructions_panel()


def display():
    apply_environment_colors()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(0.0, -3.2, zoomDistance)
    glRotatef(viewAngleX, 1.0, 0.0, 0.0)
    glRotatef(viewAngleY, 0.0, 1.0, 0.0)
    apply_environment_lighting()

    draw_scene()
    glutSwapBuffers()


def timer(value):
    global angleBlade, goatWalkPhase, dayNightBlend, timeBlend, currentTime, wolfWalkPhase, previousTime
    global farmerWalkPhase, farmerArmSwing, riverFlowPhase, cloudPhase

    angleBlade -= 3.0
    if angleBlade <= -360.0:
        angleBlade += 360.0

    # Update dayNightBlend berdasarkan currentTime
    target_blend = TIME_CONFIGS[currentTime]["sky_blend"]
    if abs(dayNightBlend - target_blend) > 0.001:
        step = 0.012
        if dayNightBlend < target_blend:
            dayNightBlend = min(dayNightBlend + step, target_blend)
        else:
            dayNightBlend = max(dayNightBlend - step, target_blend)
    else:
        # Transisi selesai, reset previousTime
        if previousTime != currentTime:
            previousTime = currentTime

    # Domba hanya berkeliaran saat pagi (currentTime == 0)
    if currentTime == 0 and dayNightBlend <= 0.02:
        goatWalkPhase += 0.025
        if goatWalkPhase >= np.pi * 2:
            goatWalkPhase -= np.pi * 2
    
    # Serigala jalan-jalan saat tengah malam (currentTime == 3)
    # Lebih cepat dari domba (0.04 vs 0.025)
    if currentTime == 3:
        wolfWalkPhase += 0.04
        if wolfWalkPhase >= np.pi * 2:
            wolfWalkPhase -= np.pi * 2
    
    # Animasi peternak
    if currentTime in [1, 2, 3]:
        farmerWalkPhase += 0.03
        if farmerWalkPhase >= np.pi * 2:
            farmerWalkPhase -= np.pi * 2
        
        farmerArmSwing += 0.05
        if farmerArmSwing >= np.pi * 2:
            farmerArmSwing -= np.pi * 2
    
    # Animasi sungai (selalu mengalir)
    riverFlowPhase += 0.08
    if riverFlowPhase >= np.pi * 2:
        riverFlowPhase -= np.pi * 2
    
    # Animasi awan (selalu bergerak)
    cloudPhase += 0.05
    if cloudPhase >= 100.0:
        cloudPhase = 0.0

    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)


def mouse(button, state, x, y):
    global isDragging, lastMouseX, lastMouseY, viewMode, zoomDistance, currentTime, previousTime, transitionStartBlend

    # Convert mouse coordinates (GLUT uses top-left origin)
    window_height = 650
    mouse_x = x
    mouse_y = window_height - y  # Flip Y coordinate
    
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            # Check if clicking on buttons (for mobile touch support)
            button_clicked = False
            
            # Button T (170-195)
            if 20 <= mouse_x <= 45 and 170 <= mouse_y <= 195:
                previousTime = currentTime
                transitionStartBlend = dayNightBlend
                currentTime = (currentTime + 1) % 4
                button_clicked = True
            
            # Button 1 (135-160)
            elif 20 <= mouse_x <= 45 and 135 <= mouse_y <= 160:
                previousTime = currentTime
                transitionStartBlend = dayNightBlend
                currentTime = 0
                button_clicked = True
            
            # Button 2 (100-125)
            elif 20 <= mouse_x <= 45 and 100 <= mouse_y <= 125:
                previousTime = currentTime
                transitionStartBlend = dayNightBlend
                currentTime = 1
                button_clicked = True
            
            # Button 3 (65-90)
            elif 20 <= mouse_x <= 45 and 65 <= mouse_y <= 90:
                previousTime = currentTime
                transitionStartBlend = dayNightBlend
                currentTime = 2
                button_clicked = True
            
            # Button 4 (30-55)
            elif 20 <= mouse_x <= 45 and 30 <= mouse_y <= 55:
                previousTime = currentTime
                transitionStartBlend = dayNightBlend
                currentTime = 3
                button_clicked = True
            
            if not button_clicked:
                # Normal camera drag
                isDragging = True
                lastMouseX = x
                lastMouseY = y
                viewMode = 5
            
            glutPostRedisplay()
        elif state == GLUT_UP:
            isDragging = False
    elif button == 3 and state == GLUT_DOWN:
        zoomDistance += 0.6
        if zoomDistance > -8.0:
            zoomDistance = -8.0
        glutPostRedisplay()
    elif button == 4 and state == GLUT_DOWN:
        zoomDistance -= 0.6
        if zoomDistance < -42.0:
            zoomDistance = -42.0
        glutPostRedisplay()


def motion(x, y):
    global isDragging, lastMouseX, lastMouseY, viewAngleX, viewAngleY

    if isDragging:
        deltaX = x - lastMouseX
        deltaY = y - lastMouseY
        viewAngleY += deltaX * 0.5
        viewAngleX += deltaY * 0.5
        lastMouseX = x
        lastMouseY = y
        glutPostRedisplay()


def menu(option):
    global viewAngleX, viewAngleY, viewMode, zoomDistance

    viewMode = option
    if option < 5:
        zoomDistance = -22.0

    if option == 1:
        viewAngleX = 10.0
        viewAngleY = 90.0
    elif option == 2:
        viewAngleX = 10.0
        viewAngleY = -90.0
    elif option == 3:
        viewAngleX = 8.0
        viewAngleY = 180.0
    elif option == 4:
        viewAngleX = 12.0
        viewAngleY = 0.0
    elif option == 5:
        viewAngleX = 12.0
        viewAngleY = -18.0

    glutPostRedisplay()
    return 0


def specialKeys(key, x, y):
    global viewAngleX, viewAngleY, viewMode

    if viewMode == 5:
        if key == GLUT_KEY_RIGHT:
            viewAngleY += 5.0
        elif key == GLUT_KEY_LEFT:
            viewAngleY -= 5.0
        elif key == GLUT_KEY_UP:
            viewAngleX += 5.0
        elif key == GLUT_KEY_DOWN:
            viewAngleX -= 5.0
        glutPostRedisplay()


def keyboard(key, x, y):
    global zoomDistance, dayNightTarget, currentTime, previousTime, transitionStartBlend

    if key == b'+' or key == b'=':
        zoomDistance += 0.6
        if zoomDistance > -8.0:
            zoomDistance = -8.0
    elif key == b'-' or key == b'_':
        zoomDistance -= 0.6
        if zoomDistance < -42.0:
            zoomDistance = -42.0
    elif key == b't' or key == b'T':
        # Toggle waktu: cycle through 0 -> 1 -> 2 -> 3 -> 0
        previousTime = currentTime
        transitionStartBlend = dayNightBlend
        currentTime = (currentTime + 1) % 4
    elif key == b'1':
        previousTime = currentTime
        transitionStartBlend = dayNightBlend
        currentTime = 0  # 07:00 Pagi
    elif key == b'2':
        previousTime = currentTime
        transitionStartBlend = dayNightBlend
        currentTime = 1  # 10:00 Jam Makan
    elif key == b'3':
        previousTime = currentTime
        transitionStartBlend = dayNightBlend
        currentTime = 2  # 19:00 Malam
    elif key == b'4':
        previousTime = currentTime
        transitionStartBlend = dayNightBlend
        currentTime = 3  # 23:00 Tengah Malam
    glutPostRedisplay()


def reshape(w, h):
    if h == 0:
        h = 1

    aspect = w / h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, aspect, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 650)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"WINDMILL FARM - DAY NIGHT BARN SCENE")

    init()

    glutCreateMenu(menu)
    glutAddMenuEntry(b"SIDE VIEW 1", 1)
    glutAddMenuEntry(b"SIDE VIEW 2", 2)
    glutAddMenuEntry(b"BACK VIEW", 3)
    glutAddMenuEntry(b"FRONT VIEW", 4)
    glutAddMenuEntry(b"CUSTOM VIEW", 5)
    glutAttachMenu(GLUT_RIGHT_BUTTON)

    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(specialKeys)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(0, timer, 0)

    glutMainLoop()


if __name__ == '__main__':
    main()
