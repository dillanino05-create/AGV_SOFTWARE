#motores.py 
# ================================
# MODULO: motores.py
# Control de tracción AGV (L298N + ESP32)
# ================================

from machine import Pin, PWM # Machine es una Librería de MicroPython para hardware que permite controlar pines, generar PWM
# Pin: Representa un pin físico del ESP32, por Ej:
#Pin(5, Pin.OUT), entonces GPIO5 queda en modo salida
#PWM : para simular voltaje a través de valores analógicos.

import config # Centraliza parámetros del sistema, evita valores que no se tienen ni idea de dónde provienen y permite cambiar comportamiento sin tocar la lógica principal.


# -------- CONFIGURACIÓN DE PINES --------

# Motor izquierdo (canal A)
IN1 = Pin(5, Pin.OUT) #Da dirección
IN2 = Pin(18, Pin.OUT) #Da dirección
ENA = PWM(Pin(23), freq=config.PWM_FREQ) #Da velocidad
#IN1	IN2	Resultado
#1	0	Adelante
#0	1	Atrás
#0	0	Stop

# Motor derecho (canal B)
IN3 = Pin(19, Pin.OUT)
IN4 = Pin(21, Pin.OUT)
ENB = PWM(Pin(22), freq=config.PWM_FREQ)

# -------- FUNCIÓN AUXILIAR --------

def _limitar_velocidad(vel):
    """
    Limita la velocidad al rango permitido por PWM
    """
    if vel > config.VELOCIDAD_MAX:
        vel = config.VELOCIDAD_MAX
    elif vel < -config.VELOCIDAD_MAX:
        vel = -config.VELOCIDAD_MAX
    return vel

#una función que actúe si se envian valores mmalos
#Ejemplo:
#avanzar (5000), se sobrepasa del límite, lo que va a generar un comportamiento errático
#por ello: 
#if vel > MAX → vel = MAX
#if vel < -MAX → vel = -MAX


# -------- CONTROL MOTOR INDIVIDUAL --------

def motor_izquierdo(vel):
    vel = _limitar_velocidad(vel)

    if vel > 0: #AVANCE
        IN1.value(1)
        IN2.value(0)
    elif vel < 0: #REVERSA
        IN1.value(0)
        IN2.value(1)
        vel = -vel #convierte velocidad negativa en PWM positivo
    else:
        IN1.value(0)
        IN2.value(0)

    ENA.duty(int(vel)) # PWM NO acepta floats


def motor_derecho(vel):
    vel = _limitar_velocidad(vel)

    if vel > 0:
        IN3.value(1)
        IN4.value(0)
    elif vel < 0:
        IN3.value(0)
        IN4.value(1)
        vel = -vel
    else:
        IN3.value(0)
        IN4.value(0)

    ENB.duty(int(vel))
#POR MOTOR, tenemos una vel ∈ [-1023, 1023]
#Cuando Avanza:
#if vel > 0:
#    IN1 = 1
#    IN2 = 0
#Lo que significa que el motor gira hacia adelante
#De reversa:
#elif vel < 0:
#    IN1 = 0
#    IN2 = 1
#Se le nvierte la polaridad por lo que cambia sentido
#AHORA: 
#vel = -vel, ya que PWM no debería aceptar negativos, se convierten a valor positivo, para mantienes la dirección con pines
#CUANDO SE DETIENE:
#IN1 = 0
#IN2 = 0

#PWM final:
#ENA.duty(int(vel)), lo que influencia la velocidad


# -------- MOVIMIENTOS DEL AGV --------

def avanzar(vel=config.VELOCIDAD_DEFAULT):
    motor_izquierdo(vel)
    motor_derecho(vel)


def retroceder(vel=config.VELOCIDAD_DEFAULT):
    motor_izquierdo(-vel)
    motor_derecho(-vel)


def girar_izquierda(vel=config.VELOCIDAD_DEFAULT):
    motor_izquierdo(-vel)
    motor_derecho(vel)


def girar_derecha(vel=config.VELOCIDAD_DEFAULT):
    motor_izquierdo(vel)
    motor_derecho(-vel)


def detener():
    motor_izquierdo(0)
    motor_derecho(0)

#PARA AVANZAR:
#motor_izquierdo(vel)
#motor_derecho(vel)
#ambos giran igual, avanza hacia el frente.
#
#PARA retroceder
#motor_izquierdo(-vel)
#motor_derecho(-vel)
#ambos hacia atrás
#
#girar izquierda:
#izq = -vel
#der = vel
#un motor adelante, otro atrás.
#
#girar derecho, inverso
#izq = vel
#der = -vel
#
#detener
#motor_izquierdo(0)
#motor_derecho(0)


# -------- FUNCIONES AVANZADAS (ESCALABILIDAD) --------

def mover_diferencial(vel_izq, vel_der):
    """
    Control independiente de cada rueda (base navegación)
    """
    motor_izquierdo(vel_izq)
    motor_derecho(vel_der)

#Esto es una función base por si se quiere hacer que haya seguimiento de línea, navegación predeterminada con lo que nos den en los formatos JSON, etc, agg sensores (IR)