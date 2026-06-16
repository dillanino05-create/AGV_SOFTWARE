# CORPUS — SISTEMA DE GUIADO AGV (prueba_2.py)

Documentación técnica del sistema de visión artificial y navegación para
el AGV (vehículo guiado autónomo). Esta carpeta es **autocontenida**:
incluye el script, el modelo entrenado y todos los archivos de datos que
necesita para arrancar sin depender del resto del repositorio.

---

## ÍNDICE

1. [Qué hace este programa](#1-qué-hace-este-programa)
2. [Contenido de esta carpeta](#2-contenido-de-esta-carpeta)
3. [Instalación y ejecución](#3-instalación-y-ejecución)
4. [Arquitectura del archivo prueba_2.py](#4-arquitectura-del-archivo-prueba_2py)
5. [Modos de operación](#5-modos-de-operación)
6. [Interfaz de usuario (sidebar)](#6-interfaz-de-usuario-sidebar)
7. [Archivos de datos — formato y propósito](#7-archivos-de-datos--formato-y-propósito)
8. [Flujo de navegación (grafo y rutas)](#8-flujo-de-navegación-grafo-y-rutas)
9. [Comandos por terminal](#9-comandos-por-terminal)
10. [Problemas conocidos / cosas a verificar](#10-problemas-conocidos--cosas-a-verificar)

---

## 1. QUÉ HACE ESTE PROGRAMA

`prueba_2.py` es una aplicación de escritorio que:

1. Abre una cámara web y corre un modelo **YOLOv8** (`best (1).pt`) entrenado
   para detectar al AGV en cada frame.
2. Ubica al AGV dentro de un **mapa de zonas** del almacén (Despacho, Pits,
   Recepción, Banda, Almacenes A1-A5 y B1-B5).
3. Permite elegir un **destino** desde la interfaz y calcula la ruta más
   corta usando un grafo de navegación (Dijkstra) construido a partir de
   caminos calibrados o rutas dibujadas a mano.
4. Muestra instrucciones de navegación en tiempo real (`SIGUE DERECHO`,
   `GIRA IZQUIERDA`, `VUELTA EN U`, `PUNTO ALCANZADO`...) calculadas según
   el rumbo detectado del AGV y el siguiente waypoint.
5. Todo esto se dibuja con primitivas de OpenCV — no usa ningún framework
   de UI (Tkinter/Qt). El "sidebar" con pestañas y botones es un panel de
   píxeles que se compone manualmente cuadro a cuadro.

No hay comunicación con el firmware del AGV en este script — es **solo la
capa de visión y cálculo de instrucciones**. El envío real de comandos al
hardware (MQTT/ESP32) vive en el módulo `ACTUADORES/` del repositorio
principal.

---

## 2. CONTENIDO DE ESTA CARPETA

| Archivo | Tipo | Descripción |
|---|---|---|
| `prueba_2.py` | Script | Programa principal (ver sección 4) |
| `best (1).pt` | Modelo binario | Pesos YOLOv8 entrenados para detectar el AGV |
| `calibracion_en_vivo.txt` | Datos (texto/Python literal) | Zonas, caminos y ROI calibrados en modo INDI |
| `calibracion_pista.json` | Datos (JSON) | Puntos `src` de la homografía del modo MULTI |
| `zonas_ajustadas.json` | Datos (JSON) | Zonas/caminos del modo MULTI (vista en perspectiva) |
| `roi_poligono.json` | Datos (JSON) | Polígono del área de pista válida (modo INDI) |
| `rutas_historial.json` | Datos (JSON) | Últimas 5 trayectorias reales dibujadas por el AGV |
| `rutas_personalizadas.json` | Datos (JSON) | Rutas punto-a-punto dibujadas manualmente entre zonas |
| `requirements.txt` | Dependencias | Paquetes Python necesarios |
| `CORPUS.md` | Este documento | |

> Todos los archivos de datos son opcionales en el sentido de que si no
> existen, el programa los crea vacíos y sigue funcionando — pero sin
> ellos no habrá zonas/rutas calibradas y la navegación no podrá
> calcularse hasta que se calibre desde la propia interfaz.

---

## 3. INSTALACIÓN Y EJECUCIÓN

```bash
cd SISTEMA_GUIADO_AGV
pip install -r requirements.txt
python prueba_2.py
```

**Requisitos de hardware:** una cámara accesible por OpenCV. El script abre
`cv2.VideoCapture(2)` (índice de cámara **2**, hardcodeado en
`hilo_camara()`). Si tu cámara está en otro índice (0, 1, 3...), hay que
cambiar ese número en el archivo.

Al iniciar, el modelo YOLO se carga desde `best (1).pt` ubicado junto al
script (`script_dir`), así que **esta carpeta debe mantenerse junta** — no
mover el script sin el `.pt`.

---

## 4. ARQUITECTURA DEL ARCHIVO prueba_2.py

El archivo (~2950 líneas) está organizado en 15 secciones marcadas con
comentarios `# N. NOMBRE`:

| # | Sección | Contenido clave |
|---|---|---|
| 1 | Configuración global | Rutas de archivos, tamaño del sidebar/canvas |
| 2 | Variables globales | `estado_sistema`, `estado_agv`, cámara, FPS, cola de comandos |
| 3 | Colores de zonas | Paleta BGR por nombre de zona |
| 4 | Funciones de rutas | Historial de trayectoria real del AGV (`rutas_guardadas`) |
| 5 | Sidebar UI | `dibujar_sidebar`, pestañas NAVEGAR/RUTAS/CONFIG, notificaciones |
| 6 | Carga/guardado de calibración | Persistencia a los `*.json`/`*.txt` |
| 6.5 | Grafo y hitboxes | Construcción del grafo de navegación (Dijkstra/BFS) |
| 7 | Funciones de navegación | Brújula, instrucción según waypoint actual |
| 8 | Panel de diagnóstico | Overlay con FPS, posición, confianza, waypoint actual |
| 9 | Modo CALIBRAR | Clic de 4 esquinas por zona (modo INDI) |
| 10 | Modo MAPA | Definición del polígono de pista válida |
| 11 | Modo AJUSTAR RUTAS | Dibujo manual de rutas origen→destino |
| 11B | Ver Rutas | Visualizar/comparar rutas guardadas entre dos zonas |
| 12 | Procesar frame INDI | Pipeline de detección + overlay para cámara real |
| 12 (bis) | Modo MULTI | Vista en perspectiva (homografía) con mapa fijo |
| 13 | Hilo de comandos | Entrada por terminal en paralelo a la GUI |
| 14 | Callback de mouse | Único `setMouseCallback` que enruta clics según zona/x |
| 15 | `main()` | Bucle: leer cámara → procesar → dibujar → `imshow` → teclado |

### Estructuras de estado principales

```python
estado_sistema = {
    'modo_operacion': 'INDI' | 'MULTI',
    'modo': 'MONITOREO' | 'CALIBRANDO' | 'AJUST_RUTAS' | 'VER_RUTAS',
    'destino': <nombre_zona> | None,
    ...
}

estado_agv = {
    'detectado': bool,
    'posicion': (x, y) | None,
    'zona_actual': <nombre_zona>,
    'rumbo': 'NORTE'|'SUR'|'ESTE'|'OESTE'|'DESCONOCIDO',
    'ruta_waypoints': [(x,y), ...],   # ruta activa a seguir
    'waypoint_actual': int,
    'instruccion': <texto mostrado>,
    ...
}
```

Estas dos variables globales son el "estado del mundo" que todas las
funciones de dibujo y navegación leen/actualizan en cada frame.

### Hilos

- **Hilo de cámara** (`hilo_camara`): lee frames continuamente en
  background y los deja en `frame_actual` protegido por `frame_lock`.
- **Hilo de comandos** (`hilo_comandos`): lee `stdin` y empuja comandos a
  `cola_comandos` — permite operar el sistema escribiendo en la terminal
  además de usar el mouse.
- El **hilo principal** corre el bucle de `main()`: consume
  `cola_comandos`, captura el frame más reciente, dibuja todo y llama a
  `cv2.imshow` + `cv2.waitKey`.

---

## 5. MODOS DE OPERACIÓN

### INDI (cámara individual)
Usa la imagen de la cámara tal cual. Las zonas se calibran a mano sobre el
video real (4 clics por zona, modo CALIBRAR). Bueno para una sola cámara
fija mirando toda la pista.

### MULTI (perspectiva)
Aplica una **homografía** (`cv2.getPerspectiveTransform`) para "enderezar"
una vista en ángulo y mapearla a un plano fijo de `640×480` con zonas
predefinidas en `zonas_por_defecto_multi()`. Útil cuando la cámara no está
perfectamente cenital.

El cambio de modo se hace desde la pestaña **CONFIG** del sidebar o
escribiendo `indi` / `multi` en la terminal.

### Submodos dentro de INDI (`estado_sistema['modo']`)
- `MONITOREO`: operación normal, navegación activa.
- `CALIBRANDO`: clic de 4 esquinas por zona requerida (`ZONAS_REQUERIDAS`).
- `AJUST_RUTAS`: clic en zona origen → zona destino → dibujar trazo de
  ruta personalizada, click a click, sobre el video.
- `VER_RUTAS`: comparar visualmente las rutas guardadas entre dos zonas.

---

## 6. INTERFAZ DE USUARIO (SIDEBAR)

El sidebar (270 px de ancho) tiene 3 pestañas:

- **NAVEGAR**: grilla de botones para elegir destino (Despacho, Pits,
  Recepción, Banda, A1-A5, B1-B5), botón "PARAR NAVEGACION", y tarjetas de
  estado del AGV (detectado, zona, rumbo, instrucción actual).
- **RUTAS**: lista de rutas personalizadas guardadas, agrupadas por par
  origen→destino, con botones `VER` (resalta la ruta sobre el video) y `X`
  (eliminar). Botón `+ NUEVA RUTA` abre el formulario de creación
  (elegir origen, destino, dibujar puntos en el video, guardar).
  *Esta lista tiene scroll con la rueda del mouse cuando hay más rutas de
  las que caben en pantalla.*
- **CONFIG**: cambio de modo INDI/MULTI, botones "Calibrar Zonas" /
  "Definir Mapa", toggle de diagnóstico, y contador de zonas/caminos/rutas
  cargadas.

Todos los clics del sidebar pasan por `procesar_click_sidebar(sx, sy)`,
que recorre `_btn_rects_cache` (rectángulos de cada botón calculados al
dibujar) y dispara la acción correspondiente (casi siempre poniendo un
comando en `cola_comandos` o cambiando una variable de estado global).

---

## 7. ARCHIVOS DE DATOS — FORMATO Y PROPÓSITO

### `calibracion_en_vivo.txt`
No es JSON — son 3 líneas con literales de Python (`repr` de dict/list),
leídas con `ast.literal_eval`:
```
zonas_cam = {'Zona Despacho': [(x,y), (x,y), (x,y), (x,y)], ...}
caminos_cam = [[(x1,y1), (x2,y2)], ...]
roi_pista = ...
```
Se genera al guardar una calibración en modo INDI (`guardar_calibracion`).

### `roi_poligono.json`
Lista de vértices `[[x,y], ...]` que delimitan el área de pista válida
(modo INDI, sección 10).

### `calibracion_pista.json`
```json
{"src": [[x,y], [x,y], [x,y], [x,y]]}
```
Los 4 puntos de origen de la homografía para el modo MULTI.

### `zonas_ajustadas.json`
```json
{"almacenes": {...}, "externas": {...}, "caminos": {...}}
```
Definición de zonas del modo MULTI sobre el plano `640×480` ya enderezado.

### `rutas_historial.json`
```json
{"rutas": [[[x,y], [x,y], ...], ...]}
```
Últimas 5 trayectorias reales recorridas por el AGV detectado (rastro).

### `rutas_personalizadas.json`
```json
{
  "ZonaOrigen|ZonaDestino": [
    [[x,y], [x,y], ...],   // ruta 1 entre ese par
    [[x,y], [x,y], ...]    // ruta 2 alternativa (opcional)
  ]
}
```
Rutas dibujadas a mano (modo AJUST_RUTAS o pestaña RUTAS → NUEVA RUTA).
Son las que usa el sistema para construir el grafo de navegación punto a
punto cuando no hay un camino calibrado directo.

---

## 8. FLUJO DE NAVEGACIÓN (GRAFO Y RUTAS)

1. Al cargar calibración, `reconstruir_grafo_navegacion()` agrupa los
   extremos de los segmentos de `caminos_cam` en **nodos** (tolerancia de
   25 px) y conecta cada zona al nodo de camino más cercano.
2. Al pedir un destino, se busca la ruta más corta entre el nodo/zona
   actual y el destino con **Dijkstra** (`encontrar_ruta_corta`), pesando
   cada arista por distancia euclidiana real en píxeles.
3. Esa secuencia de nodos se convierte en una lista de waypoints físicos
   (`construir_waypoints`).
4. En cada frame, `calcular_instruccion_waypoint` compara la posición y
   rumbo actuales del AGV contra el siguiente waypoint y genera la
   instrucción a mostrar (`SIGUE DERECHO`, `GIRA DERECHA`, etc.).
5. Si existe una ruta personalizada guardada para el par origen→destino
   (`rutas_personalizadas`), el sistema puede usarla en lugar del grafo
   genérico (ver `obtener_ruta_personalizada` / `todas_rutas_personalizadas`).

---

## 9. COMANDOS POR TERMINAL

Mientras el programa corre, la terminal acepta los mismos comandos que los
botones de la GUI (útil para debug sin usar el mouse):

```
indi            -> cambia a modo INDI
multi           -> cambia a modo MULTI
calibrar        -> inicia calibración de zonas (modo INDI)
mapa            -> inicia definición del polígono de pista
diagnostico     -> activa/desactiva el panel de diagnóstico
parar           -> cancela navegación activa
despacho / pits / recepcion / banda / a1..a5 / b1..b5  -> fija destino
salir           -> cierra el programa
```

---

## 10. PROBLEMAS CONOCIDOS / COSAS A VERIFICAR

- **Índice de cámara hardcodeado**: `cv2.VideoCapture(2)` en
  `hilo_camara()`. Si la cámara correcta está en otro índice, el programa
  imprime `❌ ERROR: No se pudo abrir la cámara` y termina.
- El archivo `calibracion_en_vivo.txt` usa `ast.literal_eval` sobre texto
  con formato Python (no JSON real) — si se edita a mano hay que respetar
  exactamente la sintaxis de tuplas/listas de Python.
- Los datos de calibración (zonas, rutas, ROI) son específicos de la
  posición física de la cámara. Si se cambia la cámara o su ángulo, hay
  que volver a calibrar (`calibrar` / `mapa` / `ajustar_rutas`) — los
  archivos `.json`/`.txt` de esta carpeta son solo un punto de partida de
  ejemplo, no valores universales.
