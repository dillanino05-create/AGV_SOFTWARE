import os
from ultralytics import YOLO
import cv2
import numpy as np
import math
import ast
import threading
import time
import queue
import heapq
import json
from collections import deque
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN GLOBAL
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'best (1).pt')
output_path = os.path.join(script_dir, 'calibracion_en_vivo.txt')
rutas_path = os.path.join(script_dir, 'rutas_historial.json')
cal_path = os.path.join(script_dir, 'calibracion_pista.json')
zones_path     = os.path.join(script_dir, 'zonas_ajustadas.json')
rutas_pers_path = os.path.join(script_dir, 'rutas_personalizadas.json')
roi_poly_path   = os.path.join(script_dir, 'roi_poligono.json')

# ── UI ────────────────────────────────────────────────────────────
SIDEBAR_W = 270
CANVAS_H  = 600
_btn_rects_cache = {}
notificaciones   = deque(maxlen=6)

# Pestañas del sidebar
tab_activa        = 'NAVEGAR'   # 'NAVEGAR' | 'RUTAS' | 'CONFIG'
rutas_sub         = 'LISTA'     # 'LISTA' | 'NUEVA'
rutas_nueva_orig  = None
rutas_nueva_dest  = None
ruta_seleccionada = None        # (par_key_tuple, raw_idx) o None

# ── Polígono de mapa (reemplaza ROI rectángulo) ───────────────────
roi_poligono = []      # [(x,y),...] vértices del área de pista
roi_cerrado  = False   # True cuando el polígono está cerrado

# ── Rutas personalizadas dibujadas por el usuario ─────────────────
rutas_personalizadas  = {}   # {('ZonaA','ZonaB'): [(x,y),...]}
par_ajustando         = None # (str, str) par en edición actual
puntos_ruta_dibujada  = []   # puntos del trazo en curso

print("=" * 60)
print("  🤖 AGV - SISTEMA DE GUIADO v6.0 PRO")
print("=" * 60)
print("Inicializando YOLO...")
model = YOLO(model_path)

# ==========================================
# ==========================================
# 2. VARIABLES GLOBALES
# ==========================================
zonas_cam = {}
caminos_cam = []
roi_pista = None

# Grafo de navegación, hitboxes y nodos físicos de caminos
grafo_navegacion = {}      # {nombre: [(nombre_vecino, peso_px), ...]}
hitboxes_zonas = {}        # {zona: {'centro': (cx,cy), 'radio': int, 'bbox': (x1,y1,x2,y2)}}
nodos_grafo = []           # [(x, y)] — puntos físicos de los caminos dibujados

# Estado del sistema
estado_sistema = {
    'modo_operacion': 'INDI',  # 'INDI' o 'MULTI'
    'modo': 'MONITOREO',       # MONITOREO, CALIBRANDO, NAVEGANDO
    'destino': None,
    'llegada': False,
    'mostrar_diagnostico': False,
    'seleccionando_roi': False,
    'modo_ajust': 'IDLE',   # 'IDLE' | 'SELEC_ORIGEN' | 'SELEC_DESTINO' | 'DIBUJANDO'
    'ajust_origen': None,
    'ajust_destino': None,
    'ver_rutas_origen': None,
    'ver_rutas_destino': None,
}

# Estado del AGV
estado_agv = {
    'detectado': False,
    'posicion': None,
    'zona_actual': "Desconocida",
    'zona_previa': "",
    'rumbo': "DESCONOCIDO",
    'rumbo_grados': 0,
    'velocidad': 0,
    'confianza': 0,
    'bbox': None,
    'historial': deque(maxlen=10),
    'frames_perdido': 0,
    'instruccion': "Esperando...",
    'color_instruccion': (255, 255, 255),
    'trayectoria': deque(maxlen=50),
    # NUEVO: Navegación por waypoints
    'ruta_waypoints': [],      # Lista de puntos (x,y) a seguir
    'ruta_alt_waypoints': [],  # Ruta alternativa (solo visualización)
    'waypoint_actual': 0,      # Índice del waypoint actual
    'zona_siguiente': None,    # Próxima zona en la ruta
    'dist_ruta': 0,            # Distancia ruta principal en px
    'dist_ruta_alt': 0,        # Distancia ruta alternativa en px
}

# Cámara
frame_actual = None
frame_lock = threading.Lock()
cap_global = None
camara_activa = False

# FPS
fps_actual = 0
ultimo_fps_time = time.time()
frames_contados = 0

# Cola de comandos
cola_comandos = queue.Queue()

# ==========================================
# 3. COLORES DE ZONAS (según especificación)
# ==========================================
COLORES_ZONAS = {
    'Zona Despacho': (0, 255, 127),      # Verde claro fosforescente
    'Despacho': (0, 255, 127),
    'Zona Pits': (0, 140, 255),          # Amarillo oscuro (naranja-dorado)
    'Pits': (0, 140, 255),
    'Recepcion': (255, 100, 0),          # Azul
    'Banda': (255, 0, 255),              # Morado/Magenta
    'Almacen_A1': (0, 255, 255),         # Amarillo (cyan en BGR)
    'Almacen_A2': (0, 255, 255),
    'Almacen_A3': (0, 255, 255),
    'Almacen_A4': (0, 255, 255),
    'Almacen_A5': (0, 255, 255),
    'Almacen_B1': (0, 100, 0),           # Verde oscuro
    'Almacen_B2': (0, 100, 0),
    'Almacen_B3': (0, 100, 0),
    'Almacen_B4': (0, 100, 0),
    'Almacen_B5': (0, 100, 0),
}

# Colores para rutas (últimos 5 caminos)
COLORES_RUTAS = [
    (0, 255, 255),    # Cyan
    (255, 0, 255),    # Magenta
    (0, 255, 0),      # Verde
    (255, 255, 0),    # Amarillo
    (0, 128, 255),    # Naranja
]

# Rutas guardadas
rutas_guardadas = []  # Lista de rutas, cada ruta es lista de puntos

ZONAS_REQUERIDAS = [
    'Zona Despacho', 'Zona Pits', 'Recepcion', 'Banda',
    'Almacen_A1', 'Almacen_A2', 'Almacen_A3', 'Almacen_A4', 'Almacen_A5',
    'Almacen_B1', 'Almacen_B2', 'Almacen_B3', 'Almacen_B4', 'Almacen_B5'
]

# Colores generales
COLOR_OK = (0, 255, 0)
COLOR_WARN = (0, 255, 255)
COLOR_ALERT = (0, 165, 255)
COLOR_ERROR = (0, 0, 255)
COLOR_INFO = (255, 255, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_GRID = (30, 30, 30)

# ==========================================
# 4. FUNCIONES DE RUTAS
# ==========================================
def cargar_rutas():
    global rutas_guardadas
    if os.path.exists(rutas_path):
        try:
            with open(rutas_path, 'r') as f:
                data = json.load(f)
                rutas_guardadas = [deque(r, maxlen=200) for r in data.get('rutas', [])]
            print(f"✅ Rutas cargadas: {len(rutas_guardadas)} rutas")
        except Exception as e:
            print(f"⚠️ Error cargando rutas: {e}")
            rutas_guardadas = []

def guardar_rutas():
    try:
        with open(rutas_path, 'w') as f:
            json.dump({'rutas': [list(r) for r in rutas_guardadas]}, f)
    except Exception as e:
        print(f"⚠️ Error guardando rutas: {e}")

def iniciar_nueva_ruta():
    """Inicia una nueva ruta cuando se envía el AGV a un destino"""
    nueva_ruta = deque(maxlen=200)
    rutas_guardadas.append(nueva_ruta)
    # Mantener solo las últimas 5 rutas
    while len(rutas_guardadas) > 5:
        rutas_guardadas.pop(0)
    return nueva_ruta

def agregar_punto_ruta(punto):
    """Agrega un punto a la ruta actual (última ruta)"""
    if rutas_guardadas and estado_sistema['destino']:
        rutas_guardadas[-1].append(punto)

def dibujar_rutas(img):
    """Dibuja las últimas 5 rutas con colores diferentes"""
    for i, ruta in enumerate(rutas_guardadas):
        puntos = list(ruta)
        if len(puntos) < 2:
            continue
        color = COLORES_RUTAS[i % len(COLORES_RUTAS)]
        grosor = 2 if i == len(rutas_guardadas) - 1 else 1  # Ruta actual más gruesa
        for j in range(1, len(puntos)):
            cv2.line(img, tuple(puntos[j-1]), tuple(puntos[j]), color, grosor)

def obtener_color_zona(nombre):
    """Obtiene el color específico de una zona"""
    for key, color in COLORES_ZONAS.items():
        if key.lower() in nombre.lower():
            return color
    return (100, 100, 100)  # Gris por defecto

def nombre_corto(nombre):
    return nombre.replace('Almacen_', '').replace('Zona ', '')

# Rango HSV del AGV (azul oscuro). Ajustar V_MIN si el AGV es muy oscuro.
_AZUL_MIN = np.array([85,  40, 15],  dtype=np.uint8)
_AZUL_MAX = np.array([145, 255, 210], dtype=np.uint8)
_RATIO_AZUL_MIN = 0.2   # Al menos 6% de píxeles azules dentro del bbox

def tiene_color_agv(img_bgr, x1, y1, x2, y2):
    """Devuelve True si el recorte tiene suficiente azul para ser el AGV."""
    roi = img_bgr[y1:y2, x1:x2]
    if roi.size == 0:
        return False
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, _AZUL_MIN, _AZUL_MAX)
    return (mascara.mean() / 255.0) >= _RATIO_AZUL_MIN

# ==========================================
# 5. SIDEBAR UI
# ==========================================

# ── Paleta de colores moderna ─────────────────────────────────────
C_BG  = (8,  10, 16)    # fondo principal
C_S1  = (16, 19, 28)    # superficie 1
C_S2  = (24, 28, 42)    # superficie 2
C_S3  = (32, 38, 58)    # superficie 3 (cards)
C_BOR = (44, 52, 76)    # bordes
C_ACC = (0,  195,255)   # acento cyan
C_GRN = (0,  210,115)   # verde éxito
C_ORG = (255,165, 35)   # naranja aviso
C_RED = (205, 50, 50)   # rojo peligro
C_T1  = (225,232,248)   # texto primario
C_T2  = (108,122,158)   # texto secundario
C_T3  = (48,  56, 80)   # texto muted


