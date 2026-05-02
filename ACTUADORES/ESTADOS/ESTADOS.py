#estados.py
# ================================
# MODULO: estados.py 
# Máquina de estados del AGV
# ================================

import motores
import elevador
import comunicacion
import config
import time

# -------- ESTADOS POSIBLES --------
IDLE = "IDLE"
MOVIENDO = "MOVIENDO"
CARGANDO = "CARGANDO"
DESCARGANDO = "DESCARGANDO"
ERROR = "ERROR"

# -------- VARIABLES DE ESTADO --------
estado_actual = IDLE
tiempo_estado = 0


# -------- CAMBIO DE ESTADO --------

def cambiar_estado(nuevo_estado):
    global estado_actual, tiempo_estado

    estado_actual = nuevo_estado
    tiempo_estado = time.ticks_ms()

    if config.DEBUG:
        print("Nuevo estado:", estado_actual)


# -------- INICIALIZACIÓN --------

def inicializar():
    cambiar_estado(IDLE)


# -------- LÓGICA PRINCIPAL --------

def actualizar():
    global estado_actual

    # 1. Leer comando desde MQTT
    accion, velocidad = comunicacion.obtener_comando()

    # 2. Máquina de estados
    if estado_actual == IDLE:
        _estado_idle(accion, velocidad)

    elif estado_actual == MOVIENDO:
        _estado_moviendo(accion, velocidad)

    elif estado_actual == CARGANDO:
        _estado_cargando()

    elif estado_actual == DESCARGANDO:
        _estado_descargando()

    elif estado_actual == ERROR:
        _estado_error()

    # 3. Actualizar módulos dependientes
    elevador.actualizar_elevador()


# -------- IMPLEMENTACIÓN DE ESTADOS --------

def _estado_idle(accion, velocidad):
    motores.detener()

    if accion == "avanzar":
        cambiar_estado(MOVIENDO)

    elif accion == "retroceder":
        cambiar_estado(MOVIENDO)

    elif accion == "girar_izquierda":
        cambiar_estado(MOVIENDO)

    elif accion == "girar_derecha":
        cambiar_estado(MOVIENDO)

    elif accion == "cargar":
        elevador.iniciar_subida()
        cambiar_estado(CARGANDO)

    elif accion == "descargar":
        elevador.iniciar_bajada()
        cambiar_estado(DESCARGANDO)


def _estado_moviendo(accion, velocidad):

    if accion == "STOP" or accion is None:
        motores.detener()
        cambiar_estado(IDLE)
        return

    if accion == "avanzar":
        motores.avanzar(velocidad)

    elif accion == "retroceder":
        motores.retroceder(velocidad)

    elif accion == "girar_izquierda":
        motores.girar_izquierda(velocidad)

    elif accion == "girar_derecha":
        motores.girar_derecha(velocidad)


def _estado_cargando():

    if elevador.obtener_estado() == "IDLE":
        cambiar_estado(IDLE)


def _estado_descargando():

    if elevador.obtener_estado() == "IDLE":
        cambiar_estado(IDLE)


def _estado_error():
    motores.detener()
    # Aquí puedes agregar lógica de recuperación futura


# -------- CONSULTA DE ESTADO --------

def obtener_estado():
    return estado_actual







#________________________________________
#EXPLICACIÓN
#________________________________________
# BLOQUE 1: PROPÓSITO
## Máquina de estados del AGV QUE actúa como el cerebro lógico del AGV
#Convirtiendo COMANDOS → DECISIONES → ACCIONES
#
#BLOQUE 2: IMPORTS
#import motores
#import elevador
#import comunicación
##este módulo NO controla directamente hardware coordina módulos, separando las responsabilidades
#•	motores → movimiento
#•	elevador → carga
#•	comunicación → órdenes
#
#BLOQUE 3: DEFINICIÓN DE ESTADOS
#IDLE, MOVIENDO, CARGANDO, DESCARGANDO, ERROR, y esto es vital porque define el comportamiento del sistema:
#Estado	Significado
#IDLE	detenido
#MOVIENDO	en desplazamiento
#CARGANDO	subiendo carga
#DESCARGANDO	bajando carga
#ERROR	fallo
#
#Esto es una FSM (Finite State Machine)
#
#BLOQUE 4: VARIABLES DE ESTADO
#estado_actual = qué está haciendo el robot
#tiempo_estado = cuándo entró al estado
#útil para: temporizadores, seguridad, watchdog
#
#BLOQUE 5: CAMBIO DE ESTADO
#def cambiar_estado(nuevo_estado) #ACTUALIZACIÓN
# registro temporal: tiempo_estado = time.ticks_ms()
#
#BLOQUE 6: ACTUALIZAR (EL CORAZÓN)
#def actualizar(): #ESTE ES EL LOOP CENTRAL. Se ejecuta constantemente desde main.py