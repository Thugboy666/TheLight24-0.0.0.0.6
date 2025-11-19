# TheLight24 v6 – Galaxy Commerce GUI 3D (pygame + OpenGL) + Shop NPC overlay
import os, sys, json, math, time, random
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
import requests

WIDTH, HEIGHT = 1366, 820
API = "http://127.0.0.1:8000"

class Camera:
    def __init__(self):
        self.yaw=20; self.pitch=-15; self.dist=20.0
        self.sens=0.15; self.zoom=0.8

    def apply(self):
        glTranslatef(0,0,-self.dist)
        glRotatef(self.pitch,1,0,0)
        glRotatef(self.yaw,0,1,0)

def fetch_stars():
    try:
        r = requests.get(f"{API}/ecom/galaxy", timeout=1.0).json()
        return r.get("stars",[])
    except Exception:
        return []

def fetch_products(shop_id, audience):
    r = requests.get(f"{API}/ecom/products", params={"shop_id":shop_id,"audience":audience}, timeout=2.0).json()
    return r.get("products",[])

def draw_star(p):
    glPointSize(5.0)
    glBegin(GL_POINTS)
    glVertex3f(p[0],p[1],p[2])
    glEnd()

def draw_axes():
    glBegin(GL_LINES)
    glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(5,0,0)
    glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,5,0)
    glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,5)
    glEnd()

def draw_grid():
    glColor3f(0.2,0.25,0.35)
    glBegin(GL_LINES)
    s=1.0
    for i in range(-20,21):
        glVertex3f(i*s, 0, -20*s); glVertex3f(i*s, 0, 20*s)
        glVertex3f(-20*s,0,i*s); glVertex3f(20*s,0,i*s)
    glEnd()

def overlay_text(screen, txt, x, y, color=(230,230,230), size=18):
    font = pygame.font.SysFont("consolas", size)
    surf = font.render(txt, True, color)
    screen.blit(surf, (x,y))

def draw_shop_panel(screen, star, products, audience, cart, message):
    pygame.draw.rect(screen, (20,24,32), (WIDTH-460, 10, 450, HEIGHT-20), border_radius=10)
    pygame.draw.rect(screen, (60,70,85), (WIDTH-460, 10, 450, HEIGHT-20), 2, border_radius=10)

    overlay_text(screen, f"★ {star['star']}  [{star['country']}]", WIDTH-450, 20, (255,220,140), 20)
    overlay_text(screen, f"Audience: {audience.upper()}  (TAB per B2C/B2B)", WIDTH-450, 48, (180,200,255), 16)

    y=80
    overlay_text(screen,"Prodotti:", WIDTH-450, y, (220,220,220), 18); y+=24
    if not products:
        overlay_text(screen,"(nessun prodotto attivo)", WIDTH-450, y); y+=22
    for p in products[:10]:
        price = list(p["price"].items())[0] if p["price"] else ("EUR",0.0)
        overlay_text(screen, f"- {p['title']} ({p['sku']})  {price[0]} {price[1]:.2f}  [Q:{p['stock_qty']}]", WIDTH-450, y, (200,220,200), 16)
        y+=20

    y+=8
    overlay_text(screen, "Carrello (ENTER per checkout):", WIDTH-450, y, (255,210,160), 18); y+=24
    if not cart:
        overlay_text(screen, "(vuoto) – usa 1..9 per aggiungere i primi 9 prod.", WIDTH-450, y, (200,200,210), 16); y+=22
    tot=0.0
    for i,it in enumerate(cart):
        overlay_text(screen, f"{i+1}) {it['title']} x{it['qty']} = {it['currency']} {it['subtotal']:.2f}", WIDTH-450, y, (210,230,210), 16); y+=20
        tot+=it["subtotal"]
    y+=4
    overlay_text(screen, f"Totale: EUR {tot:.2f}", WIDTH-450, y, (255,255,180), 18); y+=26
    overlay_text(screen, "[C]rypto  [P]ayPal  [K]arta  [D] Contrassegno", WIDTH-450, y, (180,205,255), 16); y+=20
    if message:
        overlay_text(screen, f"{message}", WIDTH-450, y, (255,180,180), 16)

