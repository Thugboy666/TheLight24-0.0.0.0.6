# TheLight24 v6 – GUI 3D (pygame + PyOpenGL), point-cloud N-body viewer + overlay gatto
import os, sys, math, json, time, random
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *

API_SNAPSHOT = ("data/runtime/last_snapshot.json")  # optional cache drop
SPEECH_STATE = "data/runtime/speech_state.json"

WIDTH, HEIGHT = 1280, 800
POINT_SIZE = 2.5

class Camera:
    def __init__(self):
        self.yaw = 35.0
        self.pitch = -15.0
        self.dist = 3.0
        self.target = [0.0, 0.0, 0.0]
        self.sensitivity = 0.15
        self.zoom_sens = 0.15

    def apply(self):
        glTranslatef(0, 0, -self.dist)
        glRotatef(self.pitch, 1,0,0)
        glRotatef(self.yaw, 0,1,0)
        glTranslatef(-self.target[0], -self.target[1], -self.target[2])

def load_snapshot():
    if not os.path.exists(API_SNAPSHOT):
        return None
    with open(API_SNAPSHOT, encoding="utf-8") as f:
        return json.load(f)

def draw_points(pos):
    glPointSize(POINT_SIZE)
    glBegin(GL_POINTS)
    for p in pos:
        glVertex3f(p[0], p[1], p[2])
    glEnd()

def draw_grid():
    glColor3f(0.2,0.25,0.35)
    glBegin(GL_LINES)
    s=1.0
    for i in range(-10,11):
        glVertex3f(i*s, 0, -10*s); glVertex3f(i*s, 0, 10*s)
        glVertex3f(-10*s, 0, i*s); glVertex3f(10*s, 0, i*s)
    glEnd()

def world_from_snapshot(snap, scale=1e-9):
    if not snap: return []
    pos = snap.get("pos", [])
    # scale metri -> Gm approx
    out=[]
    for x,y,z in pos:
        out.append([x*scale, y*scale, z*scale])
    return out

def read_speech_state():
    try:
        with open(SPEECH_STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"talking": False, "vu":0.0, "interrupted": False}

def draw_cat_overlay(screen, talking, vu, interrupted):
    # piccolo riquadro in alto a sinistra
    import pygame
    box = pygame.Rect(8,8,120,120)
    pygame.draw.rect(screen, (25,28,34), box, border_radius=10)
    pygame.draw.rect(screen, (70,78,95), box, 2, border_radius=10)
    cx, cy = box.center
    r = 50
    # faccina
    pygame.draw.circle(screen, (180,180,200), (cx,cy), r)
    # occhi
    pygame.draw.circle(screen, (30,30,40), (cx-20, cy-10), 6)
    pygame.draw.circle(screen, (30,30,40), (cx+20, cy-10), 6)
    # bocca reattiva a VU
    open_mouth = (vu>=0.18) and talking and not interrupted
    if open_mouth:
        pygame.draw.ellipse(screen, (30,30,40), (cx-15, cy+10, 30, 20))
    else:
        pygame.draw.line(screen, (30,30,40), (cx-15, cy+18), (cx+15, cy+18), 3)
    # status
    font = pygame.font.SysFont("monospace", 14)
    status = "TALK" if talking and not interrupted else "IDLE" if not talking else "INT"
    color = (120,220,160) if status=="TALK" else (220,180,120) if status=="IDLE" else (220,100,100)
    lbl = font.render(f"{status}  VU:{vu:.2f}", True, color)
    screen.blit(lbl, (box.x+4, box.bottom+4))

def main():
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("TheLight24 v6 – Universe 3D Viewer")
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(True)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.02,0.03,0.06,1.0)

    cam = Camera()
    dragging=False; lastmx=0; lastmy=0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button==1:
                    dragging=True; lastmx, lastmy = e.pos
                if e.button==4:
                    cam.dist = max(0.5, cam.dist - cam.zoom_sens)
                if e.button==5:
                    cam.dist = min(10.0, cam.dist + cam.zoom_sens)
            if e.type == pygame.MOUSEBUTTONUP and e.button==1:
                dragging=False
            if e.type == pygame.MOUSEMOTION and dragging:
                mx,my = e.pos
                dx, dy = mx-lastmx, my-lastmy
                cam.yaw += dx*cam.sensitivity
                cam.pitch += dy*cam.sensitivity
                cam.pitch = max(-89.9, min(89.9, cam.pitch))
                lastmx, lastmy = mx,my

        # Load latest snapshot saved by scheduler or API client
        snap = load_snapshot()
        pts = world_from_snapshot(snap)

        # 3D draw
        glViewport(0,0,WIDTH,HEIGHT)
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60.0, WIDTH/HEIGHT, 0.01, 100.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        cam.apply()
        glColor3f(0.05,0.1,0.2); draw_grid()
        glColor3f(0.1,0.8,1.0); draw_points(pts)

        # Overlay 2D – cat
        pygame.display.flip()
        screen = pygame.display.get_surface()
        state = read_speech_state()
        draw_cat_overlay(screen, bool(state.get("talking",False)), float(state.get("vu",0.0)), bool(state.get("interrupted",False)))
        pygame.display.update()

        clock.tick(60)

if __name__ == "__main__":
    main()
