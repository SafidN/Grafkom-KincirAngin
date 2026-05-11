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

# Animasi serigala
wolfWalkPhase = 0.0

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
    0: {"hour": 7, "minute": 0, "name": "Pagi", "sky_blend": 0.0},      # 07:00 Siang
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
    """Menampilkan panel instruksi di kiri bawah"""
    instructions = [
        "T : Toggle waktu",
        "1 : Siang (07:00)",
        "2 : Jam makan (10:00)",
        "3 : Malam (19:00)",
        "4 : Tengah malam (23:00)",
    ]
    
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
    glVertex2f(280, 120)
    glVertex2f(10, 120)
    glEnd()
    
    # Border
    glColor3f(0.8, 0.8, 0.8)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(10, 10)
    glVertex2f(280, 10)
    glVertex2f(280, 120)
    glVertex2f(10, 120)
    glEnd()
    
    # Teks instruksi
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(1.5)
    y_pos = 95
    for instruction in instructions:
        draw_text_stroke(20, y_pos, instruction, 0.08)
        y_pos -= 18
    
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


def draw_wolf():
    """Menggambar serigala yang mengintai dengan animasi jalan-jalan"""
    if currentTime != 3:  # Hanya muncul di tengah malam
        return
    
    # Animasi jalan-jalan dalam pola elips
    patrol_radius_x = 2.5
    patrol_radius_z = 1.5
    base_x = -12.5
    base_z = 5.0
    
    # Posisi serigala berdasarkan fase animasi
    wolf_x = base_x + np.cos(wolfWalkPhase) * patrol_radius_x
    wolf_z = base_z + np.sin(wolfWalkPhase * 0.8) * patrol_radius_z
    
    # Heading mengikuti arah gerakan
    heading_x = -np.sin(wolfWalkPhase) * patrol_radius_x
    heading_z = np.cos(wolfWalkPhase * 0.8) * patrol_radius_z * 0.8
    heading = -np.degrees(np.arctan2(heading_z, heading_x))
    
    # Body bobbing saat berjalan
    body_bob = 0.03 * abs(np.sin(wolfWalkPhase * 4.0))
    
    glPushMatrix()
    glTranslatef(wolf_x, 0.5 + body_bob, wolf_z)
    glRotatef(heading, 0, 1, 0)
    
    # Body (gelap)
    glColor3f(0.15, 0.15, 0.18)
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
    glColor3f(0.12, 0.12, 0.15)
    glPushMatrix()
    glTranslatef(1.0, 0.1, 0.0)
    glScalef(0.3, 0.2, 0.25)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Ears
    glColor3f(0.15, 0.15, 0.18)
    for ear_z in (-0.15, 0.15):
        glPushMatrix()
        glTranslatef(0.7, 0.5, ear_z)
        glScalef(0.15, 0.3, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()
    
    # Glowing eyes (merah menyala)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 0.2, 0.0)
    for eye_z in (-0.12, 0.12):
        glPushMatrix()
        glTranslatef(0.95, 0.25, eye_z)
        glutSolidSphere(0.08, 10, 10)
        glPopMatrix()
    glEnable(GL_LIGHTING)
    
    # Legs dengan animasi berjalan
    glColor3f(0.12, 0.12, 0.15)
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
    
    # Tail dengan animasi
    glColor3f(0.15, 0.15, 0.18)
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

    if dayNightBlend < 0.55:
        sun_t = 1.0 - smoothstep(dayNightBlend / 0.55)
        glColor3f(1.0, 0.88, 0.28)
        glPushMatrix()
        glTranslatef(9.0, 13.2, -10.0)
        glutSolidSphere(0.95 + sun_t * 0.08, 20, 20)
        glPopMatrix()

        glColor3f(1.0, 0.78, 0.2)
        for angle in range(0, 360, 45):
            glPushMatrix()
            glTranslatef(9.0, 13.2, -10.0)
            glRotatef(float(angle), 0.0, 0.0, 1.0)
            glTranslatef(0.0, 1.35, 0.0)
            glScalef(0.12, 0.5, 0.12)
            glutSolidCube(1.0)
            glPopMatrix()

    if dayNightBlend > 0.2:
        moon_t = smoothstep((dayNightBlend - 0.2) / 0.8)
        glColor3f(0.92, 0.93, 1.0)
        glPushMatrix()
        glTranslatef(-9.5, 12.2, -9.5)
        glutSolidSphere(0.8 + moon_t * 0.05, 20, 20)
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
    left = -13.8
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
    wool = (0.98, 0.97, 0.93)
    face = (0.08, 0.08, 0.09)
    eye_white = (0.96, 0.94, 0.98)
    horn_color = (0.85, 0.82, 0.75)

    # Body utama (lebih bulat dan besar)
    glColor3f(*wool)
    glPushMatrix()
    glTranslatef(0.0, 0.06, 0.0)
    glScalef(1.6, 1.3, 1.1)
    glutSolidSphere(0.5, 24, 24)
    glPopMatrix()

    # Bagian belakang (pantat) lebih bulat
    glPushMatrix()
    glTranslatef(-0.65, 0.04, 0.0)
    glScalef(0.5, 0.45, 0.45)
    glutSolidSphere(0.5, 16, 16)
    glPopMatrix()

    # Leher
    glPushMatrix()
    glTranslatef(0.5, 0.08, 0.0)
    glScalef(0.4, 0.5, 0.4)
    glutSolidSphere(0.5, 16, 16)
    glPopMatrix()

    # Head (kepala lebih detail)
    glColor3f(*face)
    glPushMatrix()
    glTranslatef(0.75, 0.08, 0.0)
    glScalef(0.9, 1.0, 0.8)
    glutSolidSphere(0.34, 20, 20)
    glPopMatrix()

    # Snout (moncong)
    glPushMatrix()
    glTranslatef(0.95, 0.0, 0.0)
    glScalef(0.5, 0.4, 0.4)
    glutSolidSphere(0.25, 16, 16)
    glPopMatrix()

    # Ears (telinga lebih besar)
    for ear_z in (-0.35, 0.35):
        glPushMatrix()
        glTranslatef(0.65, 0.25, ear_z)
        glRotatef(30 if ear_z > 0 else -30, 1, 0, 0)
        glScalef(0.18, 0.35, 0.08)
        glutSolidSphere(0.5, 12, 12)
        glPopMatrix()

    # Horns (tanduk kecil)
    glColor3f(*horn_color)
    for horn_z in (-0.15, 0.15):
        glPushMatrix()
        glTranslatef(0.7, 0.35, horn_z)
        glRotatef(25 if horn_z > 0 else -25, 0, 1, 0)
        glRotatef(-20, 1, 0, 0)
        glScalef(0.08, 0.25, 0.08)
        glutSolidCube(1.0)
        glPopMatrix()

    # Eyes (mata lebih besar)
    for eye_z in (-0.15, 0.15):
        glColor3f(*eye_white)
        glPushMatrix()
        glTranslatef(0.88, 0.15, eye_z)
        glScalef(0.18, 0.14, 0.08)
        glutSolidSphere(0.5, 12, 12)
        glPopMatrix()

        # Pupil
        glColor3f(*face)
        glPushMatrix()
        glTranslatef(0.93, 0.14, eye_z)
        glutSolidSphere(0.035, 10, 10)
        glPopMatrix()

    # Nose (hidung)
    glColor3f(0.12, 0.12, 0.12)
    for nose_z in (-0.08, 0.08):
        glPushMatrix()
        glTranslatef(1.05, -0.02, nose_z)
        glutSolidSphere(0.04, 8, 8)
        glPopMatrix()

    # Legs (kaki lebih proporsional)
    glColor3f(*face)
    leg_positions = [(-0.4, 0.25), (-0.1, -0.25), (0.35, 0.25), (0.6, -0.25)]
    for leg_x, leg_z in leg_positions:
        # Upper leg
        glPushMatrix()
        glTranslatef(leg_x, -0.2, leg_z)
        glScalef(0.18, 0.4, 0.18)
        glutSolidCube(1.0)
        glPopMatrix()

        # Lower leg
        glPushMatrix()
        glTranslatef(leg_x, -0.45, leg_z)
        glScalef(0.15, 0.3, 0.15)
        glutSolidCube(1.0)
        glPopMatrix()

        # Hoof (kuku)
        glColor3f(0.05, 0.05, 0.05)
        glPushMatrix()
        glTranslatef(leg_x, -0.58, leg_z)
        glScalef(0.2, 0.12, 0.18)
        glutSolidSphere(0.5, 12, 12)
        glPopMatrix()
        glColor3f(*face)

    # Tail (ekor)
    glColor3f(*wool)
    glPushMatrix()
    glTranslatef(-0.85, 0.08, 0.0)
    glRotatef(-30, 0, 0, 1)
    glScalef(0.12, 0.25, 0.12)
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
    
    # Tentukan target berdasarkan waktu
    if currentTime == 1:  # Jam makan (10:00) - Makan di hay bale
        # Domba menuju hay bale
        hay_idx = config["index"] % 3
        target_x = HAY_BALE_POSITIONS[hay_idx]["x"]
        target_z = HAY_BALE_POSITIONS[hay_idx]["z"]
        # Posisi di sekitar hay bale
        angle_offset = config["index"] * 120
        target_x += np.cos(np.radians(angle_offset)) * 1.2
        target_z += np.sin(np.radians(angle_offset)) * 1.2
        
        x_pos = target_x
        z_pos = target_z
        y_pos = 0.55  # Kepala menunduk makan
        
    elif currentTime >= 2:  # Malam (19:00) dan tengah malam (23:00)
        # Domba masuk kandang dengan transisi smooth
        spot = SHEEP_BARN_SPOTS[config["index"]]
        
        # Gunakan dayNightBlend untuk transisi smooth
        shelter_progress = min(dayNightBlend / 0.75, 1.0)  # Lebih cepat masuk
        
        # Fase 1: Berjalan ke pintu (0.0 - 0.6)
        walk_progress = min(shelter_progress / 0.6, 1.0)
        door_x = lerp(roam_x, spot["door_x"], walk_progress)
        door_z = lerp(roam_z, spot["door_z"], walk_progress)
        
        # Fase 2: Masuk ke dalam (0.6 - 1.0)
        if shelter_progress > 0.6:
            hide_progress = (shelter_progress - 0.6) / 0.4
            x_pos = lerp(spot["door_x"], spot["inside_x"], hide_progress)
            z_pos = lerp(spot["door_z"], spot["inside_z"], hide_progress)
            scale_factor = config["scale"] * (1.0 - hide_progress)
        else:
            x_pos = door_x
            z_pos = door_z
            scale_factor = config["scale"]
        
        y_pos = 0.62
        
        # Jika sudah masuk sepenuhnya, jangan render
        if shelter_progress >= 0.98:
            return
            
    else:  # Pagi (07:00) - Berkeliaran
        x_pos = roam_x
        z_pos = roam_z
        y_pos = 0.62 + body_bob
    
    # ===== TRANSISI SMOOTH DARI PAGI (07:00) KE JAM MAKAN (10:00) =====
    # Gunakan dayNightBlend sebagai progress indicator
    # Saat transisi dari time 0 ke time 1, dayNightBlend berubah dari 0.0 ke 0.15
    if currentTime == 0 and dayNightBlend > 0.0:
        # Sedang transisi ke jam makan
        transition_progress = dayNightBlend / 0.15  # 0.0 to 1.0
        
        # Target hay bale
        hay_idx = config["index"] % 3
        target_x = HAY_BALE_POSITIONS[hay_idx]["x"]
        target_z = HAY_BALE_POSITIONS[hay_idx]["z"]
        angle_offset = config["index"] * 120
        target_x += np.cos(np.radians(angle_offset)) * 1.2
        target_z += np.sin(np.radians(angle_offset)) * 1.2
        
        # Interpolasi posisi
        x_pos = lerp(roam_x, target_x, transition_progress)
        z_pos = lerp(roam_z, target_z, transition_progress)
        y_pos = lerp(0.62 + body_bob, 0.55, transition_progress)
        
    elif currentTime == 1 and dayNightBlend < 0.15:
        # Baru masuk jam makan, masih dalam transisi
        transition_progress = dayNightBlend / 0.15
        
        # Dari roaming ke hay bale
        hay_idx = config["index"] % 3
        target_x = HAY_BALE_POSITIONS[hay_idx]["x"]
        target_z = HAY_BALE_POSITIONS[hay_idx]["z"]
        angle_offset = config["index"] * 120
        target_x += np.cos(np.radians(angle_offset)) * 1.2
        target_z += np.sin(np.radians(angle_offset)) * 1.2
        
        # Interpolasi posisi
        x_pos = lerp(roam_x, target_x, transition_progress)
        z_pos = lerp(roam_z, target_z, transition_progress)
        y_pos = lerp(0.62 + body_bob, 0.55, transition_progress)
    
    # Hitung heading
    if currentTime == 1:
        # Saat makan, hadap ke hay bale
        hay_idx = config["index"] % 3
        hay_x = HAY_BALE_POSITIONS[hay_idx]["x"]
        hay_z = HAY_BALE_POSITIONS[hay_idx]["z"]
        path_dx = hay_x - x_pos
        path_dz = hay_z - z_pos
    else:
        path_dx = x_pos - roam_x
        path_dz = z_pos - roam_z
    
    if abs(path_dx) + abs(path_dz) > 0.001:
        heading = -np.degrees(np.arctan2(path_dz, path_dx))
    else:
        heading = roam_heading
    
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


def draw_scene():
    draw_celestial_body()
    draw_farm_plot()
    draw_windmill()
    draw_barn()

    for goat in GOAT_CONFIGS:
        draw_goat(goat)
    
    # Tambahkan serigala di tengah malam
    draw_wolf()
    
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
    global angleBlade, goatWalkPhase, dayNightBlend, timeBlend, currentTime, wolfWalkPhase

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

    # Domba hanya berkeliaran saat pagi (currentTime == 0)
    if currentTime == 0 and dayNightBlend <= 0.02:
        goatWalkPhase += 0.025
        if goatWalkPhase >= np.pi * 2:
            goatWalkPhase -= np.pi * 2
    
    # Serigala jalan-jalan saat tengah malam (currentTime == 3)
    if currentTime == 3:
        wolfWalkPhase += 0.02
        if wolfWalkPhase >= np.pi * 2:
            wolfWalkPhase -= np.pi * 2

    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)


def mouse(button, state, x, y):
    global isDragging, lastMouseX, lastMouseY, viewMode, zoomDistance

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            isDragging = True
            lastMouseX = x
            lastMouseY = y
            viewMode = 5
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
    global zoomDistance, dayNightTarget, currentTime

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
        currentTime = (currentTime + 1) % 4
    elif key == b'1':
        currentTime = 0  # 07:00 Pagi
    elif key == b'2':
        currentTime = 1  # 10:00 Jam Makan
    elif key == b'3':
        currentTime = 2  # 19:00 Malam
    elif key == b'4':
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