def main():
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("TheLight24 v6 – Galaxy Commerce")
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(True)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.02,0.03,0.06,1.0)

    cam = Camera()
    dragging=False; last=(0,0)

    stars = fetch_stars()
    # current selection
    sel = 0 if stars else -1
    audience = "b2c"
    products_cache=[]
    cart=[]  # [{product_id,title,qty,currency,unit,subtotal}]
    message="Usa FRECCE per cambiare stella. INVIO per checkout."
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_TAB:
                    audience = "b2b" if audience=="b2c" else "b2c"
                    products_cache=[]
                    cart=[]
                if e.key == pygame.K_RIGHT and stars:
                    sel = (sel+1)%len(stars); products_cache=[]; cart=[]
                if e.key == pygame.K_LEFT and stars:
                    sel = (sel-1)%len(stars); products_cache=[]; cart=[]
                if e.key in [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9]:
                    idx = (e.key - pygame.K_1)
                    if stars and products_cache and idx < len(products_cache):
                        p = products_cache[idx]
                        price = list(p["price"].items())[0] if p["price"] else ("EUR",0.0)
                        cart.append({"product_id":p["product_id"],"title":p["title"],"qty":1,
                                     "currency":price[0],"unit":price[1],"subtotal":price[1]})
                if e.key == pygame.K_RETURN and stars and products_cache:
                    # checkout default crypto
                    pm="crypto"
                    shop = stars[sel]
                    items=[{"product_id":c["product_id"],"qty":c["qty"]} for c in cart]
                    try:
                        r = requests.post(f"{API}/ecom/checkout",
                                          data={"shop_id":shop["shop_id"], "user_id":"guest",
                                                "audience":audience, "currency":"EUR", "payment":pm,
                                                "items_json":json.dumps(items)}, timeout=4.0).json()
                        if r.get("ok"):
                            message=f"Ordine {r['order_id']} {r['status']} via {r['provider']} ({r['reference']})"
                            cart=[]
                        else:
                            message="Pagamento fallito"
                    except Exception as ex:
                        message=f"Errore checkout: {ex}"
                if e.key in [pygame.K_c, pygame.K_p, pygame.K_k, pygame.K_d] and stars and products_cache and cart:
                    pm = {"c":"crypto","p":"paypal","k":"card","d":"cod"}[pygame.key.name(e.key)[0]]
                    shop = stars[sel]
                    items=[{"product_id":c["product_id"],"qty":c["qty"]} for c in cart]
                    try:
                        r = requests.post(f"{API}/ecom/checkout",
                                          data={"shop_id":shop["shop_id"], "user_id":"guest",
                                                "audience":audience, "currency":"EUR", "payment":pm,
                                                "items_json":json.dumps(items)}, timeout=4.0).json()
                        if r.get("ok"):
                            message=f"Ordine {r['order_id']} {r['status']} via {r['provider']} ({r['reference']})"
                            cart=[]
                        else:
                            message="Pagamento fallito"
                    except Exception as ex:
                        message=f"Errore checkout: {ex}"

            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button==1: dragging=True; last=e.pos
                if e.button==4: cam.dist=max(5.0, cam.dist-cam.zoom)
                if e.button==5: cam.dist=min(100.0, cam.dist+cam.zoom)
            if e.type == pygame.MOUSEBUTTONUP and e.button==1:
                dragging=False
            if e.type == pygame.MOUSEMOTION and dragging:
                dx,dy = e.pos[0]-last[0], e.pos[1]-last[1]
                cam.yaw += dx*cam.sens
                cam.pitch += dy*cam.sens
                cam.pitch = max(-89.0, min(89.0, cam.pitch))
                last=e.pos

        if stars and sel>=0:
            # ensure products cached
            if not products_cache:
                try:
                    products_cache = fetch_products(stars[sel]["shop_id"], audience)
                except Exception:
                    products_cache=[]

        glViewport(0,0,WIDTH,HEIGHT)
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60.0, WIDTH/HEIGHT, 0.1, 500.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()

        glClearColor(0.02,0.03,0.06,1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        cam.apply()

        glColor3f(0.1,0.2,0.35); draw_grid()
        glColor3f(0.9,0.9,0.2);  # stars
        for i,s in enumerate(stars):
            p = s["pos"]; draw_star((p["x"], p["y"], p["z"]))
            if i==sel:
                glColor3f(1,0.5,0.1); draw_star((p["x"], p["y"]+0.2, p["z"]))
                glColor3f(0.9,0.9,0.2)

        pygame.display.flip()
        screen = pygame.display.get_surface()
        # right panel
        if stars and sel>=0:
            draw_shop_panel(screen, stars[sel], products_cache, audience, cart, message)
        else:
            overlay_text(screen, "Nessuna stella-negozio abilitata. Crea/abilita shop via API /ecom/merchant/...", 20, 20, (255,220,160), 20)
        pygame.display.update()
        clock.tick(60)

if __name__=="__main__":
    main()
