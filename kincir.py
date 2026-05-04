from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import numpy as np

# Variabel global
angleBlade = 0.0
viewAngleX = 10.0 # Sedikit nunduk biar rumputnya kelihatan
viewAngleY = 0.0
viewMode = 5 # Kita set default ke Custom View aja biar lu bisa langsung geser-geser
zoomDistance = -20.0 

isDragging = False
lastMouseX = 0
lastMouseY = 0

# Verteks bilah turbin modern (menggunakan numpy)
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

        x1, z1 = 0.0, -th/2
        blade_vertices.append([x1 * np.cos(rad_twist) - z1 * np.sin(rad_twist), p * blade_length, x1 * np.sin(rad_twist) + z1 * np.cos(rad_twist)])
        x2, z2 = 0.0, th/2
        blade_vertices.append([x2 * np.cos(rad_twist) - z2 * np.sin(rad_twist), p * blade_length, x2 * np.sin(rad_twist) + z2 * np.cos(rad_twist)])
        x3, z3 = w, th/2
        blade_vertices.append([x3 * np.cos(rad_twist) - z3 * np.sin(rad_twist), p * blade_length, x3 * np.sin(rad_twist) + z3 * np.cos(rad_twist)])
        x4, z4 = w, -th/2
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
    # Warna langit cerah (Sky Blue)
    sky_color = [0.4, 0.7, 1.0, 1.0]
    glClearColor(sky_color[0], sky_color[1], sky_color[2], sky_color[3]) 
    glEnable(GL_DEPTH_TEST)
    
    # Pencahayaan ala matahari
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Matahari agak di atas biar bayangannya bagus
    light_pos = [10.0, 20.0, 10.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

    # Efek Kabut (Atmospheric Fog) biar padang rumputnya nyatu sama langit
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogfv(GL_FOG_COLOR, sky_color) # Warna kabut sama kayak langit
    glFogf(GL_FOG_DENSITY, 0.02)     # Ketebalan kabut
    glHint(GL_FOG_HINT, GL_NICEST)

# FUNGSI BARU: Menggambar hamparan rumput & perbukitan
def draw_landscape():
    # 1. Tanah datar super luas
    glPushMatrix()
    glColor3f(0.3, 0.75, 0.25) # Hijau rumput cerah
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    # Bikin area 100x100
    glVertex3f(-50.0, 0.0,  50.0)
    glVertex3f( 50.0, 0.0,  50.0)
    glVertex3f( 50.0, 0.0, -50.0)
    glVertex3f(-50.0, 0.0, -50.0)
    glEnd()
    glPopMatrix()

    # 2. Bukit-bukit di kejauhan (menggunakan bola yang dipipihkan)
    glColor3f(0.25, 0.65, 0.2) # Hijau bukit agak sedikit gelap
    
    # Bukit 1 (Kanan Belakang)
    glPushMatrix()
    glTranslatef(15.0, -2.0, -20.0)
    glScalef(15.0, 4.0, 15.0) # Skala Y dikecilin biar gepeng jadi bukit
    glutSolidSphere(1.0, 32, 16)
    glPopMatrix()

    # Bukit 2 (Kiri Belakang)
    glPushMatrix()
    glTranslatef(-25.0, -3.0, -15.0)
    glScalef(20.0, 5.0, 20.0)
    glutSolidSphere(1.0, 32, 16)
    glPopMatrix()
    
    # Bukit 3 (Kanan Depan)
    glPushMatrix()
    glTranslatef(20.0, -4.0, 10.0)
    glScalef(18.0, 4.5, 15.0)
    glutSolidSphere(1.0, 32, 16)
    glPopMatrix()

def draw_tapered_cylinder(bottom_radius, top_radius, height, slices, stacks):
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

def drawWindmill():
    # Gambar pemandangan rumput dulu
    draw_landscape()

    # 1. Menara
    glColor3f(0.9, 0.9, 0.9)
    draw_tapered_cylinder(0.4, 0.15, 6.0, 32, 32)

    # 2. Nacelle (Badan atas)
    glPushMatrix()
    glTranslatef(0.0, 5.8, 0.0)
    glColor3f(0.95, 0.95, 0.95)
    glPushMatrix()
    glTranslatef(0.0, 0.0, -0.6)
    gluCylinder(gluNewQuadric(), 0.25, 0.2, 1.2, 32, 16)
    glTranslatef(0.0, 0.0, 0.0)
    glutSolidSphere(0.25, 32, 16)
    glPopMatrix()
    
    # 3. Rotor (Hub & Bilah)
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

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Kamera agak dinaikkan (Y diturunin jadi -3.0) biar nggak tembus rumput
    glTranslatef(0.0, -3.0, zoomDistance) 
    glRotatef(viewAngleX, 1.0, 0.0, 0.0) 
    glRotatef(viewAngleY, 0.0, 1.0, 0.0) 

    drawWindmill()
    glutSwapBuffers()

def timer(value):
    global angleBlade
    angleBlade -= 3.0
    if angleBlade <= -360.0:
        angleBlade += 360.0
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

# ==========================================
# FUNGSI KONTROL MOUSE & KEYBOARD
# ==========================================
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
        zoomDistance += 0.5
        if zoomDistance > -6.0: zoomDistance = -6.0 
        glutPostRedisplay()
    elif button == 4 and state == GLUT_DOWN:
        zoomDistance -= 0.5
        if zoomDistance < -40.0: zoomDistance = -40.0 
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
    if option < 5: zoomDistance = -20.0 

    if option == 1:   # SIDE VIEW 1
        viewAngleX = 5.0; viewAngleY = 90.0
    elif option == 2: # SIDE VIEW 2
        viewAngleX = 5.0; viewAngleY = -90.0
    elif option == 3: # BACK VIEW
        viewAngleX = 5.0; viewAngleY = 180.0
    elif option == 4: # FRONT VIEW
        viewAngleX = 10.0; viewAngleY = 0.0
    
    glutPostRedisplay()
    return 0

def specialKeys(key, x, y):
    global viewAngleX, viewAngleY, viewMode
    if viewMode == 5:
        if key == GLUT_KEY_RIGHT: viewAngleY += 5.0
        elif key == GLUT_KEY_LEFT: viewAngleY -= 5.0
        elif key == GLUT_KEY_UP: viewAngleX += 5.0
        elif key == GLUT_KEY_DOWN: viewAngleX -= 5.0
        glutPostRedisplay()

def keyboard(key, x, y):
    global zoomDistance
    if key == b'+' or key == b'=':
        zoomDistance += 0.5
        if zoomDistance > -6.0: zoomDistance = -6.0
    elif key == b'-' or key == b'_':
        zoomDistance -= 0.5
        if zoomDistance < -40.0: zoomDistance = -40.0
    glutPostRedisplay()

def reshape(w, h):
    if h == 0: h = 1
    aspect = w / h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, aspect, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"SIMULATION OF WINDMILL - MODERN TURBINE & LANDSCAPE")
    
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