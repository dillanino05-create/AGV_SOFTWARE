#elevador.py 
# ================================
# MODULO: elevador.py
# Control de actuador de elevación AGV
# ================================

from machine import Pin
import time
import config

#PIN: controla salidas digitales
#Time: permite medir tiempo sin bloquear
#Config: ACCESO A
#config.TIEMPO_ELEVADOR

# -------- CONFIGURACIÓN DE PINES --------

motor_subir = Pin(25, Pin.OUT)
motor_bajar = Pin(26, Pin.OUT)

#para controlar punte h o relé doble:
#Subir	Bajar	Resultado
#1	0	Sube
#0	1	Baja
#0	0	Stop
#1	1	PELIGRO


# -------- VARIABLES DE ESTADO --------

estado_elevador = "IDLE"   # IDLE, SUBIENDO, BAJANDO
tiempo_inicio = 0
#Estados posibles: IDLE → quieto, SUBIENDO → activo, BAJANDO → activo


# -------- CONTROL BÁSICO --------

def detener_elevador():
    motor_subir.value(0)
    motor_bajar.value(0)


def iniciar_subida():
    global estado_elevador, tiempo_inicio

    motor_subir.value(1)
    motor_bajar.value(0)

    estado_elevador = "SUBIENDO"
    tiempo_inicio = time.ticks_ms()


def iniciar_bajada():
    global estado_elevador, tiempo_inicio

    motor_subir.value(0)
    motor_bajar.value(1)

    estado_elevador = "BAJANDO"
    tiempo_inicio = time.ticks_ms()


# -------- ACTUALIZACIÓN NO BLOQUEANTE --------

def actualizar_elevador(): #ESTAR ACTUALIZANDO EL ESTADO DEL ELEVADOR, POR LO QUE SE DEBE DE ESTAR LLAMANDO EN EL LOOP PRINCIPAL
    global estado_elevador

    if estado_elevador == "IDLE":
        return

    tiempo_actual = time.ticks_ms()
    tiempo_transcurrido = time.ticks_diff(tiempo_actual, tiempo_inicio)
# evita errores por overflow del contador

    if tiempo_transcurrido >= config.TIEMPO_ELEVADOR:
        detener_elevador()
        estado_elevador = "IDLE"


# -------- CONSULTA DE ESTADO --------

def obtener_estado():
    return estado_elevador

# integración con main.py, MQTT, HMI.