def rrect(img, pt1, pt2, color, r=5, filled=True, thick=1):
    """Rectángulo con esquinas redondeadas."""
    x1,y1 = int(pt1[0]),int(pt1[1])
    x2,y2 = int(pt2[0]),int(pt2[1])
    r = max(0, min(r,(x2-x1)//2,(y2-y1)//2))
    if filled:
        cv2.rectangle(img,(x1+r,y1),(x2-r,y2),color,-1)
        cv2.rectangle(img,(x1,y1+r),(x2,y2-r),color,-1)
        for cx,cy in [(x1+r,y1+r),(x2-r,y1+r),(x1+r,y2-r),(x2-r,y2-r)]:
            cv2.circle(img,(cx,cy),r,color,-1)
    else:
        cv2.line(img,(x1+r,y1),(x2-r,y1),color,thick)
        cv2.line(img,(x1+r,y2),(x2-r,y2),color,thick)
        cv2.line(img,(x1,y1+r),(x1,y2-r),color,thick)
        cv2.line(img,(x2,y1+r),(x2,y2-r),color,thick)
        cv2.ellipse(img,(x1+r,y1+r),(r,r),180,0,90,color,thick)
        cv2.ellipse(img,(x2-r,y1+r),(r,r),270,0,90,color,thick)
        cv2.ellipse(img,(x1+r,y2-r),(r,r), 90,0,90,color,thick)
        cv2.ellipse(img,(x2-r,y2-r),(r,r),  0,0,90,color,thick)


def _btn(panel, bid, label, btn_rects, y, color_base, activo, h_btn=28, W=SIDEBAR_W):
    """Botón moderno con esquinas redondeadas."""
    x1, x2 = 8, W-8
    y1, y2 = y, y+h_btn
    # Fondo
    bg = tuple(min(c+50,255) for c in color_base) if activo else color_base
    rrect(panel,(x1,y1),(x2,y2),bg,r=5)
    # Brillo superior sutil
    cv2.line(panel,(x1+6,y1+1),(x2-6,y1+1),
             tuple(min(c+30,255) for c in bg),1)
    # Borde
    rrect(panel,(x1,y1),(x2,y2),C_ACC if activo else C_BOR,r=5,filled=False)
    # Barra lateral de estado
    if activo:
        rrect(panel,(x1,y1+3),(x1+4,y2-3),C_ACC,r=2)
    # Texto centrado
    (tw,th),_ = cv2.getTextSize(label,cv2.FONT_HERSHEY_SIMPLEX,0.36,1)
    tx = x1+14 if activo else x1+(x2-x1-tw)//2
    cv2.putText(panel,label,(tx,y1+(h_btn+th)//2),
                cv2.FONT_HERSHEY_SIMPLEX,0.36,C_T1,1)
    btn_rects[bid]=(x1,y1,x2,y2)
    return y2+5


def _sec(panel, titulo, y, W=SIDEBAR_W):
    """Encabezado de sección con línea divisoria."""
    cv2.putText(panel,titulo.upper(),(10,y+10),
                cv2.FONT_HERSHEY_SIMPLEX,0.27,C_T3,1)
    cv2.line(panel,(8,y+14),(W-8,y+14),C_BOR,1)
    return y+19


def dibujar_sidebar(h, W=SIDEBAR_W):
    """Panel lateral moderno con pestañas NAVEGAR | RUTAS | CONFIG."""
    global _btn_rects_cache
    panel = np.zeros((h,W,3),dtype=np.uint8)
    panel[:] = C_BG
    btn_rects = {}

    # ── CABECERA ──────────────────────────────────────────────
    cv2.rectangle(panel,(0,0),(W,50),C_S1,-1)
    cv2.line(panel,(0,50),(W,50),C_BOR,1)

    det = estado_agv['detectado']
    dot = C_GRN if det else C_RED
    # Dot con halo
    cv2.circle(panel,(18,25),9,tuple(c//4 for c in dot),-1)
    cv2.circle(panel,(18,25),6,dot,-1)
    cv2.circle(panel,(18,25),6,tuple(min(c+60,255) for c in dot),1)

    cv2.putText(panel,"AGV  GUIADO",(33,22),
                cv2.FONT_HERSHEY_SIMPLEX,0.46,C_T1,1)
    fps_c = C_GRN if fps_actual>=20 else C_ORG if fps_actual>=10 else C_RED
    modo_s = estado_sistema['modo_operacion']
    cv2.putText(panel,f"v6  ·  {modo_s}  ·  {fps_actual}fps",(33,38),
                cv2.FONT_HERSHEY_SIMPLEX,0.27,C_T2,1)

    # ── PESTAÑAS ──────────────────────────────────────────────
    TABS = [
        ('NAVEGAR', 'tab_NAVEGAR', C_GRN),
        ('RUTAS',   'tab_RUTAS',   C_ACC),
        ('CONFIG',  'tab_CONFIG',  C_ORG),
    ]
    tw_tab = W // 3
    ty1, ty2 = 52, 76

    for ti,(label,bid,acc) in enumerate(TABS):
        tx1 = ti*tw_tab;  tx2 = tx1+tw_tab
        activo = (tab_activa == bid[4:])
        bg = C_S2 if activo else C_BG
        cv2.rectangle(panel,(tx1,ty1),(tx2,ty2),bg,-1)
        # Separador vertical
        if ti > 0:
            cv2.line(panel,(tx1,ty1+6),(tx1,ty2-6),C_BOR,1)
        # Indicador inferior de color
        if activo:
            cv2.rectangle(panel,(tx1+3,ty2-3),(tx2-3,ty2),acc,-1)
        (ftw,fth),_ = cv2.getTextSize(label,cv2.FONT_HERSHEY_SIMPLEX,0.32,1)
        col_t = acc if activo else C_T3
        cv2.putText(panel,label,(tx1+(tw_tab-ftw)//2,ty1+(22+fth)//2),
                    cv2.FONT_HERSHEY_SIMPLEX,0.32,col_t,1)
        btn_rects[bid]=(tx1,ty1,tx2,ty2)

    cv2.line(panel,(0,ty2),(W,ty2),C_BOR,1)
    y = ty2+6

    # ── CONTENIDO ────────────────────────────────────────────
    if tab_activa == 'NAVEGAR':
        _tab_navegar(panel,btn_rects,y,W)
    elif tab_activa == 'RUTAS':
        _tab_rutas(panel,btn_rects,y,W)
    elif tab_activa == 'CONFIG':
        _tab_config(panel,btn_rects,y,W)

    _btn_rects_cache = btn_rects
    return panel, btn_rects


def notif(texto, color=None):
    """Registra mensaje visible en el overlay del video."""
    notificaciones.append((texto, color or (210,215,225), time.time()))


def dibujar_notificaciones(img):
    """Overlay de notificaciones recientes en esquina inferior izquierda."""
    ahora = time.time()
    y_base = img.shape[0] - 8
    for txt, col, t in reversed(list(notificaciones)):
        edad = ahora - t
        if edad > 5.0: continue
        alpha = min(1.0, (5.0-edad)/1.5)
        ca = tuple(int(c*alpha) for c in col)
        (tw,th),_ = cv2.getTextSize(txt,cv2.FONT_HERSHEY_SIMPLEX,0.36,1)
        cv2.rectangle(img,(4,y_base-th-3),(tw+10,y_base+3),(0,0,0),-1)
        cv2.putText(img,txt,(7,y_base),cv2.FONT_HERSHEY_SIMPLEX,0.36,ca,1)
        y_base -= th+6


def _sidebar_ajust_rutas(panel, y, btn_rects, W=SIDEBAR_W):
    """Contenido del sidebar exclusivo para el modo Ajustar Rutas."""
    sub  = estado_sistema['modo_ajust']
    orig = estado_sistema.get('ajust_origen')
    dest = estado_sistema.get('ajust_destino')

    # ── Estado actual ─────────────────────────────────────────
    estados_color = {
        'SELEC_ORIGEN':  ((0,160,200), "1. Elige ORIGEN"),
        'SELEC_DESTINO': ((0,200,100), "2. Elige DESTINO"),
        'DIBUJANDO':     ((0,200,255), "3. Dibuja la ruta"),
    }
    col_s, txt_s = estados_color.get(sub, ((100,100,100), ""))
    cv2.rectangle(panel, (6,y), (W-6,y+22), (20,24,36), -1)
    cv2.rectangle(panel, (6,y), (W-6,y+22), col_s, 1)
    cv2.circle(panel, (15, y+11), 5, col_s, -1)
    cv2.putText(panel, txt_s, (24, y+15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, col_s, 1)
    y += 26

    # ── Zonas para seleccionar ORIGEN ─────────────────────────
    y = _sec(panel, "  ORIGEN", y, W)
    todas_zonas = (['Zona Despacho','Zona Pits','Recepcion','Banda'] +
                   [f'Almacen_A{i}' for i in range(1,6)] +
                   [f'Almacen_B{i}' for i in range(1,6)])
    bw = (W-12)//4
    y0 = y
    for idx, z in enumerate(todas_zonas):
        col_idx = idx % 4
        row_idx = idx // 4
        x1 = 6 + col_idx*bw
        x2 = x1 + bw - 2
        y1 = y0 + row_idx*23
        y2 = y1 + 21
        es_orig = (orig == z)
        cb = (40,90,40) if es_orig else (25,35,50)
        cv2.rectangle(panel,(x1,y1),(x2,y2),cb,-1)
        cv2.rectangle(panel,(x1,y1),(x2,y2),(55,60,78),1)
        if es_orig:
            cv2.rectangle(panel,(x1,y1),(x1+2,y2),(0,220,120),-1)
        etq = nombre_corto(z)[:4]
        (tw,th),_ = cv2.getTextSize(etq, cv2.FONT_HERSHEY_SIMPLEX, 0.30, 1)
        cv2.putText(panel, etq, (x1+(bw-2-tw)//2, y1+(21+th)//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.30, (205,210,220), 1)
        btn_rects[f'ajor_{z}'] = (x1,y1,x2,y2)
    y = y0 + (len(todas_zonas)+3)//4 * 23 + 4

    # ── Zonas para seleccionar DESTINO ────────────────────────
    activo_dest = sub in ('SELEC_DESTINO', 'DIBUJANDO')
    y = _sec(panel, "  DESTINO", y, W)
    y0 = y
    for idx, z in enumerate(todas_zonas):
        col_idx = idx % 4
        row_idx = idx // 4
        x1 = 6 + col_idx*bw
        x2 = x1 + bw - 2
        y1 = y0 + row_idx*23
        y2 = y1 + 21
        es_dest = (dest == z)
        cb = (30,50,90) if es_dest else ((22,30,44) if activo_dest else (16,18,26))
        cv2.rectangle(panel,(x1,y1),(x2,y2),cb,-1)
        cv2.rectangle(panel,(x1,y1),(x2,y2),(55,60,78) if activo_dest else (30,32,40),1)
        if es_dest:
            cv2.rectangle(panel,(x1,y1),(x1+2,y2),(0,130,255),-1)
        etq = nombre_corto(z)[:4]
        (tw,th),_ = cv2.getTextSize(etq, cv2.FONT_HERSHEY_SIMPLEX, 0.30, 1)
        col_txt = (205,210,220) if activo_dest else (70,75,90)
        cv2.putText(panel, etq, (x1+(bw-2-tw)//2, y1+(21+th)//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.30, col_txt, 1)
        if activo_dest:
            btn_rects[f'ajde_{z}'] = (x1,y1,x2,y2)
    y = y0 + (len(todas_zonas)+3)//4 * 23 + 4

    # ── Rutas guardadas ───────────────────────────────────────
    y = _sec(panel, "  RUTAS GUARDADAS", y, W)
    mostradas = 0
    if rutas_personalizadas:
        for (ori, de), rutas_lista in list(rutas_personalizadas.items()):
            for r_idx, pts in enumerate(rutas_lista):
                if mostradas >= 10 or len(pts) < 2:
                    continue
                dist = int(sum(
                    math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
                    for i in range(1, len(pts))
                ))
                n = len(rutas_lista)
                etq = f"{nombre_corto(ori)}->{nombre_corto(de)}" + \
                      (f" R{r_idx+1}" if n > 1 else "") + f"  {dist}px"
                col_r = COLORES_VIS[r_idx % len(COLORES_VIS)]
                cv2.circle(panel, (12, y+8), 4, col_r, -1)
                cv2.putText(panel, etq, (22, y+12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.29, (160,220,160), 1)
                y += 16
                mostradas += 1
    if mostradas == 0:
        cv2.putText(panel, "  (ninguna guardada)", (6, y+11),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.30, (70,75,90), 1)
        y += 15

    # ── Botón salir ───────────────────────────────────────────
    y += 4
    y = _btn(panel, 'ajust_salir', 'SALIR AJUSTE', btn_rects, y, (65,20,20), False, 24, W)
    return y


# ============================================================
# OVERLAY DE RUTAS (pestaña RUTAS en el video)
# ============================================================

def dibujar_overlay_rutas(img):
    """Dibuja todas las rutas guardadas + trazo en curso sobre el frame."""
    # Zonas como referencia tenue
    for nombre, pts in zonas_cam.items():
        arr = np.array(pts, np.int32).reshape((-1,1,2))
        cv2.polylines(img, [arr], True, (50,54,70), 1)
        cx = sum(p[0] for p in pts)//len(pts)
        cy = sum(p[1] for p in pts)//len(pts)
        n_c = nombre_corto(nombre)
        (tw,th),_ = cv2.getTextSize(n_c, cv2.FONT_HERSHEY_SIMPLEX, 0.32, 1)
        cv2.rectangle(img,(cx-tw//2-2,cy-th-2),(cx+tw//2+2,cy+2),(0,0,0),-1)
        cv2.putText(img, n_c,(cx-tw//2,cy), cv2.FONT_HERSHEY_SIMPLEX,0.32,(90,100,130),1)

    # Caminos calibrados como guía
    for linea in caminos_cam:
        if len(linea)==2:
            cv2.line(img, tuple(linea[0]), tuple(linea[1]), (55,58,75), 2)

    # Rutas guardadas — no se muestran mientras se dibuja una nueva
    if rutas_sub == 'NUEVA':
        pass   # mapa limpio, solo se verá el trazo en curso
    elif ruta_seleccionada:
        # ── Modo individual: solo muestra la ruta seleccionada ──
        par_k_sel, r_idx_sel = ruta_seleccionada
        ori_sel, dest_sel = par_k_sel
        pts = rutas_personalizadas.get(par_k_sel, [[]])[r_idx_sel] \
              if r_idx_sel < len(rutas_personalizadas.get(par_k_sel, [])) else []
        if len(pts) >= 2:
            col = COLORES_VIS[r_idx_sel % len(COLORES_VIS)]
            n = len(rutas_personalizadas.get(par_k_sel, []))
            for i in range(1, len(pts)):
                cv2.line(img, tuple(pts[i-1]), tuple(pts[i]), (255,255,255), 4)
                cv2.line(img, tuple(pts[i-1]), tuple(pts[i]), col, 2)
            cv2.circle(img, tuple(pts[0]),  9, C_GRN, -1)
            cv2.circle(img, tuple(pts[-1]), 9, C_ACC, -1)
            dist = int(sum(math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
                           for i in range(1, len(pts))))
            etq = f"{nombre_corto(ori_sel)} -> {nombre_corto(dest_sel)}" + \
                  (f"  R{r_idx_sel+1}" if n > 1 else "") + f"   {dist}px"
            mid = pts[len(pts)//2]
            (tw,th),_ = cv2.getTextSize(etq, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
            rrect(img, (int(mid[0])+3, int(mid[1])-th-8),
                       (int(mid[0])+tw+10, int(mid[1])+4), (0,0,0), r=4)
            cv2.putText(img, etq, (int(mid[0])+7, int(mid[1])-2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255,255,200), 1)
    else:
        # ── Modo general: muestra todas las rutas (tenues) ──────
        for par_k, rutas_lista in rutas_personalizadas.items():
            ori, dest = par_k
            for r_idx, pts in enumerate(rutas_lista):
                if len(pts) < 2: continue
                col = COLORES_VIS[r_idx % len(COLORES_VIS)]
                for i in range(1, len(pts)):
                    cv2.line(img, tuple(pts[i-1]), tuple(pts[i]), col, 1)
                cv2.circle(img, tuple(pts[0]),  4, col, -1)
                cv2.circle(img, tuple(pts[-1]), 4, col, -1)
                n = len(rutas_lista)
                mid = pts[len(pts)//2]
                etq = f"{nombre_corto(ori)}->{nombre_corto(dest)}" + \
                      (f" R{r_idx+1}" if n > 1 else "")
                cv2.putText(img, etq, (int(mid[0])+5, int(mid[1])-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.28, col, 1)

    # Trazo en curso (nueva ruta)
    if puntos_ruta_dibujada:
        for i in range(1,len(puntos_ruta_dibujada)):
            cv2.line(img, tuple(puntos_ruta_dibujada[i-1]),
                     tuple(puntos_ruta_dibujada[i]), (0,240,240), 2)
        for p in puntos_ruta_dibujada:
            cv2.circle(img, tuple(p), 4, (0,240,240), -1)
        cv2.circle(img, tuple(puntos_ruta_dibujada[0]),  8, (0,220,120), 2)
        cv2.circle(img, tuple(puntos_ruta_dibujada[-1]), 8, (0,100,255), 2)

    # Barra de estado
    h,w = img.shape[:2]
    cv2.rectangle(img,(0,h-26),(w,h),(12,14,20),-1)
    if rutas_sub == 'NUEVA':
        ori_s = nombre_corto(rutas_nueva_orig) if rutas_nueva_orig else "---"
        des_s = nombre_corto(rutas_nueva_dest) if rutas_nueva_dest else "---"
        n_pts = len(puntos_ruta_dibujada)
        msg = f"NUEVA RUTA  {ori_s} -> {des_s}  |  {n_pts} pts  |  Clic=agregar  Der=deshacer"
    elif ruta_seleccionada:
        par_k, r_i = ruta_seleccionada
        ori_s = nombre_corto(par_k[0]); dest_s = nombre_corto(par_k[1])
        msg = f"VIENDO: {ori_s} -> {dest_s}  R{r_i+1}  |  Clic VER de nuevo para deseleccionar"
    else:
        total = sum(len(v) for v in rutas_personalizadas.values())
        msg = f"{total} ruta(s) guardada(s)  |  Presiona VER en el sidebar para ver una ruta"
    cv2.putText(img, msg,(5,h-7), cv2.FONT_HERSHEY_SIMPLEX,0.35,(120,140,180),1)
    return img


# ============================================================
# PESTAÑAS DEL SIDEBAR
# ============================================================

def _zona_grid_tab(panel, btn_rects, y, prefix, seleccionada, activo=True, W=SIDEBAR_W):
    """Grid de zonas compacto para selección de origen/destino."""
    todas = (['Zona Despacho','Zona Pits','Recepcion','Banda'] +
             [f'Almacen_A{i}' for i in range(1,6)] +
             [f'Almacen_B{i}' for i in range(1,6)])
    bw = (W-12)//4
    y0 = y
    for idx, z in enumerate(todas):
        ci = idx%4; ri = idx//4
        x1 = 6+ci*bw; x2 = x1+bw-2
        y1 = y0+ri*22; y2 = y1+20
        act = (seleccionada == z)
        if not activo:
            cb = (16,18,25)
        else:
            cb = (38,85,38) if (act and 'or' in prefix) else \
                 (25,40,90) if (act and 'de' in prefix) else (22,28,42)
        cv2.rectangle(panel,(x1,y1),(x2,y2),cb,-1)
        cv2.rectangle(panel,(x1,y1),(x2,y2),(52,58,75) if activo else (28,30,38),1)
        if act:
            col_ac = (0,220,120) if 'or' in prefix else (0,130,255)
            cv2.rectangle(panel,(x1,y1),(x1+2,y2),col_ac,-1)
        etq = nombre_corto(z)[:5]
        col_t = (200,208,218) if activo else (50,55,65)
        (tw,th),_ = cv2.getTextSize(etq,cv2.FONT_HERSHEY_SIMPLEX,0.29,1)
        cv2.putText(panel,etq,(x1+(bw-2-tw)//2,y1+(20+th)//2),
                    cv2.FONT_HERSHEY_SIMPLEX,0.29,col_t,1)
        if activo:
            btn_rects[f'{prefix}{z}'] = (x1,y1,x2,y2)
    return y0 + (len(todas)+3)//4 * 22 + 4


def _zone_btn(panel, btn_rects, bid, label, x1, y1, x2, y2, activo):
    """Botón de zona con esquinas redondeadas."""
    bg = C_S3 if activo else C_S2
    rrect(panel,(x1,y1),(x2,y2),bg,r=4)
    if activo:
        # Borde brillante + top-glow
        rrect(panel,(x1,y1),(x2,y2),C_GRN,r=4,filled=False)
        cv2.line(panel,(x1+5,y1+1),(x2-5,y1+1),
                 tuple(min(c+40,255) for c in C_S3),1)
    else:
        rrect(panel,(x1,y1),(x2,y2),C_BOR,r=4,filled=False)
    (tw,th),_ = cv2.getTextSize(label,cv2.FONT_HERSHEY_SIMPLEX,0.34,1)
    col_t = C_GRN if activo else C_T1
    cv2.putText(panel,label,(x1+(x2-x1-tw)//2,y1+(y2-y1+th)//2),
                cv2.FONT_HERSHEY_SIMPLEX,0.34,col_t,1)
    if bid: btn_rects[bid]=(x1,y1,x2,y2)


def _tab_navegar(panel, btn_rects, y, W=SIDEBAR_W):
    """Pestaña NAVEGAR con botones modernos."""
    dest = estado_sistema.get('destino','')

    y = _sec(panel,"DESTINO",y,W)
    # Grid 2×2 zonas principales
    top4=[('Zona Despacho','Despch'),('Zona Pits','Pits'),
          ('Recepcion','Recep'),('Banda','Banda')]
    bw2=(W-18)//2
    for row in range(2):
        for col in range(2):
            zk,zl=top4[row*2+col]
            x1=8+col*(bw2+2); x2=x1+bw2
            _zone_btn(panel,btn_rects,f'go_{zk}',zl,x1,y,x2,y+27,dest==zk)
        y+=31
    y+=2

    # Filas A1-A5 / B1-B5
    PREFIJOS=[('Almacen_A','A','A'),(  'Almacen_B','B','B')]
    for pref,pre_e,_ in PREFIJOS:
        bw5=(W-16)//5; y0=y
        for j in range(1,6):
            zk=f'{pref}{j}'
            etq=f'{pre_e}{j}'
            x1=8+(j-1)*bw5; x2=x1+bw5-2
            _zone_btn(panel,btn_rects,f'go_{zk}',etq,x1,y0,x2,y0+24,dest==zk)
        y=y0+28
    y+=4

    # Botón PARAR — rojo redondeado
    x1,x2,y1,y2 = 8,W-8,y,y+30
    cp = (140,22,22) if dest else (55,20,20)
    rrect(panel,(x1,y1),(x2,y2),cp,r=6)
    cv2.line(panel,(x1+7,y1+1),(x2-7,y1+1),(170,40,40),1)
    rrect(panel,(x1,y1),(x2,y2),C_RED if dest else C_BOR,r=6,filled=False)
    etq_p="PARAR NAVEGACION"
    (tw,th),_=cv2.getTextSize(etq_p,cv2.FONT_HERSHEY_SIMPLEX,0.36,1)
    cv2.putText(panel,etq_p,(x1+(x2-x1-tw)//2,y1+(30+th)//2),
                cv2.FONT_HERSHEY_SIMPLEX,0.36,(240,175,175),1)
    btn_rects['parar']=(x1,y1,x2,y2)
    y=y2+6

    # ── Card de estado AGV ────────────────────────────────
    y = _sec(panel,"ESTADO AGV",y,W)
    det = estado_agv['detectado']
    # Card de estado
    rrect(panel,(8,y),(W-8,y+16),C_S2,r=4)
    dot_c = C_GRN if det else C_RED
    cv2.circle(panel,(17,y+8),5,dot_c,-1)
    cv2.circle(panel,(17,y+8),5,tuple(min(c+60,255) for c in dot_c),1)
    txt_d='AGV DETECTADO' if det else 'SIN DETECTAR'
    cv2.putText(panel,txt_d,(26,y+12),cv2.FONT_HERSHEY_SIMPLEX,0.33,
                (165,240,165) if det else (210,165,165),1)
    y+=20

    if det:
        # Mini card con zona y rumbo
        rrect(panel,(8,y),(W-8,y+34),C_S1,r=4)
        rrect(panel,(8,y),(W-8,y+34),C_BOR,r=4,filled=False)
        z_s = nombre_corto(estado_agv['zona_actual'])
        r_s = estado_agv['rumbo']
        cv2.putText(panel,f"Zona   {z_s}",(14,y+13),
                    cv2.FONT_HERSHEY_SIMPLEX,0.32,C_ACC,1)
        cv2.putText(panel,f"Rumbo  {r_s}",(14,y+27),
                    cv2.FONT_HERSHEY_SIMPLEX,0.32,C_T2,1)
        y+=38

    if dest:
        # Card destino + instruccion
        dest_s=nombre_corto(dest)
        rrect(panel,(8,y),(W-8,y+22),C_S3,r=5)
        rrect(panel,(8,y),(W-8,y+22),C_GRN,r=5,filled=False)
        cv2.putText(panel,f">> {dest_s}",(15,y+15),
                    cv2.FONT_HERSHEY_SIMPLEX,0.38,C_GRN,1)
        y+=26
        instr=estado_agv['instruccion']; ci=estado_agv['color_instruccion']
        words,lines,cur=instr.split(),[],''
        for w in words:
            test=(cur+' '+w).strip()
            if cv2.getTextSize(test,cv2.FONT_HERSHEY_SIMPLEX,0.33,1)[0][0]>W-18:
                if cur: lines.append(cur); cur=w
            else: cur=test
        if cur: lines.append(cur)
        for ln in lines[:3]:
            cv2.putText(panel,f"  {ln}",(10,y+11),cv2.FONT_HERSHEY_SIMPLEX,0.33,ci,1)
            y+=14
    return y


def _tab_rutas(panel, btn_rects, y, W=SIDEBAR_W):
    """Pestaña RUTAS — lista agrupada con cards modernas."""
    if rutas_sub == 'LISTA':
        total = sum(len(v) for v in rutas_personalizadas.values())

        # Badge de total
        badge = f"{total} ruta(s)"
        (bw,bh),_ = cv2.getTextSize(badge,cv2.FONT_HERSHEY_SIMPLEX,0.29,1)
        rrect(panel,(W-bw-14,y+1),(W-8,y+14),(30,45,65),r=3)
        cv2.putText(panel,badge,(W-bw-10,y+11),cv2.FONT_HERSHEY_SIMPLEX,0.29,C_ACC,1)
        cv2.putText(panel,"RUTAS GUARDADAS",(8,y+11),
                    cv2.FONT_HERSHEY_SIMPLEX,0.29,C_T3,1)
        y+=18

        count = 0
        for par_k, rutas_lista in rutas_personalizadas.items():
            ori, dest = par_k
            n = [pts for pts in rutas_lista if len(pts)>=2]
            if not n: continue

            # ── Cabecera de grupo (card header) ──────────────
            rrect(panel,(8,y),(W-8,y+18),C_S2,r=4)
            cv2.line(panel,(12,y+18),(W-12,y+18),C_BOR,1)
            grp_txt = f"{nombre_corto(ori)}  →  {nombre_corto(dest)}"
            cv2.putText(panel,grp_txt,(14,y+13),
                        cv2.FONT_HERSHEY_SIMPLEX,0.32,C_T2,1)
            # Badge de cantidad
            bc = f"×{len(n)}"
            (bcw,bch),_ = cv2.getTextSize(bc,cv2.FONT_HERSHEY_SIMPLEX,0.28,1)
            rrect(panel,(W-bcw-16,y+3),(W-10,y+15),(38,50,75),r=3)
            cv2.putText(panel,bc,(W-bcw-12,y+13),
                        cv2.FONT_HERSHEY_SIMPLEX,0.28,C_ACC,1)
            y+=19

            for r_idx, pts in enumerate(rutas_lista):
                if len(pts)<2: continue
                dist = int(sum(math.hypot(pts[i][0]-pts[i-1][0],
                                         pts[i][1]-pts[i-1][1])
                               for i in range(1,len(pts))))
                col  = COLORES_VIS[r_idx % len(COLORES_VIS)]
                es_sel = (ruta_seleccionada == (par_k, r_idx))

                # Card de ruta
                bg = C_S3 if es_sel else C_S1
                rrect(panel,(10,y),(W-10,y+20),bg,r=3)
                bor = col if es_sel else C_BOR
                rrect(panel,(10,y),(W-10,y+20),bor,r=3,filled=False)

                # Dot de color
                cv2.circle(panel,(18,y+10),5,col,-1)
                # Texto
                etq = f"R{r_idx+1}  {dist}px"
                cv2.putText(panel,etq,(28,y+14),cv2.FONT_HERSHEY_SIMPLEX,0.30,
                            C_T1 if es_sel else col,1)

                # Botón VER
                bv1,bv2 = W-46,W-27
                ver_bg = (20,55,30) if es_sel else (15,35,22)
                rrect(panel,(bv1,y+3),(bv2,y+17),ver_bg,r=3)
                rrect(panel,(bv1,y+3),(bv2,y+17),C_GRN,r=3,filled=False)
                cv2.putText(panel,"VER",(bv1+3,y+13),cv2.FONT_HERSHEY_SIMPLEX,
                            0.24,C_GRN,1)
                btn_rects[f'sel_ruta_{count}'] = (bv1,y+3,bv2,y+17)

                # Botón X
                rrect(panel,(W-24,y+3),(W-10,y+17),(80,18,18),r=3)
                rrect(panel,(W-24,y+3),(W-10,y+17),C_RED,r=3,filled=False)
                cv2.putText(panel,"X",(W-20,y+13),cv2.FONT_HERSHEY_SIMPLEX,
                            0.28,(255,110,110),1)
                btn_rects[f'del_ruta_{count}'] = (W-24,y+3,W-10,y+17)

                y+=22; count+=1
            # Espacio entre grupos
            y+=4

        if total == 0:
            rrect(panel,(8,y),(W-8,y+30),C_S1,r=5)
            cv2.putText(panel,"Sin rutas guardadas",(14,y+19),
                        cv2.FONT_HERSHEY_SIMPLEX,0.30,C_T3,1); y+=34
        y+=2
        y = _btn(panel,'nueva_ruta','+ NUEVA RUTA',btn_rects,y,(15,58,40),False,30,W)

    else:  # rutas_sub == 'NUEVA'
        y = _sec(panel,"NUEVA RUTA — ORIGEN",y,W)
        y = _zona_grid_tab(panel,btn_rects,y,'nor_',rutas_nueva_orig,True,W)

        tiene_orig = rutas_nueva_orig is not None
        y = _sec(panel,"NUEVA RUTA — DESTINO",y,W)
        y = _zona_grid_tab(panel,btn_rects,y,'nde_',rutas_nueva_dest,tiene_orig,W)

        y = _sec(panel,"ESTADO",y,W)
        # Mini card de resumen
        ori_s = nombre_corto(rutas_nueva_orig) if rutas_nueva_orig else "---"
        des_s = nombre_corto(rutas_nueva_dest) if rutas_nueva_dest else "---"
        n_pts = len(puntos_ruta_dibujada)
        rrect(panel,(8,y),(W-8,y+54),C_S2,r=5)
        rrect(panel,(8,y),(W-8,y+54),C_BOR,r=5,filled=False)
        cv2.putText(panel,f"De:    {ori_s}",(14,y+14),
                    cv2.FONT_HERSHEY_SIMPLEX,0.32,C_ACC,1)
        cv2.putText(panel,f"A:     {des_s}",(14,y+28),
                    cv2.FONT_HERSHEY_SIMPLEX,0.32,C_ACC,1)
        col_p = C_GRN if n_pts>1 else C_T3
        cv2.putText(panel,f"Pts:   {n_pts}",(14,y+44),
                    cv2.FONT_HERSHEY_SIMPLEX,0.32,col_p,1)
        y+=58
        can_save = (rutas_nueva_orig and rutas_nueva_dest and n_pts>=2)
        col_sv = (16,68,32) if can_save else (20,32,22)
        y = _btn(panel,'save_ruta','GUARDAR RUTA',btn_rects,y,col_sv,can_save,29,W)
        y = _btn(panel,'clear_ruta','Borrar puntos',btn_rects,y,(42,28,12),False,25,W)
        y = _btn(panel,'cancel_ruta','Cancelar',btn_rects,y,(60,16,16),False,25,W)
    return y


def _tab_config(panel, btn_rects, y, W=SIDEBAR_W):
    """Pestaña CONFIG con estilo moderno."""
    y = _sec(panel,"MODO DE OPERACION",y,W)
    es_indi = estado_sistema['modo_operacion']=='INDI'
    y = _btn(panel,'indi', 'INDI  (camara viva)',  btn_rects,y,(18,52,18), es_indi)
    y = _btn(panel,'multi','MULTI (perspectiva)',   btn_rects,y,(18,18,58), not es_indi)
    y+=4
    y = _sec(panel,"CALIBRACION",y,W)
    modo = estado_sistema['modo']
    y = _btn(panel,'calibrar','Calibrar Zonas',btn_rects,y,(48,44,10),modo=='CALIBRANDO')
    y = _btn(panel,'mapa','Definir Mapa',      btn_rects,y,(46,12,46),
             estado_sistema.get('seleccionando_roi',False))
    y+=4
    y = _sec(panel,"OPCIONES",y,W)
    y = _btn(panel,'diagnostico','Diagnostico',btn_rects,y,(10,28,50),
             estado_sistema['mostrar_diagnostico'])
    y+=6
    # Info card
    rrect(panel,(8,y),(W-8,y+46),C_S1,r=5)
    rrect(panel,(8,y),(W-8,y+46),C_BOR,r=5,filled=False)
    n_zonas  = len(zonas_cam)
    n_camin  = len(caminos_cam)
    n_rutas  = sum(len(v) for v in rutas_personalizadas.values())
    cv2.putText(panel,f"Zonas:   {n_zonas}",(14,y+14),
                cv2.FONT_HERSHEY_SIMPLEX,0.30,C_T2,1)
    cv2.putText(panel,f"Caminos: {n_camin}",(14,y+28),
                cv2.FONT_HERSHEY_SIMPLEX,0.30,C_T2,1)
    cv2.putText(panel,f"Rutas:   {n_rutas}",(14,y+42),
                cv2.FONT_HERSHEY_SIMPLEX,0.30,C_T2,1)
    y+=50
    return y


# ============================================================
# SIDEBAR PRINCIPAL CON PESTAÑAS
# ============================================================

def procesar_click_sidebar(sx, sy):
    """Clic en coordenadas locales del sidebar."""
    global tab_activa, rutas_sub, rutas_nueva_orig, rutas_nueva_dest
    global puntos_ruta_dibujada, ruta_seleccionada
    for bid,(x1,y1,x2,y2) in _btn_rects_cache.items():
        if not(x1<=sx<=x2 and y1<=sy<=y2): continue

        # ── Cambio de pestaña ─────────────────────────────────
        if bid.startswith('tab_'):
            tab_activa = bid[4:]   # 'NAVEGAR' | 'RUTAS' | 'CONFIG'
            break

        # ── Pestaña NAVEGAR ───────────────────────────────────
        if bid == 'parar':
            cola_comandos.put('parar')
        elif bid.startswith('go_'):
            cola_comandos.put('__nav__'+bid[3:])

        # ── Pestaña CONFIG ────────────────────────────────────
        elif bid in ('indi','multi','calibrar','mapa','diagnostico'):
            cola_comandos.put(bid)

        # ── Pestaña RUTAS — lista ─────────────────────────────
        elif bid == 'nueva_ruta':
            rutas_sub = 'NUEVA'
            rutas_nueva_orig = None
            rutas_nueva_dest = None
            puntos_ruta_dibujada = []

        elif bid.startswith('sel_ruta_'):
            idx_sel = int(bid[9:])
            todas = [(pk,ri) for pk,rl in rutas_personalizadas.items()
                     for ri,pts in enumerate(rl) if len(pts)>=2]
            if idx_sel < len(todas):
                clave = todas[idx_sel]
                ruta_seleccionada = None if ruta_seleccionada == clave else clave

        elif bid.startswith('del_ruta_'):
            idx_del = int(bid[9:])
            todas = [(pk,ri) for pk,rl in rutas_personalizadas.items()
                     for ri,pts in enumerate(rl) if len(pts)>=2]
            if idx_del < len(todas):
                par_k, r_i = todas[idx_del]
                if ruta_seleccionada == (par_k, r_i):
                    ruta_seleccionada = None
                rutas_personalizadas[par_k].pop(r_i)
                if not rutas_personalizadas[par_k]:
                    del rutas_personalizadas[par_k]
                guardar_rutas_personalizadas()
                notif(f"Ruta R{idx_del+1} eliminada", (220,80,80))

        # ── Pestaña RUTAS — nueva ruta ────────────────────────
        elif bid.startswith('nor_'):
            zona = bid[4:]
            rutas_nueva_orig = zona
            if rutas_nueva_dest == zona:
                rutas_nueva_dest = None
            puntos_ruta_dibujada = []
            notif(f"Origen: {nombre_corto(zona)}", (0,200,120))

        elif bid.startswith('nde_'):
            zona = bid[4:]
            if rutas_nueva_orig and zona != rutas_nueva_orig:
                rutas_nueva_dest = zona
                puntos_ruta_dibujada = []
                notif(f"Destino: {nombre_corto(zona)} — dibuja la ruta en el video", (0,190,240))

        elif bid == 'save_ruta':
            if rutas_nueva_orig and rutas_nueva_dest and len(puntos_ruta_dibujada)>=2:
                par = (rutas_nueva_orig, rutas_nueva_dest)
                if par not in rutas_personalizadas:
                    rutas_personalizadas[par] = []
                rutas_personalizadas[par].append([[p[0],p[1]] for p in puntos_ruta_dibujada])
                guardar_rutas_personalizadas()
                n = len(rutas_personalizadas[par])
                notif(f"Ruta {n} guardada: {nombre_corto(rutas_nueva_orig)}->{nombre_corto(rutas_nueva_dest)}", (0,220,120))
                rutas_nueva_orig = None
                rutas_nueva_dest = None
                puntos_ruta_dibujada = []
                rutas_sub = 'LISTA'

        elif bid == 'clear_ruta':
            puntos_ruta_dibujada = []

        elif bid == 'cancel_ruta':
            rutas_nueva_orig = None
            rutas_nueva_dest = None
            puntos_ruta_dibujada = []
            rutas_sub = 'LISTA'

        break


# ==========================================
# 5B. HILO DE CÁMARA
# ==========================================
def hilo_camara():
    global cap_global, camara_activa, frame_actual
    cap_global = cv2.VideoCapture(2)
    cap_global.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap_global.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap_global.set(cv2.CAP_PROP_FPS, 30)
    cap_global.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap_global.isOpened():
        print("❌ ERROR: No se pudo abrir la cámara")
        camara_activa = False
        return
    for _ in range(1,5):
        cap_global.read()
    camara_activa = True
    print("✅ Cámara activa")
    while camara_activa:
        success, frame = cap_global.read()
        if success:
            with frame_lock:
                frame_actual = frame

def obtener_frame():
    with frame_lock:
        if frame_actual is not None:
            return frame_actual.copy()
    return None

# ==========================================
# 6. CARGAR/GUARDAR CALIBRACIÓN
# ==========================================
def cargar_calibracion():
    global zonas_cam, caminos_cam, roi_pista, grafo_navegacion, hitboxes_zonas
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r') as f:
                contenido = f.read()
            if 'zonas_cam = ' in contenido:
                inicio = contenido.find('zonas_cam = ') + len('zonas_cam = ')
                fin = contenido.find('\ncaminos_cam = ')
                if fin == -1: fin = len(contenido)
                zonas_cam = ast.literal_eval(contenido[inicio:fin].strip())
            if 'caminos_cam = ' in contenido:
                inicio_c = contenido.find('caminos_cam = ') + len('caminos_cam = ')
                fin_c = contenido.find('\nroi_pista = ')
                if fin_c == -1: fin_c = len(contenido)
                caminos_cam = ast.literal_eval(contenido[inicio_c:fin_c].strip())
            if 'roi_pista = ' in contenido:
                inicio_r = contenido.find('roi_pista = ') + len('roi_pista = ')
                roi_pista = ast.literal_eval(contenido[inicio_r:].strip())
            
            # NUEVO: Reconstruir grafo y hitboxes
            reconstruir_grafo_navegacion()
            reconstruir_hitboxes()
            
            print(f"✅ Calibración: {len(zonas_cam)} zonas, {len(caminos_cam)} caminos")
            return True
        except Exception as e:
            print(f"⚠️ Error cargando: {e}")
    return False

def guardar_calibracion():
    with open(output_path, 'w') as f:
        f.write(f"zonas_cam = {zonas_cam}\n")
        f.write(f"caminos_cam = {caminos_cam}\n")
        f.write(f"roi_pista = {roi_pista}\n")
    if roi_poligono:
        with open(roi_poly_path, 'w') as f:
            json.dump(roi_poligono, f)
    print("💾 Guardado")


def cargar_roi_poligono():
    global roi_poligono, roi_cerrado
    if os.path.exists(roi_poly_path):
        try:
            with open(roi_poly_path) as f:
                roi_poligono = [tuple(p) for p in json.load(f)]
            roi_cerrado = len(roi_poligono) >= 3
            print(f"✅ Polígono ROI: {len(roi_poligono)} vértices")
        except Exception as e:
            print(f"⚠️ Error cargando polígono: {e}")


def cargar_rutas_personalizadas():
    """Carga rutas. Formato nuevo: {par: [[ruta1], [ruta2], ...]}
    Compatible con formato viejo: {par: [[x,y],[x,y],...]}."""
    global rutas_personalizadas
    if not os.path.exists(rutas_pers_path):
        return
    try:
        with open(rutas_pers_path) as f:
            data = json.load(f)
        rutas_personalizadas = {}
        for k, v in data.items():
            par = tuple(k.split('|'))
            # Detectar formato viejo: lista de [x,y] vs formato nuevo: lista de listas de [x,y]
            if v and isinstance(v[0], (int, float)):
                # Formato muy viejo (plano) — convertir
                rutas_personalizadas[par] = [[v]]
            elif v and isinstance(v[0], list) and v[0] and isinstance(v[0][0], (int, float)):
                # Formato viejo: una sola ruta como [[x,y],[x,y],...]
                rutas_personalizadas[par] = [[[int(p[0]),int(p[1])] for p in v]]
            else:
                # Formato nuevo: lista de rutas
                rutas_personalizadas[par] = [
                    [[int(p[0]),int(p[1])] for p in ruta] for ruta in v
                ]
        total = sum(len(v) for v in rutas_personalizadas.values())
        print(f"✅ Rutas personalizadas: {len(rutas_personalizadas)} pares, {total} rutas")
    except Exception as e:
        print(f"⚠️ Error cargando rutas personalizadas: {e}")


def guardar_rutas_personalizadas():
    try:
        data = {
            f"{k[0]}|{k[1]}": [[[p[0],p[1]] for p in ruta] for ruta in rutas]
            for k, rutas in rutas_personalizadas.items()
        }
        with open(rutas_pers_path, 'w') as f:
            json.dump(data, f, indent=2)
        total = sum(len(v) for v in rutas_personalizadas.values())
        print(f"💾 Rutas personalizadas: {len(rutas_personalizadas)} pares, {total} rutas")
    except Exception as e:
        print(f"⚠️ Error guardando: {e}")

# ==========================================
# NUEVO: 6.5 FUNCIONES DE GRAFO Y HITBOXES
# ==========================================

def reconstruir_hitboxes():
    """Calcula centro, radio y bbox para cada zona poligonal"""
    global hitboxes_zonas
    hitboxes_zonas = {}
    for nombre, pts in zonas_cam.items():
        if len(pts) < 3:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx = sum(xs) // len(xs)
        cy = sum(ys) // len(ys)
        # Radio = distancia máxima del centro a cualquier vértice
        radio = int(max(math.hypot(p[0]-cx, p[1]-cy) for p in pts))
        # BBox rectangular
        x1, y1 = min(xs), min(ys)
        x2, y2 = max(xs), max(ys)
        hitboxes_zonas[nombre] = {
            'centro': (cx, cy),
            'radio': radio,
            'bbox': (x1, y1, x2, y2)
        }
    print(f"📦 Hitboxes: {len(hitboxes_zonas)} zonas")

def get_pos_nodo(nombre):
    """Devuelve (x, y) de cualquier nodo: zona o punto físico de camino."""
    if nombre.startswith('_n_'):
        idx = int(nombre[3:])
        return nodos_grafo[idx] if idx < len(nodos_grafo) else (0, 0)
    return hitboxes_zonas.get(nombre, {}).get('centro', (0, 0))

def reconstruir_grafo_navegacion():
    """
    Grafo basado en los segmentos de camino dibujados.
    Nodos: endpoints de líneas agrupados por proximidad (_n_X) + centros de zonas.
    Aristas: cada segmento dibujado + conexión zona→nodo_más_cercano.
    """
    global grafo_navegacion, nodos_grafo
    TOLERANCIA = 25   # px — endpoints dentro de este radio = mismo nodo

    # ── 1. Agrupar endpoints en nodos únicos ──────────────────────
    nodos_grafo = []

    def idx_nodo(p):
        px, py = int(p[0]), int(p[1])
        for i, (nx, ny) in enumerate(nodos_grafo):
            if math.hypot(px - nx, py - ny) <= TOLERANCIA:
                return i
        nodos_grafo.append((px, py))
        return len(nodos_grafo) - 1

    # ── 2. Aristas entre nodos de líneas ─────────────────────────
    aristas = {}   # {idx: [(idx_vecino, peso), ...]}
    for linea in caminos_cam:
        if len(linea) != 2:
            continue
        i1 = idx_nodo(linea[0])
        i2 = idx_nodo(linea[1])
        if i1 == i2:
            continue
        p1, p2 = nodos_grafo[i1], nodos_grafo[i2]
        peso = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
        aristas.setdefault(i1, [])
        aristas.setdefault(i2, [])
        if not any(v == i2 for v, _ in aristas[i1]):
            aristas[i1].append((i2, peso))
            aristas[i2].append((i1, peso))

    # ── 3. Inicializar grafo con nodos de caminos + zonas ─────────
    grafo_navegacion = {z: [] for z in zonas_cam.keys()}
    for idx, vecinos in aristas.items():
        grafo_navegacion[f'_n_{idx}'] = [
            (f'_n_{v}', p) for v, p in vecinos
        ]

    # ── 4. Conectar cada zona al nodo de camino más cercano ───────
    for nombre, hb in hitboxes_zonas.items():
        zx, zy = hb['centro']
        mejor_i, mejor_d = None, float('inf')
        for i, (nx, ny) in enumerate(nodos_grafo):
            d = math.hypot(zx - nx, zy - ny)
            if d < mejor_d:
                mejor_d = d
                mejor_i = i
        if mejor_i is not None:
            nn = f'_n_{mejor_i}'
            grafo_navegacion[nombre].append((nn, mejor_d))
            grafo_navegacion.setdefault(nn, [])
            if not any(v == nombre for v, _ in grafo_navegacion[nn]):
                grafo_navegacion[nn].append((nombre, mejor_d))

    n_seg = sum(len(v) for v in aristas.values()) // 2
    print(f"🕸️ Grafo: {len(nodos_grafo)} nodos, {n_seg} segmentos de camino")

def encontrar_ruta_zonas(origen, destino):
    """BFS para encontrar secuencia de zonas desde origen hasta destino"""
    if origen == destino:
        return [origen]
    if origen not in grafo_navegacion or destino not in grafo_navegacion:
        return None

    visitados = {origen}
    cola = deque([(origen, [origen])])

    while cola:
        actual, ruta = cola.popleft()
        for vecino, _ in grafo_navegacion.get(actual, []):
            if vecino == destino:
                return ruta + [vecino]
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, ruta + [vecino]))
    return None


def encontrar_ruta_corta(origen, destino, excluir=None):
    """Dijkstra: ruta mínima ponderada por distancia real en píxeles."""
    if origen == destino:
        return [origen], 0.0
    if origen not in grafo_navegacion or destino not in grafo_navegacion:
        return None, 0.0
    excluir = set(excluir or [])
    dist_map = {origen: 0.0}
    prev_map = {}
    heap = [(0.0, origen)]
    while heap:
        cost, nodo = heapq.heappop(heap)
        if nodo == destino:
            break
        if cost > dist_map.get(nodo, float('inf')):
            continue
        for vecino, _ in grafo_navegacion.get(nodo, []):
            if vecino in excluir:
                continue
            ca = get_pos_nodo(nodo)
            cb = get_pos_nodo(vecino)
            peso = math.hypot(ca[0] - cb[0], ca[1] - cb[1])
            nueva = cost + peso
            if nueva < dist_map.get(vecino, float('inf')):
                dist_map[vecino] = nueva
                prev_map[vecino] = nodo
                heapq.heappush(heap, (nueva, vecino))
    if destino not in prev_map:
        return None, 0.0
    ruta, nodo = [], destino
    while nodo in prev_map:
        ruta.append(nodo)
        nodo = prev_map.get(nodo)
    ruta.append(origen)
    return list(reversed(ruta)), dist_map.get(destino, 0.0)


def _dist_ruta(pts):
    return sum(math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
               for i in range(1, len(pts)))


def obtener_ruta_personalizada(origen, destino):
    """Devuelve (waypoints, distancia) de la ruta más corta entre todas las guardadas."""
    candidatas = []
    for par in [(origen, destino), (destino, origen)]:
        if par not in rutas_personalizadas:
            continue
        for ruta_raw in rutas_personalizadas[par]:
            if par[1] == destino:
                wps = [tuple(p) for p in ruta_raw]
            else:
                wps = [tuple(p) for p in reversed(ruta_raw)]
            dist = _dist_ruta(wps)
            candidatas.append((wps, int(dist)))
    if not candidatas:
        return None, 0
    candidatas.sort(key=lambda x: x[1])
    return candidatas[0]


def todas_rutas_personalizadas(origen, destino):
    """Devuelve lista de (waypoints, distancia, par_key, raw_idx) ordenada por distancia."""
    candidatas = []
    for par in [(origen, destino), (destino, origen)]:
        if par not in rutas_personalizadas:
            continue
        for raw_idx, ruta_raw in enumerate(rutas_personalizadas[par]):
            if par[1] == destino:
                wps = [tuple(p) for p in ruta_raw]
            else:
                wps = [tuple(p) for p in reversed(ruta_raw)]
            candidatas.append((wps, int(_dist_ruta(wps)), par, raw_idx))
    candidatas.sort(key=lambda x: x[1])
    return candidatas


def encontrar_rutas_alternativas(origen, destino):
    """Devuelve hasta 2 rutas [(ruta, dist_px)] ordenadas de menor a mayor distancia."""
    ruta1, dist1 = encontrar_ruta_corta(origen, destino)
    if not ruta1:
        return []
    rutas = [(ruta1, dist1)]
    if len(ruta1) > 2:
        ruta2, dist2 = encontrar_ruta_corta(origen, destino, excluir={ruta1[1]})
        if ruta2 and ruta2 != ruta1:
            rutas.append((ruta2, dist2))
    return rutas

def construir_waypoints(ruta_zonas):
    """Convierte ruta de nodos en lista de puntos (x,y) físicos a seguir."""
    waypoints = []
    for nodo in ruta_zonas:
        pos = get_pos_nodo(nodo)
        if pos != (0, 0) and (not waypoints or waypoints[-1] != pos):
            waypoints.append(pos)
    return waypoints

def esta_en_zona(cx, cy, nombre_zona, margen=0):
    """Verifica si punto (cx,cy) está dentro de la hitbox de una zona"""
    if nombre_zona not in hitboxes_zonas:
        return False
    hb = hitboxes_zonas[nombre_zona]
    # Método 1: Dentro del polígono original
    if nombre_zona in zonas_cam:
        poly = np.array(zonas_cam[nombre_zona], np.int32)
        if cv2.pointPolygonTest(poly, (cx, cy), False) >= 0:
            return True
    # Método 2: Dentro del radio (con margen para "cerca")
    centro = hb['centro']
    radio = hb['radio'] + margen
    dist = math.hypot(cx - centro[0], cy - centro[1])
    return dist <= radio

def obtener_zona_con_hitbox(cx, cy):
    """Obtiene zona actual usando polígono primero, hitbox como fallback"""
    # Primero: polígono exacto
    for nombre, pts in zonas_cam.items():
        if cv2.pointPolygonTest(np.array(pts, np.int32), (cx, cy), False) >= 0:
            return nombre
    # Fallback: hitbox más cercana dentro del radio
    mejor_zona = "Camino"
    mejor_dist = float('inf')
    for nombre, hb in hitboxes_zonas.items():
        dist = math.hypot(cx - hb['centro'][0], cy - hb['centro'][1])
        if dist <= hb['radio'] and dist < mejor_dist:
            mejor_dist = dist
            mejor_zona = nombre
    return mejor_zona

# ==========================================
# 7. FUNCIONES DE NAVEGACIÓN
# ==========================================
def obtener_brujula(dx, dy):
    angulo = math.degrees(math.atan2(-dy, dx))
    if angulo < 0: angulo += 360
    if 45 <= angulo < 135: return "NORTE", angulo
    elif 135 <= angulo < 225: return "OESTE", angulo
    elif 225 <= angulo < 315: return "SUR", angulo
    else: return "ESTE", angulo

def calcular_instruccion_waypoint(pos_x, pos_y, waypoint_x, waypoint_y, rumbo_actual, angulo_actual):
    """Instrucción hacia un waypoint específico (siguiente punto de la ruta)"""
    dir_meta, ang_meta = obtener_brujula(waypoint_x - pos_x, waypoint_y - pos_y)
    dist = math.hypot(waypoint_x - pos_x, waypoint_y - pos_y)
    
    if dist < 25:
        return "PUNTO ALCANZADO", COLOR_OK, dist
    
    if rumbo_actual == "DESCONOCIDO":
        return "Detectando rumbo...", COLOR_WARN, dist
    
    diff = (ang_meta - angulo_actual + 360) % 360
    
    if 150 < diff < 210:
        return "VUELTA EN U", COLOR_ALERT, dist
    elif diff < 15 or diff > 345:
        return "SIGUE DERECHO", COLOR_OK, dist
    elif diff < 180:
        return "GIRA DERECHA", COLOR_WARN, dist
    else:
        return "GIRA IZQUIERDA", COLOR_WARN, dist

def centro_zona(nombre):
    if nombre in hitboxes_zonas:
        return hitboxes_zonas[nombre]['centro']
    return None
# ==========================================
# 8. PANEL DE DIAGNÓSTICO
# ==========================================
def dibujar_panel_diagnostico(img, fps):
    h, w = img.shape[:2]
    pw = 320  # Un poco más ancho para info de waypoints
    overlay = img.copy()
    cv2.rectangle(overlay, (w-pw, 0), (w, h), (15, 15, 25), -1)
    img = cv2.addWeighted(overlay, 0.9, img, 0.1, 0)
    x = w - pw + 10
    y = 22
    
    cv2.putText(img, "DIAGNOSTICO AGV", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_INFO, 2)
    y += 26
    color_fps = COLOR_OK if fps >= 20 else COLOR_WARN if fps >= 10 else COLOR_ERROR
    cv2.putText(img, f"FPS: {fps:.1f}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_fps, 2)
    y += 22
    cv2.putText(img, f"Modo: {estado_sistema['modo_operacion']}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_TEXT, 1)
    y += 20
    
    if estado_agv['detectado']:
        cv2.putText(img, "AGV: OK", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_OK, 2)
        y += 22
        px, py = estado_agv['posicion']
        cv2.putText(img, f"Pos: ({px},{py})", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLOR_TEXT, 1)
        y += 18
        cv2.putText(img, f"Zona: {estado_agv['zona_actual']}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, COLOR_WARN, 2)
        y += 20
        cv2.putText(img, f"Rumbo: {estado_agv['rumbo']}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLOR_TEXT, 1)
        y += 18
        
        # Barra de confianza
        barra_w = 100
        conf = estado_agv['confianza']
        fill = int(barra_w * conf)
        cv2.rectangle(img, (x, y), (x+barra_w, y+8), (50,50,50), -1)
        cv2.rectangle(img, (x, y), (x+fill, y+8), COLOR_OK if conf > 0.7 else COLOR_WARN, -1)
        cv2.putText(img, f"{conf:.0%}", (x+barra_w+5, y+8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_TEXT, 1)
        y += 22
        
        # NUEVO: Info de navegación por waypoints
        if estado_agv['ruta_waypoints']:
            y += 5
            wp_total = len(estado_agv['ruta_waypoints'])
            wp_actual = estado_agv['waypoint_actual'] + 1
            cv2.putText(img, f"Waypoint: {wp_actual}/{wp_total}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_INFO, 1)
            y += 18
            if estado_agv['zona_siguiente']:
                cv2.putText(img, f"Prox: {estado_agv['zona_siguiente']}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLOR_WARN, 1)
                y += 18
    else:
        cv2.putText(img, "AGV: NO DETECTADO", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, COLOR_ERROR, 2)
        y += 22
    
    if estado_sistema['destino']:
        y += 5
        cv2.putText(img, f"A: {estado_sistema['destino']}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_OK, 2)
        y += 22
        cv2.putText(img, estado_agv['instruccion'], (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, estado_agv['color_instruccion'], 2)
    
    # Rutas
    y += 15
    cv2.putText(img, f"Rutas: {len(rutas_guardadas)}/5", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_INFO, 1)
    return img

# ==========================================
# 9. MODO CALIBRAR (INDI)  [sin cambios, se mantiene igual]
# ==========================================
puntos_temp = []
indice_zona_calib = 0
modo_calibracion = "ZONAS"

def clic_calibrador(event, x, y, flags, param):
    global puntos_temp, indice_zona_calib, modo_calibracion, zonas_cam, caminos_cam
    if event == cv2.EVENT_LBUTTONDOWN:
        puntos_temp.append((x, y))
        if modo_calibracion == "ZONAS" and len(puntos_temp) == 4:
            nombre = ZONAS_REQUERIDAS[indice_zona_calib]
            zonas_cam[nombre] = puntos_temp.copy()
            print(f"  ✅ {nombre}")
            puntos_temp = []
            indice_zona_calib += 1
            if indice_zona_calib >= len(ZONAS_REQUERIDAS):
                modo_calibracion = "CAMINOS"
                print("✅ Zonas listas. Caminos (pares). 's'=guardar")
        elif modo_calibracion == "CAMINOS" and len(puntos_temp) == 2:
            caminos_cam.append(puntos_temp.copy())
            print(f"  ✅ Camino agregado")
            puntos_temp = []

def iniciar_calibracion():
    global puntos_temp, indice_zona_calib, modo_calibracion, zonas_cam, caminos_cam
    zonas_cam.clear(); caminos_cam.clear()
    puntos_temp = []; indice_zona_calib = 0; modo_calibracion = "ZONAS"
    estado_sistema['modo'] = 'CALIBRANDO'
    print("\n--- CALIBRACION ---")
    print("Clic 4 esquinas por zona. 's'=guardar 'r'=reiniciar 'q'=cancelar")

def procesar_calibracion(img):
    h, w = img.shape[:2]
    
    # Dibujar zonas ya calibradas con NOMBRES
    for nombre, pts in zonas_cam.items():
        pts_arr = np.array(pts, np.int32).reshape((-1, 1, 2))
        color = obtener_color_zona(nombre)
        cv2.polylines(img, [pts_arr], True, color, 2)
        
        # Centro y nombre corto de zona
        cx = sum(p[0] for p in pts) // len(pts)
        cy = sum(p[1] for p in pts) // len(pts)

        n_corto = nombre_corto(nombre)
        (tw, th), _ = cv2.getTextSize(n_corto, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
        cv2.rectangle(img, (cx - tw//2 - 3, cy - th - 2),
                      (cx + tw//2 + 3, cy + 2), (0, 0, 0), -1)
        cv2.putText(img, n_corto, (cx - tw//2, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1)
    
    # Dibujar caminos
    for linea in caminos_cam:
        cv2.line(img, linea[0], linea[1], (255, 0, 255), 2)
    
    # Puntos temporales
    for i, pt in enumerate(puntos_temp):
        cv2.circle(img, pt, 6, COLOR_ERROR, -1)
        cv2.putText(img, str(i+1), (pt[0]+8, pt[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_ERROR, 1)
    
    # Barra superior
    cv2.rectangle(img, (0, 0), (w, 35), (20, 15, 10), -1)
    if modo_calibracion == "ZONAS":
        zona_act = ZONAS_REQUERIDAS[indice_zona_calib] if indice_zona_calib < len(ZONAS_REQUERIDAS) else "LISTO"
        txt = f"CALIBRAR | {zona_act} | {indice_zona_calib}/{len(ZONAS_REQUERIDAS)} | Clics: {len(puntos_temp)}/4"
    else:
        txt = f"CAMINOS | Clics: {len(puntos_temp)}/2 | Total: {len(caminos_cam)}"
    cv2.putText(img, txt, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_WARN, 2)
    
    # Barra inferior
    cv2.rectangle(img, (0, h-25), (w, h), (20, 15, 10), -1)
    cv2.putText(img, "'s' Guardar | 'r' Reiniciar | 'q' Cancelar", (10, h-8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_TEXT, 1)
    return img

def tecla_calibracion(tecla):
    global puntos_temp, indice_zona_calib, modo_calibracion, zonas_cam, caminos_cam
    if tecla == ord('s'):
        # NUEVO: Reconstruir grafo y hitboxes al guardar
        reconstruir_grafo_navegacion()
        reconstruir_hitboxes()
        guardar_calibracion()
        estado_sistema['modo'] = 'MONITOREO'
        print("✅ Guardado")
        return True
    elif tecla == ord('r'):
        if modo_calibracion == "ZONAS" and len(puntos_temp) > 0:
            puntos_temp = []
        elif modo_calibracion == "ZONAS" and indice_zona_calib > 0:
            indice_zona_calib -= 1
            z = ZONAS_REQUERIDAS[indice_zona_calib]
            if z in zonas_cam: del zonas_cam[z]
        elif modo_calibracion == "CAMINOS" and len(caminos_cam) > 0:
            caminos_cam.pop()
    elif tecla == ord('q'):
        cargar_calibracion()
        estado_sistema['modo'] = 'MONITOREO'
        print("❌ Cancelado")
        return True
    return False

# ==========================================
# 10. MODO MAPA (ROI POLÍGONO)
# ==========================================

def clic_mapa_poligono(event, x, y, flags, param):
    """Click handler para definir el área de pista como polígono."""
    global roi_poligono, roi_cerrado
    if event == cv2.EVENT_LBUTTONDOWN:
        # Clic cerca del primer punto → cerrar polígono
        if len(roi_poligono) >= 3:
            px, py = roi_poligono[0]
            if math.hypot(x - px, y - py) < 14:
                roi_cerrado = True
                estado_sistema['seleccionando_roi'] = False
                guardar_calibracion()
                print(f"✅ Polígono cerrado: {len(roi_poligono)} vértices")
                return
        roi_poligono.append((x, y))
        print(f"  Vértice {len(roi_poligono)}: ({x},{y})")
    elif event == cv2.EVENT_RBUTTONDOWN:
        if roi_poligono:
            roi_poligono.pop()
            print(f"  Deshacer — {len(roi_poligono)} vértices")


def iniciar_mapa():
    global roi_poligono, roi_cerrado
    roi_poligono = []
    roi_cerrado  = False
    estado_sistema['seleccionando_roi'] = True
    print("\n--- MAPA (POLÍGONO) ---")
    print("Clic izq = agregar vértice | Clic en el 1er punto = cerrar | Clic der = deshacer")


def dibujar_roi_seleccion(img):
    h, w = img.shape[:2]
    # Polígono cerrado — dibujar como overlay semitransparente
    if roi_cerrado and len(roi_poligono) >= 3:
        ov = img.copy()
        pts = np.array(roi_poligono, np.int32)
        cv2.fillPoly(ov, [pts], (0, 255, 255))
        img = cv2.addWeighted(ov, 0.18, img, 0.82, 0)
        cv2.polylines(img, [pts], True, COLOR_WARN, 2)
    # Vértices y líneas en curso
    for i, (px, py) in enumerate(roi_poligono):
        cv2.circle(img, (px, py), 6, COLOR_WARN, -1)
        cv2.circle(img, (px, py), 6, (255, 255, 255), 1)
        cv2.putText(img, str(i+1), (px+8, py-4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, COLOR_WARN, 1)
    if len(roi_poligono) >= 2:
        for i in range(1, len(roi_poligono)):
            cv2.line(img, roi_poligono[i-1], roi_poligono[i], COLOR_WARN, 2)
        cv2.line(img, roi_poligono[-1], roi_poligono[0], (80, 80, 80), 1)
    if len(roi_poligono) >= 3:
        cv2.circle(img, roi_poligono[0], 13, COLOR_OK, 2)   # indica punto de cierre

    cv2.rectangle(img, (0, 0), (w, 32), (20, 15, 10), -1)
    cv2.putText(img, "MAPA: clic=vertice | clic1er=cerrar | der=deshacer | s=guardar",
                (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.40, COLOR_WARN, 1)
    return img

# ==========================================
# 11. MODO AJUSTAR RUTAS
# ==========================================

def iniciar_ajustar_rutas():
    global par_ajustando, puntos_ruta_dibujada
    par_ajustando = None
    puntos_ruta_dibujada = []
    estado_sistema['modo'] = 'AJUST_RUTAS'
    estado_sistema['modo_ajust'] = 'SELEC_ORIGEN'
    estado_sistema['ajust_origen']  = None
    estado_sistema['ajust_destino'] = None
    print("\n--- AJUSTAR RUTAS ---")
    print("Clic en zona ORIGEN en la imagen | 'q' para salir")


def clic_ajust_rutas(event, x, y):
    """Maneja clics en el area de video durante el modo Ajustar Rutas."""
    global par_ajustando, puntos_ruta_dibujada
    sub = estado_sistema['modo_ajust']

    if event == cv2.EVENT_LBUTTONDOWN:
        if sub in ('SELEC_ORIGEN', 'SELEC_DESTINO'):
            # Identificar zona clicada
            zona_clic = None
            for nombre, pts in zonas_cam.items():
                if cv2.pointPolygonTest(np.array(pts, np.int32), (x, y), False) >= 0:
                    zona_clic = nombre
                    break
            if zona_clic:
                if sub == 'SELEC_ORIGEN':
                    estado_sistema['ajust_origen']  = zona_clic
                    estado_sistema['modo_ajust'] = 'SELEC_DESTINO'
                    print(f"  Origen: {nombre_corto(zona_clic)} → ahora clic en DESTINO")
                else:
                    estado_sistema['ajust_destino'] = zona_clic
                    par_ajustando = (estado_sistema['ajust_origen'],
                                     estado_sistema['ajust_destino'])
                    puntos_ruta_dibujada = []
                    estado_sistema['modo_ajust'] = 'DIBUJANDO'
                    print(f"  Destino: {nombre_corto(zona_clic)}")
                    print(f"  Dibuja la ruta. 's'=guardar 'r'=borrar 'n'=nueva pareja 'q'=salir")
        elif sub == 'DIBUJANDO':
            puntos_ruta_dibujada.append((x, y))

    elif event == cv2.EVENT_RBUTTONDOWN and sub == 'DIBUJANDO':
        if puntos_ruta_dibujada:
            puntos_ruta_dibujada.pop()


def tecla_ajust_rutas(k):
    """Procesa teclas en modo Ajustar Rutas. Devuelve True si se debe salir."""
    global puntos_ruta_dibujada, par_ajustando
    if k == ord('s') and par_ajustando and len(puntos_ruta_dibujada) >= 2:
        if par_ajustando not in rutas_personalizadas:
            rutas_personalizadas[par_ajustando] = []
        rutas_personalizadas[par_ajustando].append(
            [[p[0],p[1]] for p in puntos_ruta_dibujada]
        )
        guardar_rutas_personalizadas()
        n = len(rutas_personalizadas[par_ajustando])
        notif(f"Ruta {n} guardada: {nombre_corto(par_ajustando[0])}->{nombre_corto(par_ajustando[1])}", (0,220,120))
        par_ajustando = None
        puntos_ruta_dibujada = []
        estado_sistema['modo_ajust'] = 'SELEC_ORIGEN'
        estado_sistema['ajust_origen'] = estado_sistema['ajust_destino'] = None
    elif k == ord('r'):
        puntos_ruta_dibujada = []
        print("  Trazo borrado — vuelve a dibujar")
    elif k == ord('n'):
        par_ajustando = None
        puntos_ruta_dibujada = []
        estado_sistema['modo_ajust'] = 'SELEC_ORIGEN'
        estado_sistema['ajust_origen'] = estado_sistema['ajust_destino'] = None
        print("  Nueva pareja — clic en ORIGEN")
    elif k == ord('q') or k == 27:
        estado_sistema['modo'] = 'MONITOREO'
        estado_sistema['modo_ajust'] = 'IDLE'
        par_ajustando = None
        puntos_ruta_dibujada = []
        print("  Ajustar Rutas cerrado")
        return True
    return False


def dibujar_ajust_rutas(img):
    """Overlay del modo Ajustar Rutas sobre el frame."""
    h, w = img.shape[:2]
    sub = estado_sistema['modo_ajust']

    # ── Dibujar zonas calibradas ──────────────────────────────
    for nombre, pts in zonas_cam.items():
        pts_arr = np.array(pts, np.int32).reshape((-1,1,2))
        es_origen  = (nombre == estado_sistema['ajust_origen'])
        es_destino = (nombre == estado_sistema['ajust_destino'])
        color = (0,255,0) if es_origen else (0,100,255) if es_destino else obtener_color_zona(nombre)
        grosor = 3 if (es_origen or es_destino) else 1
        cv2.polylines(img, [pts_arr], True, color, grosor)
        cx = sum(p[0] for p in pts)//len(pts)
        cy = sum(p[1] for p in pts)//len(pts)
        n_corto = nombre_corto(nombre)
        (tw, th), _ = cv2.getTextSize(n_corto, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
        cv2.rectangle(img, (cx-tw//2-3, cy-th-3), (cx+tw//2+3, cy+3), (0,0,0), -1)
        cv2.putText(img, n_corto, (cx-tw//2, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)

    # ── Dibujar caminos como referencia ──────────────────────
    for linea in caminos_cam:
        if len(linea) == 2:
            cv2.line(img, tuple(linea[0]), tuple(linea[1]), (60, 60, 60), 2)

    # ── Rutas personalizadas ya guardadas ─────────────────────
    # rutas_personalizadas = {(ori,dest): [ [ruta1_pts], [ruta2_pts], ... ]}
    for (ori, dest), rutas_lista in rutas_personalizadas.items():
        for r_idx, pts in enumerate(rutas_lista):
            if len(pts) < 2:
                continue
            col_r = COLORES_VIS[r_idx % len(COLORES_VIS)]
            for i in range(len(pts)-1):
                cv2.line(img, tuple(pts[i]), tuple(pts[i+1]), col_r, 2)
            cv2.circle(img, tuple(pts[0]),  5, col_r, -1)
            cv2.circle(img, tuple(pts[-1]), 5, col_r, -1)
            mid = pts[len(pts)//2]
            n = len(rutas_lista)
            etq = f"{nombre_corto(ori)}->{nombre_corto(dest)}" + (f" R{r_idx+1}" if n > 1 else "")
            cv2.putText(img, etq, (int(mid[0])+5, int(mid[1])-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.32, col_r, 1)

    # ── Trazo actual en dibujo ────────────────────────────────
    if puntos_ruta_dibujada:
        for i in range(1, len(puntos_ruta_dibujada)):
            cv2.line(img, puntos_ruta_dibujada[i-1], puntos_ruta_dibujada[i], (0,255,255), 2)
        for p in puntos_ruta_dibujada:
            cv2.circle(img, p, 4, (0,255,255), -1)
        cv2.circle(img, puntos_ruta_dibujada[0],  7, (0,200,0),   2)
        cv2.circle(img, puntos_ruta_dibujada[-1], 7, (0,100,255), 2)

    # ── Barra de instrucciones ───────────────────────────────
    if sub == 'SELEC_ORIGEN':
        msg = "Clic en zona ORIGEN (sidebar o imagen)"
    elif sub == 'SELEC_DESTINO':
        org = nombre_corto(estado_sistema.get('ajust_origen') or '')
        msg = f"Origen: {org}  —  clic en zona DESTINO"
    elif sub == 'DIBUJANDO' and par_ajustando:
        msg = f"{nombre_corto(par_ajustando[0])}->{nombre_corto(par_ajustando[1])}  |  s=guardar  r=borrar  n=nueva  q=salir"
    else:
        msg = "q=salir"
    cv2.rectangle(img, (0, h-30), (w, h), (15,15,20), -1)
    cv2.putText(img, msg, (5, h-9), cv2.FONT_HERSHEY_SIMPLEX, 0.38, COLOR_WARN, 1)
    return img


# ==========================================
# 11B. VER RUTAS
# ==========================================

COLORES_VIS = [
    (0, 240, 240),   # Cyan  — más corta
    (0, 130, 255),   # Naranja
    (255, 0, 220),   # Magenta
    (0, 255, 80),    # Verde
    (255, 240, 0),   # Amarillo
    (180, 0, 255),   # Violeta
]


def dibujar_ver_rutas(img):
    """Overlay del modo Ver Rutas sobre el frame."""
    h, w = img.shape[:2]
    orig = estado_sistema.get('ver_rutas_origen')
    dest = estado_sistema.get('ver_rutas_destino')

    # Zonas de referencia (contorno tenue)
    for nombre, pts in zonas_cam.items():
        pts_arr = np.array(pts, np.int32).reshape((-1,1,2))
        es_sel = nombre in (orig, dest)
        col = obtener_color_zona(nombre) if es_sel else (50,55,70)
        grosor = 2 if es_sel else 1
        cv2.polylines(img, [pts_arr], True, col, grosor)
        cx = sum(p[0] for p in pts)//len(pts)
        cy = sum(p[1] for p in pts)//len(pts)
        n_c = nombre_corto(nombre)
        (tw,th),_ = cv2.getTextSize(n_c, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1)
        cv2.rectangle(img,(cx-tw//2-2,cy-th-2),(cx+tw//2+2,cy+2),(0,0,0),-1)
        cv2.putText(img, n_c, (cx-tw//2, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.34, col, 1)

    # Caminos de referencia
    for linea in caminos_cam:
        if len(linea)==2:
            cv2.line(img, tuple(linea[0]), tuple(linea[1]), (40,42,55), 1)

    if orig and dest:
        rutas = todas_rutas_personalizadas(orig, dest)
        if rutas:
            # Dibujar de mayor a menor para que la más corta quede encima
            for i, (pts, dist, *_) in enumerate(reversed(rutas)):
                idx = len(rutas)-1-i
                col = COLORES_VIS[idx % len(COLORES_VIS)]
                grosor = 3 if idx == 0 else 2
                for j in range(1, len(pts)):
                    cv2.line(img, pts[j-1], pts[j], col, grosor)
                cv2.circle(img, pts[0],  7, col, -1)
                cv2.circle(img, pts[-1], 7, col, -1)
                mid = pts[len(pts)//2]
                tag = f"R{idx+1}: {dist}px" + (" (MENOR)" if idx==0 else "")
                cv2.putText(img, tag, (mid[0]+6, mid[1]-6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.36, col, 1)
        else:
            cv2.putText(img, f"Sin rutas guardadas: {nombre_corto(orig)}->{nombre_corto(dest)}",
                        (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,100,200), 1)

    # Barra inferior
    cv2.rectangle(img,(0,h-28),(w,h),(12,14,20),-1)
    if orig and dest:
        n_rutas = len(todas_rutas_personalizadas(orig,dest))
        msg = f"{nombre_corto(orig)} -> {nombre_corto(dest)}  |  {n_rutas} ruta(s)  |  q=salir"
    elif orig:
        msg = f"Origen: {nombre_corto(orig)}  —  elige DESTINO en el sidebar"
    else:
        msg = "Elige ORIGEN en el sidebar"
    cv2.putText(img, msg, (5,h-8), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (130,150,200), 1)
    return img


def _sidebar_ver_rutas(panel, y, btn_rects, W=SIDEBAR_W):
    """Sidebar exclusivo del modo Ver Rutas."""
    orig = estado_sistema.get('ver_rutas_origen')
    dest = estado_sistema.get('ver_rutas_destino')

    todas_zonas = (['Zona Despacho','Zona Pits','Recepcion','Banda'] +
                   [f'Almacen_A{i}' for i in range(1,6)] +
                   [f'Almacen_B{i}' for i in range(1,6)])

    def zona_grid(prefix, selected, W=W):
        nonlocal y
        bw = (W-12)//4
        y0 = y
        for idx, z in enumerate(todas_zonas):
            ci = idx % 4;  ri = idx // 4
            x1 = 6+ci*bw; x2 = x1+bw-2
            y1 = y0+ri*23; y2 = y1+21
            act = (selected == z)
            cb = (38,85,38) if (act and 'or' in prefix) else \
                 (25,40,90) if (act and 'de' in prefix) else \
                 (22,28,40)
            cv2.rectangle(panel,(x1,y1),(x2,y2),cb,-1)
            cv2.rectangle(panel,(x1,y1),(x2,y2),(52,58,75),1)
            if act:
                col_ac = (0,220,120) if 'or' in prefix else (0,130,255)
                cv2.rectangle(panel,(x1,y1),(x1+2,y2),col_ac,-1)
            etq = nombre_corto(z)[:4]
            (tw,th),_ = cv2.getTextSize(etq,cv2.FONT_HERSHEY_SIMPLEX,0.30,1)
            cv2.putText(panel,etq,(x1+(bw-2-tw)//2,y1+(21+th)//2),
                        cv2.FONT_HERSHEY_SIMPLEX,0.30,(200,208,218),1)
            btn_rects[f'{prefix}{z}'] = (x1,y1,x2,y2)
        y = y0 + (len(todas_zonas)+3)//4 * 23 + 4

    y = _sec(panel,"  DESDE (ORIGEN)",y,W)
    zona_grid('vor_', orig)

    y = _sec(panel,"  HASTA (DESTINO)",y,W)
    zona_grid('vde_', dest)

    # Leyenda de colores + botón X por ruta
    if orig and dest:
        rutas = todas_rutas_personalizadas(orig, dest)
        y = _sec(panel,f"  {len(rutas)} RUTA(S)  (X = eliminar)",y,W)
        for i, ruta_item in enumerate(rutas):
            dist = ruta_item[1]
            col = COLORES_VIS[i % len(COLORES_VIS)]
            # Fondo tenue para la fila
            cv2.rectangle(panel,(6,y),(W-6,y+19),(20,22,32),-1)
            cv2.circle(panel,(14,y+9),5,col,-1)
            tag = f"R{i+1}: {dist}px" + (" MENOR" if i==0 else "")
            cv2.putText(panel,tag,(24,y+13),cv2.FONT_HERSHEY_SIMPLEX,0.31,col,1)
            # Botón X — parte derecha de la fila
            xb1,yb1,xb2,yb2 = W-22,y+2,W-6,y+17
            cv2.rectangle(panel,(xb1,yb1),(xb2,yb2),(90,20,20),-1)
            cv2.rectangle(panel,(xb1,yb1),(xb2,yb2),(140,40,40),1)
            cv2.putText(panel,"X",(xb1+3,yb1+11),cv2.FONT_HERSHEY_SIMPLEX,0.32,(255,120,120),1)
            btn_rects[f'del_ruta_{i}'] = (xb1,yb1,xb2,yb2)
            y+=21
        y+=3

    y = _btn(panel,'ver_rutas_salir','SALIR VER RUTAS',btn_rects,y,(60,18,18),False,24,W)
    return y


# ==========================================
# 12. PROCESAR FRAME PRINCIPAL (INDI) - MEJORADO
# ==========================================
def procesar_frame_indi(img):
    global frames_contados, ultimo_fps_time, fps_actual
    ahora = time.time()
    frames_contados += 1
    if ahora - ultimo_fps_time >= 1.0:
        fps_actual = frames_contados
        frames_contados = 0
        ultimo_fps_time = ahora
    h, w = img.shape[:2]
    img_limpia = img.copy()

    # Grilla
    for x in range(0, w, 100):
        cv2.line(img, (x, 0), (x, h), COLOR_GRID, 1)
    for y in range(0, h, 100):
        cv2.line(img, (0, y), (w, y), COLOR_GRID, 1)
    
    # ROI: polígono tiene prioridad sobre rectángulo legacy
    if roi_cerrado and len(roi_poligono) >= 3:
        pts_roi = np.array(roi_poligono, np.int32)
        ov_roi = img.copy()
        cv2.fillPoly(ov_roi, [pts_roi], (0, 210, 210))
        img = cv2.addWeighted(ov_roi, 0.08, img, 0.92, 0)
        cv2.polylines(img, [pts_roi], True, COLOR_WARN, 2)
    elif roi_pista is not None and not estado_sistema['seleccionando_roi']:
        rx, ry, rw, rh = roi_pista
        cv2.rectangle(img, (rx, ry), (rx+rw, ry+rh), COLOR_WARN, 2)
    
    # ==========================================
    # ZONAS CON NOMBRES Y HITBOXES VISIBLES
    # ==========================================
    for nombre, pts in zonas_cam.items():
        pts_arr = np.array(pts, np.int32).reshape((-1, 1, 2))
        es_destino = (nombre == estado_sistema['destino'])
        color = obtener_color_zona(nombre)
        grosor = 3 if es_destino else 2
        cv2.polylines(img, [pts_arr], True, color, grosor)
        
        # NUEVO: Calcular centroide real del polígono
        cx = sum(p[0] for p in pts) // len(pts)
        cy = sum(p[1] for p in pts) // len(pts)
        
        # NUEVO: Dibujar hitbox visual (círculo)
        if nombre in hitboxes_zonas:
            radio = hitboxes_zonas[nombre]['radio']
            # Círculo punteado o sólido según si es destino
            if es_destino:
                cv2.circle(img, (cx, cy), radio, color, 2)
                cv2.circle(img, (cx, cy), 4, COLOR_ERROR, -1)  # Centro
            else:
                cv2.circle(img, (cx, cy), radio, color, 1)
        
        # Dibujar nombre corto de zona con fondo
        n_corto = nombre_corto(nombre)
        (tw, th), _ = cv2.getTextSize(n_corto, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
        cv2.rectangle(img, (cx - tw//2 - 3, cy - th - 3),
                      (cx + tw//2 + 3, cy + 3), (0, 0, 0), -1)
        cv2.putText(img, n_corto, (cx - tw//2, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1)
        
        # Si es destino, resaltar más
        if es_destino:
            cv2.circle(img, (cx, cy), 8, COLOR_OK, 2)
            cv2.putText(img, "DESTINO", (cx - 25, cy - 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_OK, 2)
    
    # ==========================================
    # CAMINOS CON COLORES Y GROSOR
    # ==========================================
    for i, linea in enumerate(caminos_cam):
        if len(linea) == 2:
            # Color según si es parte de la ruta activa
            color_camino = (80, 80, 80)  # Gris por defecto
            grosor_camino = 1
            
            # Si hay navegación activa, resaltar caminos de la ruta
            if estado_sistema['destino'] and estado_agv['ruta_waypoints']:
                # Verificar si este camino conecta zonas de la ruta
                # (simplificado: resaltar todos durante navegación)
                color_camino = (0, 150, 255)  # Naranja
                grosor_camino = 2
            
            cv2.line(img, linea[0], linea[1], color_camino, grosor_camino)
            
            # NUEVO: Punto medio del camino como waypoint visual
            mx = (linea[0][0] + linea[1][0]) // 2
            my = (linea[0][1] + linea[1][1]) // 2
            cv2.circle(img, (mx, my), 3, (100, 100, 100), -1)
    
    # Dibujar rutas guardadas (últimos 5 caminos)
    dibujar_rutas(img)
    
    # ==========================================
    # NODOS FÍSICOS DEL GRAFO (puntos de caminos)
    # ==========================================
    for i, (nx, ny) in enumerate(nodos_grafo):
        cv2.circle(img, (nx, ny), 3, (40, 40, 80), -1)

    # ==========================================
    # RUTA ALTERNATIVA (gris, solo referencia)
    # ==========================================
    if estado_agv['ruta_alt_waypoints'] and estado_sistema['destino']:
        alt = estado_agv['ruta_alt_waypoints']
        for i in range(len(alt) - 1):
            cv2.line(img, alt[i], alt[i + 1], (70, 70, 110), 1)
        if estado_agv['dist_ruta_alt']:
            mid = alt[len(alt) // 2]
            cv2.putText(img, f"Alt:{estado_agv['dist_ruta_alt']}px",
                        (mid[0] + 5, mid[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 170), 1)

    # ==========================================
    # WAYPOINTS VISUALES (ruta activa)
    # ==========================================
    if estado_agv['ruta_waypoints'] and estado_sistema['destino']:
        waypoints = estado_agv['ruta_waypoints']
        wp_idx = estado_agv['waypoint_actual']
        
        # Dibujar línea de ruta completa
        if len(waypoints) >= 2:
            for i in range(len(waypoints) - 1):
                wp1 = waypoints[i]
                wp2 = waypoints[i + 1]
                # Waypoints ya pasados: gris, actual y futuros: amarillo
                if i < wp_idx:
                    cv2.line(img, wp1, wp2, (80, 80, 80), 1)
                else:
                    cv2.line(img, wp1, wp2, (255, 255, 0), 2)
            # Etiqueta de distancia sobre el punto medio
            if estado_agv['dist_ruta']:
                mid = waypoints[len(waypoints) // 2]
                cv2.putText(img, f"Ruta:{estado_agv['dist_ruta']}px",
                            (mid[0] + 5, mid[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 0), 1)
        
        # Dibujar waypoints
        for i, wp in enumerate(waypoints):
            if i < wp_idx:
                # Ya pasado
                cv2.circle(img, wp, 4, (80, 80, 80), -1)
            elif i == wp_idx:
                # Actual - resaltar
                cv2.circle(img, wp, 8, (0, 255, 255), 2)
                cv2.circle(img, wp, 4, (0, 255, 255), -1)
                cv2.putText(img, f"WP{i+1}", (wp[0]+10, wp[1]), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
            else:
                # Futuro
                cv2.circle(img, wp, 4, (0, 150, 255), -1)
                cv2.putText(img, f"WP{i+1}", (wp[0]+10, wp[1]), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.30, (0, 150, 255), 1)
    
    # ==========================================
    # DETECCIÓN YOLO
    # ==========================================
    resultados = model(img_limpia, verbose=False)
    agv_detectado = False
    
    for r in resultados:
        for caja in r.boxes:
            cx1, cy1, cx2, cy2 = map(int, caja.xyxy[0])
            conf = float(caja.conf[0])

            # Filtro de confianza
            if conf < 0.45:
                continue
            # Filtro de tamaño: descarta objetos demasiado grandes (ej. banda)
            area_bb = (cx2 - cx1) * (cy2 - cy1)
            if area_bb < 400 or area_bb > h * w * 0.28:
                continue
            # Filtro de color: el AGV es azul oscuro, la banda es negra
            if not tiene_color_agv(img_limpia, cx1, cy1, cx2, cy2):
                continue

            cx = (cx1 + cx2) // 2
            cy = (cy1 + cy2) // 2

            # Filtro ROI: polígono tiene prioridad sobre rectángulo legacy
            if roi_cerrado and len(roi_poligono) >= 3:
                poly_roi = np.array(roi_poligono, np.int32)
                if cv2.pointPolygonTest(poly_roi, (cx, cy), False) < 0:
                    continue
            elif roi_pista is not None and not estado_sistema['seleccionando_roi']:
                rx, ry, rw, rh = roi_pista
                if not (rx <= cx <= rx+rw and ry <= cy <= ry+rh):
                    continue
            
            agv_detectado = True
            estado_agv['detectado'] = True
            estado_agv['posicion'] = (cx, cy)
            estado_agv['confianza'] = conf
            estado_agv['bbox'] = (cx1, cy1, cx2, cy2)
            estado_agv['frames_perdido'] = 0
            estado_agv['trayectoria'].append((cx, cy))
            estado_agv['historial'].append((cx, cy))
            
            # Guardar punto en ruta actual
            agregar_punto_ruta((cx, cy))
            
            if len(estado_agv['historial']) >= 2:
                p1 = list(estado_agv['historial'])[-2]
                p2 = list(estado_agv['historial'])[-1]
                estado_agv['velocidad'] = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
            
            # NUEVO: Obtener zona usando hitbox mejorado
            zona = obtener_zona_con_hitbox(cx, cy)
            estado_agv['zona_actual'] = zona
            if zona != "Camino" and zona != estado_agv['zona_previa']:
                notif(f"Zona: {nombre_corto(zona)}", (0,195,232))
                estado_agv['zona_previa'] = zona
            
            if len(estado_agv['historial']) >= 5:
                p_ant = list(estado_agv['historial'])[0]
                rumbo, angulo = obtener_brujula(cx - p_ant[0], cy - p_ant[1])
                estado_agv['rumbo'] = rumbo
                estado_agv['rumbo_grados'] = angulo
            
            # ==========================================
            # NAVEGACIÓN POR WAYPOINTS (usando caminos)
            # ==========================================
            if estado_sistema['destino']:
                destino = estado_sistema['destino']
                
                # Verificar si llegó al destino (hitbox con margen de 20px)
                if esta_en_zona(cx, cy, destino, margen=20):
                    if not estado_agv['llegada']:
                        estado_agv['llegada'] = True
                        print(f"\n🎯 ¡LLEGADA A {destino.upper()}!")
                        notif(f"LLEGADA: {nombre_corto(destino)}", (0,230,100))
                        estado_agv['ruta_waypoints'] = []
                        estado_agv['ruta_alt_waypoints'] = []
                        estado_agv['waypoint_actual'] = 0
                        estado_agv['zona_siguiente'] = None
                        estado_agv['dist_ruta'] = 0
                        estado_agv['dist_ruta_alt'] = 0
                        guardar_rutas()
                    estado_agv['instruccion'] = "LLEGADA ✓"
                    estado_agv['color_instruccion'] = COLOR_OK
                
                elif estado_agv['ruta_waypoints']:
                    # Seguir waypoints
                    wp_idx = estado_agv['waypoint_actual']
                    waypoints = estado_agv['ruta_waypoints']
                    
                    if wp_idx < len(waypoints):
                        wp_actual = waypoints[wp_idx]
                        dist_wp = math.hypot(cx - wp_actual[0], cy - wp_actual[1])
                        
                        # ¿Llegó al waypoint actual?
                        if dist_wp < 30:
                            estado_agv['waypoint_actual'] += 1
                            print(f"  ✅ Waypoint {wp_idx+1} alcanzado")
                            if estado_agv['waypoint_actual'] < len(waypoints):
                                wp_sig = waypoints[estado_agv['waypoint_actual']]
                                # Actualizar zona siguiente
                                for nombre, hb in hitboxes_zonas.items():
                                    if math.hypot(wp_sig[0]-hb['centro'][0], 
                                                  wp_sig[1]-hb['centro'][1]) < hb['radio']:
                                        estado_agv['zona_siguiente'] = nombre
                                        break
                        
                        # Calcular instrucción hacia waypoint actual
                        wp_target = waypoints[min(wp_idx, len(waypoints)-1)]
                        estado_agv['llegada'] = False
                        instruccion, color_inst, dist = calcular_instruccion_waypoint(
                            cx, cy, wp_target[0], wp_target[1],
                            estado_agv['rumbo'], estado_agv['rumbo_grados']
                        )
                        estado_agv['instruccion'] = f"{instruccion} ({dist:.0f}px)"
                        estado_agv['color_instruccion'] = color_inst
                        
                        # Línea visual al waypoint actual
                        cv2.line(img, (cx, cy), wp_target, (0, 255, 255), 2)
                        
                        # Línea punteada al destino final
                        if destino in hitboxes_zonas:
                            centro_dest = hitboxes_zonas[destino]['centro']
                            cv2.line(img, wp_target, centro_dest, (0, 100, 200), 1)
                    
                    else:
                        # Todos los waypoints completados, ir directo al destino
                        meta = centro_zona(destino)
                        if meta:
                            estado_agv['llegada'] = False
                            instruccion, color_inst, dist = calcular_instruccion_waypoint(
                                cx, cy, meta[0], meta[1],
                                estado_agv['rumbo'], estado_agv['rumbo_grados']
                            )
                            estado_agv['instruccion'] = f"{instruccion} → DESTINO ({dist:.0f}px)"
                            estado_agv['color_instruccion'] = color_inst
                            cv2.line(img, (cx, cy), meta, (255, 150, 0), 2)
                
                else:
                    # Sin waypoints, ir directo (fallback)
                    meta = centro_zona(destino)
                    if meta:    
                        instruccion, color_inst, dist = calcular_instruccion_waypoint(
                            cx, cy, meta[0], meta[1],
                            estado_agv['rumbo'], estado_agv['rumbo_grados']
                        )
                        estado_agv['instruccion'] = f"{instruccion} → DESTINO ({dist:.0f}px)"
                        estado_agv['color_instruccion'] = color_inst
                        cv2.line(img, (cx, cy), meta, (255, 150, 0), 1)
            
            # ==========================================
            # DIBUJAR AGV
            # ==========================================
            cv2.circle(img, (cx, cy), 12, (200, 200, 255), -1)
            cv2.circle(img, (cx, cy), 12, (80, 80, 180), 2)
            cv2.circle(img, (cx, cy), 4, COLOR_ERROR, -1)
            
            if estado_agv['rumbo'] != "DESCONOCIDO":
                fx = int(cx + 20 * math.cos(math.radians(estado_agv['rumbo_grados'])))
                fy = int(cy - 20 * math.sin(math.radians(estado_agv['rumbo_grados'])))
                cv2.arrowedLine(img, (cx, cy), (fx, fy), COLOR_ERROR, 2, tipLength=0.3)
            
            cv2.putText(img, f"AGV {conf:.0%}", (cx1, cy1-6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_OK, 1)
            break  # Solo primer AGV
    
    if not agv_detectado:
        estado_agv['detectado'] = False
        estado_agv['frames_perdido'] += 1
        estado_agv['velocidad'] = 0
    
    # ==========================================
    # BARRA SUPERIOR DE ESTADO
    # ==========================================
    cv2.rectangle(img, (0, 0), (w, 22), (15, 15, 20), -1)
    status = f"[{estado_sistema['modo_operacion']}] AGV: {'OK' if estado_agv['detectado'] else 'PERDIDO'}"
    if estado_agv['detectado']:
        status += f" | {estado_agv['zona_actual']} | {estado_agv['rumbo']}"
    if estado_sistema['destino']:
        wp_info = ""
        if estado_agv['ruta_waypoints']:
            wp_info = f" | WP{estado_agv['waypoint_actual']+1}/{len(estado_agv['ruta_waypoints'])}"
        status += f" | → {estado_sistema['destino']}{wp_info}"
    color_status = COLOR_OK if estado_agv['detectado'] else COLOR_ERROR
    cv2.putText(img, status, (8, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color_status, 1)
    
    # Panel diagnóstico SOLO si se activa
    if estado_sistema['mostrar_diagnostico']:
        img = dibujar_panel_diagnostico(img, fps_actual)

    dibujar_notificaciones(img)
    return img
# ==========================================
# 12. MODO MULTI (basado en prueba_3.py)
# ==========================================
WARP_W, WARP_H = 640, 480
CENTRAL_Y = 240
GROSOR = 14
ACCESO_W = 60

M_warp = None
M_inv = None
puntos_cal_multi = []
calibrado_multi = False
modo_ajuste_multi = False
idx_zona_multi = 0
PASO_AJUSTE = 5

zonas_almacenes = {}
zonas_externas = {}
caminos_multi = {}
zonas_plano = {}

def zonas_por_defecto_multi():
    _ax1 = ACCESO_W
    _ax2 = WARP_W
    _cw = (_ax2 - _ax1) // 5
    cols = [(int(_ax1+i*_cw), int(_ax1+(i+1)*_cw)) for i in range(5)]
    alm = {}
    for i, (cx1, cx2) in enumerate(cols, start=1):
        alm[f"A{i}"] = [cx1, GROSOR, cx2, CENTRAL_Y - GROSOR//2]
        alm[f"B{i}"] = [cx1, CENTRAL_Y + GROSOR//2, cx2, WARP_H - GROSOR]
    ext = {
        "Pits": [ACCESO_W, -90, WARP_W//2, -10],
        "Despacho": [WARP_W//2, -90, WARP_W, -10],
        "Recepcion": [-110, GROSOR, -10, WARP_H//2],
        "Banda": [-110, WARP_H//2, -10, WARP_H],
    }
    cam = {
        "sup": [0, 0, WARP_W, GROSOR],
        "inf": [0, WARP_H-GROSOR, WARP_W, WARP_H],
        "izq": [0, 0, GROSOR+ACCESO_W, WARP_H],
        "der": [WARP_W-GROSOR, 0, WARP_W, WARP_H],
        "central": [ACCESO_W, CENTRAL_Y-GROSOR//2, WARP_W, CENTRAL_Y+GROSOR//2],
    }
    return alm, ext, cam

def color_zona_multi(n):
    if n == "Pits": return (0, 140, 255)       # Amarillo oscuro
    if n == "Despacho": return (0, 255, 127)   # Verde claro fosforescente
    if n == "Recepcion": return (255, 100, 0)  # Azul
    if n == "Banda": return (255, 0, 255)      # Morado
    if n.startswith("A"): return (0, 255, 255)  # Amarillo (cyan BGR)
    if n.startswith("B"): return (0, 100, 0)    # Verde oscuro
    return (160, 160, 160)

def cargar_zonas_multi():
    global zonas_almacenes, zonas_externas, caminos_multi, zonas_plano
    if not os.path.exists(zones_path):
        zonas_almacenes, zonas_externas, caminos_multi = zonas_por_defecto_multi()
    else:
        try:
            with open(zones_path) as f:
                data = json.load(f)
            zonas_almacenes = data["almacenes"]
            zonas_externas = data["externas"]
            caminos_multi = data["caminos"]
        except:
            zonas_almacenes, zonas_externas, caminos_multi = zonas_por_defecto_multi()
    zonas_plano = {**zonas_externas, **zonas_almacenes}

def guardar_zonas_multi():
    with open(zones_path, "w") as f:
        json.dump({
            "almacenes": zonas_almacenes,
            "externas": zonas_externas,
            "caminos": caminos_multi
        }, f, indent=2)
    print("Zonas guardadas")

def cargar_calibracion_multi():
    global M_warp, M_inv, calibrado_multi
    if not os.path.exists(cal_path):
        return False
    try:
        with open(cal_path) as f:
            data = json.load(f)
        src = np.float32(data["src"])
        dst = np.float32([[0,0],[WARP_W,0],[WARP_W,WARP_H],[0,WARP_H]])
        M_warp = cv2.getPerspectiveTransform(src, dst)
        M_inv = cv2.getPerspectiveTransform(dst, src)
        calibrado_multi = True
        print("Calibración multi cargada")
        return True
    except:
        return False

def guardar_calibracion_multi(pts):
    global M_warp, M_inv, calibrado_multi
    src = np.float32(pts)
    dst = np.float32([[0,0],[WARP_W,0],[WARP_W,WARP_H],[0,WARP_H]])
    M_warp = cv2.getPerspectiveTransform(src, dst)
    M_inv = cv2.getPerspectiveTransform(dst, src)
    calibrado_multi = True
    with open(cal_path, "w") as f:
        json.dump({"src": [list(map(float,p)) for p in pts]}, f)
    print("Calibración multi guardada")

def warp_pt_a_frame(px, py):
    r = cv2.perspectiveTransform(np.float32([[[px,py]]]), M_inv)
    return int(r[0][0][0]), int(r[0][0][1])

def proyectar_rect(x1, y1, x2, y2):
    return cv2.perspectiveTransform(
        np.float32([[[x1,y1],[x2,y1],[x2,y2],[x1,y2]]]), M_inv)[0].astype(int)

def mouse_cb_multi(event, x, y, flags, param):
    global puntos_cal_multi
    if event == cv2.EVENT_LBUTTONDOWN and not calibrado_multi:
        if len(puntos_cal_multi) < 4:
            puntos_cal_multi.append([x, y])
            print(f"  Punto {len(puntos_cal_multi)}: ({x},{y})")
            if len(puntos_cal_multi) == 4:
                guardar_calibracion_multi(puntos_cal_multi[:])

def nombre_zona_actual_multi():
    nombres = list(zonas_plano.keys())
    return nombres[idx_zona_multi % len(nombres)]

def ajustar_zona_multi(nombre, dx1, dy1, dx2, dy2):
    z = zonas_plano[nombre]
    nueva = [z[0]+dx1, z[1]+dy1, z[2]+dx2, z[3]+dy2]
    zonas_plano[nombre] = nueva
    if nombre in zonas_almacenes:
        zonas_almacenes[nombre] = nueva
    elif nombre in zonas_externas:
        zonas_externas[nombre] = nueva

def manejar_tecla_ajuste_multi(k):
    global idx_zona_multi
    n = nombre_zona_actual_multi()
    p = PASO_AJUSTE
    if k == 9: idx_zona_multi += 1; return
    if k == ord('z'): idx_zona_multi -= 1; return
    if k == 82: ajustar_zona_multi(n, 0, -p, 0, -p)
    elif k == 84: ajustar_zona_multi(n, 0, p, 0, p)
    elif k == 81: ajustar_zona_multi(n, -p, 0, -p, 0)
    elif k == 83: ajustar_zona_multi(n, p, 0, p, 0)
    elif k == ord('+'): ajustar_zona_multi(n, -p, -p, p, p)
    elif k == ord('-'): ajustar_zona_multi(n, p, p, -p, -p)
    elif k == ord('w'): ajustar_zona_multi(n, 0, -p, 0, 0)
    elif k == ord('s'): ajustar_zona_multi(n, 0, p, 0, 0)
    elif k == ord('a'): ajustar_zona_multi(n, -p, 0, 0, 0)
    elif k == ord('d'): ajustar_zona_multi(n, p, 0, 0, 0)
    elif k == ord(' '): guardar_zonas_multi()

def dibujar_overlay_multi(frame):
    overlay = frame.copy()
    for nombre, z in zonas_plano.items():
        pts = proyectar_rect(*z)
        cv2.fillPoly(overlay, [pts], color_zona_multi(nombre))
    for z in caminos_multi.values():
        pts = proyectar_rect(*z)
        cv2.fillPoly(overlay, [pts], (20, 20, 20))
    frame = cv2.addWeighted(overlay, 0.10, frame, 0.90, 0)
    
    for nombre, z in zonas_plano.items():
        c = color_zona_multi(nombre)
        pts = proyectar_rect(*z)
        grosor = 3 if (modo_ajuste_multi and nombre == nombre_zona_actual_multi()) else 1
        col = (0, 255, 255) if (modo_ajuste_multi and nombre == nombre_zona_actual_multi()) else c
        cv2.polylines(frame, [pts], True, col, grosor)
        lx = int(np.mean(pts[:,0]))
        ly = int(np.mean(pts[:,1]))
        n_corto = nombre_corto(nombre)
        (tw, th), _ = cv2.getTextSize(n_corto, cv2.FONT_HERSHEY_SIMPLEX, 0.32, 1)
        cv2.rectangle(frame, (lx-tw//2-2, ly-th-2), (lx+tw//2+2, ly+2), (0,0,0), -1)
        cv2.putText(frame, n_corto, (lx-tw//2, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.32, col, 1)
    
    for z in caminos_multi.values():
        pts = proyectar_rect(*z)
        cv2.polylines(frame, [pts], True, (40, 40, 40), 1)
    
    return frame

def dibujar_panel_ajuste_multi(frame, h, w):
    cv2.rectangle(frame, (0, 0), (w, 52), (30, 30, 30), -1)
    zona_sel = nombre_zona_actual_multi()
    z = zonas_plano[zona_sel]
    cv2.putText(frame, f"[AJUSTE] Zona: {zona_sel} coords:{z}",
                (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 1)
    cv2.putText(frame, "Tab/Z=cambiar zona  Flechas=mover  +/-=tamaño  WASD=bordes  Espacio=guardar  E=salir",
                (8, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (180, 180, 180), 1)

def procesar_frame_multi(frame):
    global frames_contados, ultimo_fps_time, fps_actual
    ahora = time.time()
    frames_contados += 1
    if ahora - ultimo_fps_time >= 1.0:
        fps_actual = frames_contados
        frames_contados = 0
        ultimo_fps_time = ahora
    
    h, w = frame.shape[:2]
    
    # Modo calibración
    if not calibrado_multi:
        display = frame.copy()
        PASOS = [
            "PASO 1/4 — clic en esquina SUPERIOR-IZQUIERDA",
            "PASO 2/4 — clic en esquina SUPERIOR-DERECHA",
            "PASO 3/4 — clic en esquina INFERIOR-DERECHA",
            "PASO 4/4 — clic en esquina INFERIOR-IZQUIERDA",
        ]
        COLS_CAL = [(0, 220, 255), (0, 180, 200), (0, 140, 180), (0, 100, 160)]
        NOMS_CAL = ["sup-izq", "sup-der", "inf-der", "inf-izq"]
        
        for i, (px, py) in enumerate(puntos_cal_multi):
            cv2.circle(display, (px, py), 10, COLS_CAL[i], -1)
            cv2.circle(display, (px, py), 10, (255, 255, 255), 2)
            cv2.putText(display, NOMS_CAL[i], (px+13, py+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLS_CAL[i], 1)
        if len(puntos_cal_multi) > 1:
            for i in range(len(puntos_cal_multi)-1):
                cv2.line(display, tuple(puntos_cal_multi[i]),
                         tuple(puntos_cal_multi[i+1]), (0, 200, 255), 2)
            if len(puntos_cal_multi) == 4:
                cv2.line(display, tuple(puntos_cal_multi[3]),
                         tuple(puntos_cal_multi[0]), (0, 200, 255), 2)
        
        paso = PASOS[len(puntos_cal_multi)] if len(puntos_cal_multi) < 4 else "Procesando..."
        cv2.rectangle(display, (0, 0), (w, 52), (0, 0, 0), -1)
        cv2.putText(display, paso, (10, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 255), 2)
        cv2.rectangle(display, (0, h-38), (w, h), (18, 18, 18), -1)
        cv2.putText(display, "C=borrar y reiniciar | Q=salir",
                    (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1)
        return display
    
    # Modo detección / ajuste
    warp_limpio = cv2.warpPerspective(frame, M_warp, (WARP_W, WARP_H))
    frame = dibujar_overlay_multi(frame)

    if not modo_ajuste_multi:
        resultados = model(warp_limpio, verbose=False)
        agv_visto = False
        zona_actual = None
        en_camino = False
        ultima_ub = "Esperando..."
        
        for r in resultados:
            for caja in r.boxes:
                agv_visto = True
                bx1, by1, bx2, by2 = map(int, caja.xyxy[0])
                cx = (bx1 + bx2) // 2
                cy = (by1 + by2) // 2
                conf = float(caja.conf[0])
                
                for _, z in caminos_multi.items():
                    zx1, zy1, zx2, zy2 = z
                    if zx1 < cx < zx2 and zy1 < cy < zy2:
                        zona_actual = "En Camino"
                        en_camino = True
                        break
                
                if not en_camino:
                    for nz, z in zonas_almacenes.items():
                        zx1, zy1, zx2, zy2 = z
                        if zx1 < cx < zx2 and zy1 < cy < zy2:
                            zona_actual = nz
                            break
                
                if zona_actual is None:
                    zona_actual = "Fuera de mapa"
                
                # Dibujar en frame original
                col_bb = (0, 255, 80) if en_camino else (0, 255, 0)
                poli_bb = proyectar_rect(bx1, by1, bx2, by2)
                cv2.polylines(frame, [poli_bb], True, col_bb, 2)
                fx, fy = warp_pt_a_frame(cx, cy)
                cv2.circle(frame, (fx, fy), 6, (0, 0, 255), -1)
                cv2.circle(frame, (fx, fy), 6, (255, 255, 255), 1)
                
                etq = f"AGV {conf:.0%} | {zona_actual}"
                (tw, th), _ = cv2.getTextSize(etq, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 1)
                ex = min(fx+8, w-tw-10)
                ey = max(fy-12, th+6)
                cv2.rectangle(frame, (ex-2, ey-th-2), (ex+tw+2, ey+2), (0, 0, 0), -1)
                cv2.putText(frame, etq, (ex, ey), cv2.FONT_HERSHEY_SIMPLEX, 0.50, col_bb, 1)
                break
        
        # Panel estado
        cv2.rectangle(frame, (0, h-38), (w, h), (18, 18, 18), -1)
        col_est = (0, 255, 120) if agv_visto else (0, 80, 255)
        estado = "EN VIVO" if agv_visto else "SIN DETECTAR"
        cv2.putText(frame, f"UBICACION: {zona_actual or ultima_ub} [{estado}]",
                    (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.62, col_est, 2)
        cv2.putText(frame, "E=ajustar zonas  C=recalibrar  Q=salir",
                    (10, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (100, 100, 100), 1)
    else:
        dibujar_panel_ajuste_multi(frame, h, w)
        cv2.rectangle(frame, (0, h-38), (w, h), (18, 18, 18), -1)
        cv2.putText(frame, "MODO AJUSTE — E para volver a deteccion",
                    (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 255), 1)
    
    return frame

# ==========================================
# 13. HILO DE COMANDOS
# ==========================================
def hilo_comandos():
    """Hilo opcional de terminal. Si no hay stdin disponible, termina silenciosamente."""
    try:
        print("\n" + "="*55)
        print("  AGV v6.0 — usa la interfaz grafica o escribe aqui")
        print("  Comandos: indi multi calibrar mapa diagnostico parar salir")
        print("  Zonas:    despacho pits recepcion banda A1..A5 B1..B5")
        print("="*55)
        while True:
            try:
                cmd = input(">> ").strip().lower()
                if cmd:
                    cola_comandos.put(cmd)
                if cmd == 'salir':
                    break
            except EOFError:
                break
    except Exception:
        pass   # Sin terminal disponible — interfaz gráfica se encarga de todo

def ejecutar_comando(comando):
    global modo_ajuste_multi, puntos_cal_multi, calibrado_multi
    
    if comando == 'salir':
        return False
    
    elif comando == 'indi':
        estado_sistema['modo_operacion'] = 'INDI'
        print("🔄 Modo INDIVIDUAL activado")
        cargar_calibracion()
        
    elif comando == 'multi':
        estado_sistema['modo_operacion'] = 'MULTI'
        print("🔄 Modo MULTI/PERSPECTIVA activado")
        cargar_zonas_multi()
        cargar_calibracion_multi()
        
    elif comando == 'calibrar':
        if estado_sistema['modo_operacion'] == 'INDI':
            if estado_sistema['modo'] != 'CALIBRANDO' and not estado_sistema['seleccionando_roi']:
                iniciar_calibracion()
            else:
                print("⚠️ Ya en modo especial")
        else:
            print("⚠️ Calibrar solo en modo INDI. En MULTI usa C para recalibrar perspectiva")
            
    elif comando == 'mapa':
        if estado_sistema['modo_operacion'] == 'INDI':
            if estado_sistema['modo'] == 'MONITOREO' and not estado_sistema['seleccionando_roi']:
                iniciar_mapa()
            else:
                print("⚠️ Termina calibración primero")
        else:
            print("⚠️ Mapa solo en modo INDI")
            
    elif comando == 'camino':
        print(f"📍 Rutas guardadas: {len(rutas_guardadas)}")
        for i, ruta in enumerate(rutas_guardadas):
            print(f"  Ruta {i+1}: {len(ruta)} puntos")
        if estado_sistema['destino']:
            print("🛣️ Nueva ruta iniciada para navegación actual")
            
    elif comando in ('ajustar_rutas', 'ajustar rutas'):
        if estado_sistema['modo'] != 'AJUST_RUTAS':
            iniciar_ajustar_rutas()
        else:
            estado_sistema['modo'] = 'MONITOREO'
            estado_sistema['modo_ajust'] = 'IDLE'
            print("🔄 Ajustar Rutas cerrado")

    elif comando == 'ver_rutas':
        if estado_sistema['modo'] != 'VER_RUTAS':
            estado_sistema['modo'] = 'VER_RUTAS'
            estado_sistema['ver_rutas_origen'] = None
            estado_sistema['ver_rutas_destino'] = None
            notif("Ver Rutas activado", (140,80,200))
        else:
            estado_sistema['modo'] = 'MONITOREO'
            notif("Ver Rutas cerrado", (130,130,150))

    elif comando == 'diagnostico':
        estado_sistema['mostrar_diagnostico'] = not estado_sistema['mostrar_diagnostico']
        print(f"📊 Diagnóstico {'ON' if estado_sistema['mostrar_diagnostico'] else 'OFF'}")
        
    elif comando == 'parar':
        if estado_sistema['destino']:
            notif("Navegacion cancelada", (238,172,172))
            guardar_rutas()
            estado_sistema['destino'] = None
            estado_agv['llegada'] = False
            estado_agv['ruta_alt_waypoints'] = []
            estado_agv['dist_ruta'] = 0
            estado_agv['dist_ruta_alt'] = 0
        else:
            print("ℹ️ Sin destino")
            
    else:
        # Destino directo desde botón del sidebar (__nav__NombreExacto)
        destino = None
        if comando.startswith('__nav__'):
            zona_exacta = comando[7:]
            zonas_buscar = zonas_cam if estado_sistema['modo_operacion'] == 'INDI' else zonas_plano
            if zona_exacta in zonas_buscar:
                destino = zona_exacta
        else:
            # Búsqueda por texto (terminal)
            zonas_buscar = zonas_cam if estado_sistema['modo_operacion'] == 'INDI' else zonas_plano
            for z in zonas_buscar.keys():
                if comando in z.lower():
                    destino = z
                    break
        
        if destino:
            if estado_sistema['modo'] == 'MONITOREO' and not estado_sistema['seleccionando_roi']:
                estado_sistema['destino'] = destino
                estado_agv['llegada'] = False
                notif(f"Destino: {nombre_corto(destino)}", (92,240,112))
                
                # NUEVO: Calcular ruta por grafo y waypoints
                zona_actual = estado_agv['zona_actual'] if estado_agv['zona_actual'] != "Desconocida" else None

                # Si está en un camino, usar el nodo físico más cercano como origen
                if zona_actual in (None, "Camino", "Desconocida") and estado_agv['posicion']:
                    px, py = estado_agv['posicion']
                    mejor_i, mejor_d = None, float('inf')
                    for i, (nx, ny) in enumerate(nodos_grafo):
                        d = math.hypot(px - nx, py - ny)
                        if d < mejor_d:
                            mejor_d = d
                            mejor_i = i
                    if mejor_i is not None:
                        zona_actual = f'_n_{mejor_i}'

                if zona_actual and zona_actual in grafo_navegacion:
                    # 1) Ruta personalizada tiene prioridad
                    wps_pers, dist_pers = obtener_ruta_personalizada(zona_actual, destino)
                    if wps_pers:
                        estado_agv['ruta_waypoints']     = wps_pers
                        estado_agv['ruta_alt_waypoints'] = []
                        estado_agv['waypoint_actual']    = 0
                        estado_agv['dist_ruta']          = dist_pers
                        estado_agv['dist_ruta_alt']      = 0
                        estado_agv['zona_siguiente']     = destino
                        print(f"🗺️ Ruta personalizada ({dist_pers}px): {nombre_corto(zona_actual)} → {nombre_corto(destino)}")
                    else:
                        # 2) Dijkstra por caminos calibrados
                        rutas = encontrar_rutas_alternativas(zona_actual, destino)
                        if rutas:
                            ruta1, dist1 = rutas[0]
                            estado_agv['ruta_waypoints']  = construir_waypoints(ruta1)
                            estado_agv['waypoint_actual'] = 0
                            estado_agv['dist_ruta']       = int(dist1)
                            estado_agv['zona_siguiente']  = ruta1[1] if len(ruta1) > 1 else destino
                            print(f"🗺️ Ruta óptima ({int(dist1)}px): {' → '.join(nombre_corto(n) for n in ruta1 if not n.startswith('_'))}")
                            if len(rutas) > 1:
                                ruta2, dist2 = rutas[1]
                                estado_agv['ruta_alt_waypoints'] = construir_waypoints(ruta2)
                                estado_agv['dist_ruta_alt']      = int(dist2)
                                print(f"   Alternativa ({int(dist2)}px)")
                            else:
                                estado_agv['ruta_alt_waypoints'] = []
                                estado_agv['dist_ruta_alt']      = 0
                        else:
                            estado_agv['ruta_waypoints']     = []
                            estado_agv['ruta_alt_waypoints'] = []
                            estado_agv['waypoint_actual']    = 0
                            estado_agv['dist_ruta']          = 0
                            estado_agv['dist_ruta_alt']      = 0
                            print("⚠️ Sin ruta — navegación directa")
                else:
                    # Sin zona conocida, ir directo
                    estado_agv['ruta_waypoints'] = []
                    estado_agv['waypoint_actual'] = 0
                
                iniciar_nueva_ruta()
                print(f"🚀 A: {destino.upper()} | Nueva ruta iniciada")
            else:
                print("⚠️ Termina calibración/mapa primero")
        else:
            print(f"❌ '{comando}' no encontrado")
    
    return True

# ==========================================
# 14. CALLBACK UNIFICADO DE MOUSE
# ==========================================

VIDEO_W = 640   # ancho fijo del area de video

def clic_universal(event, x, y, flags, param):
    """Un solo callback para toda la ventana."""
    if x >= VIDEO_W:
        if event == cv2.EVENT_LBUTTONDOWN:
            procesar_click_sidebar(x - VIDEO_W, y)
        return
    # Área de video
    modo    = estado_sistema['modo']
    modo_op = estado_sistema['modo_operacion']
    if modo == 'CALIBRANDO':
        clic_calibrador(event, x, y, flags, param)
    elif estado_sistema.get('seleccionando_roi', False):
        clic_mapa_poligono(event, x, y, flags, param)
    elif tab_activa == 'RUTAS' and rutas_sub == 'NUEVA':
        # Dibujar puntos de ruta en el video
        if event == cv2.EVENT_LBUTTONDOWN:
            puntos_ruta_dibujada.append((x, y))
        elif event == cv2.EVENT_RBUTTONDOWN and puntos_ruta_dibujada:
            puntos_ruta_dibujada.pop()
    elif modo_op == 'MULTI' and not calibrado_multi:
        mouse_cb_multi(event, x, y, flags, param)


# ==========================================
# 15. MAIN
# ==========================================
def main():
    global camara_activa, modo_ajuste_multi, puntos_cal_multi, calibrado_multi
    global tab_activa, rutas_sub, rutas_nueva_orig, rutas_nueva_dest, ruta_seleccionada

    cargar_calibracion()
    cargar_roi_poligono()
    cargar_rutas()
    cargar_rutas_personalizadas()
    
    t_cam = threading.Thread(target=hilo_camara, daemon=True)
    t_cam.start()
    
    timeout = 0
    while not camara_activa and timeout < 100:
        time.sleep(0.05)
        timeout += 1
    
    if not camara_activa:
        print("❌ Cámara falló")
        return
    
    t_cmd = threading.Thread(target=hilo_comandos, daemon=True)
    t_cmd.start()
    
    cv2.namedWindow("AGV - SISTEMA DE GUIADO", cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("AGV - SISTEMA DE GUIADO", 80, 60)
    cv2.setMouseCallback("AGV - SISTEMA DE GUIADO", clic_universal)

    print("\n✅ Sistema activo | Modo por defecto: INDI")
    
    running = True
    while running:
        while not cola_comandos.empty():
            cmd = cola_comandos.get()
            if not ejecutar_comando(cmd):
                running = False
                break
        
        if not running:
            break
        
        frame = obtener_frame()
        if frame is None:
            time.sleep(0.005)
            continue
        
        if estado_sistema['modo_operacion'] == 'INDI':
            img = frame.copy()
            modo_actual = estado_sistema['modo']
            if estado_sistema['seleccionando_roi']:
                img = procesar_frame_indi(img)
                img = dibujar_roi_seleccion(img)
            elif modo_actual == 'CALIBRANDO':
                img = procesar_frame_indi(img)
                img = procesar_calibracion(img)
            elif tab_activa == 'RUTAS':
                img = procesar_frame_indi(img)
                if ruta_seleccionada or rutas_sub == 'NUEVA':
                    img = dibujar_overlay_rutas(img)
            else:
                img = procesar_frame_indi(img)

            # Extender canvas a CANVAS_H si el video es más corto
            if img.shape[0] < CANVAS_H:
                pad = np.zeros((CANVAS_H - img.shape[0], img.shape[1], 3), dtype=np.uint8)
                img = np.vstack([img, pad])
            sidebar, _ = dibujar_sidebar(CANVAS_H)
            combined = np.hstack([img, sidebar])
            cv2.imshow("AGV - SISTEMA DE GUIADO", combined)
            tecla = cv2.waitKey(1) & 0xFF
            if modo_actual == 'CALIBRANDO':
                tecla_calibracion(tecla)
            elif tecla == ord('q') or tecla == 27:
                if tab_activa == 'RUTAS':
                    tab_activa = 'NAVEGAR'   # q sale de la pestaña RUTAS
                    ruta_seleccionada = None
                else:
                    running = False           # q cierra el programa
        
        else:  # MODO MULTI
            img = frame.copy()
            img = procesar_frame_multi(img)
            if img.shape[0] < CANVAS_H:
                pad = np.zeros((CANVAS_H - img.shape[0], img.shape[1], 3), dtype=np.uint8)
                img = np.vstack([img, pad])
            sidebar, _ = dibujar_sidebar(CANVAS_H)
            combined = np.hstack([img, sidebar])
            cv2.imshow("AGV - SISTEMA DE GUIADO", combined)
            tecla = cv2.waitKey(20) & 0xFF
            
            if not calibrado_multi:
                if tecla == ord('q'):
                    running = False
                if tecla == ord('c'):
                    puntos_cal_multi.clear()
                    calibrado_multi = False
                    M_warp = M_inv = None
                    if os.path.exists(cal_path):
                        os.remove(cal_path)
            else:
                if tecla == ord('q'):
                    running = False
                if tecla == ord('c'):
                    puntos_cal_multi.clear()
                    calibrado_multi = False
                    M_warp = M_inv = None
                    if os.path.exists(cal_path):
                        os.remove(cal_path)
                if tecla == ord('e'):
                    modo_ajuste_multi = not modo_ajuste_multi
                    print("Modo ajuste:", "ON" if modo_ajuste_multi else "OFF")
                if modo_ajuste_multi:
                    manejar_tecla_ajuste_multi(tecla)
    
    # Cierre
    camara_activa = False
    guardar_rutas()
    time.sleep(0.2)
    if cap_global:
        cap_global.release()
    cv2.destroyAllWindows()
    print("👋 Cerrado")

if __name__ == "__main__":
    main()