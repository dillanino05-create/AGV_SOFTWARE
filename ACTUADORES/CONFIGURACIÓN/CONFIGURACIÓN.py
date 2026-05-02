#CÓDIGO 1: config.py 
# ================================
# CONFIGURACIÓN GLOBAL DEL AGV
# ================================

# -------- MQTT / COMUNICACIÓN --------
MQTT_BROKER = "192.168.1.100" #(Red de Área local LAN, para menor latencia, "192.168.1.100", normalmente para redes con rangos en casas, laboratorios.)

MQTT_PORT = 1883 # (MQTT ESTÁNDAR SIN CIFRADO, simple, rápido y suficiente para prototipos)

CLIENT_ID = "AGV_01" # (Porque en un sistema real habrá: AGV_01, AGV_02, AGV_03, etc., lo que permite identificación única y evita conflictos en bróker)

#BLOQUE MQTT
#Esto cumple directamente con el contrato de interfaces:
#•	comunicación por red
#•	identificación única del AGV
#•	integración con WMS
#

TOPIC_CMD = "agv/cmd"
TOPIC_STATUS = "agv/status"
#BLOQUE TOPICS
#Se separa: entrada (comandos) de salida (estado), y Esto es EXACTAMENTE lo que pide un sistema distribuido tipo AS/RS.

# -------- FORMATO DE MENSAJES --------
USE_JSON = True

#BLOQUE FORMATO: mensajes estructurados (JSON)
 #Esto permite algo como:
#{
#  "accion": "mover",
#  "vel": 600,
#  "direccion": "adelante"
#}


# -------- PWM / MOTORES --------
PWM_FREQ = 1000          # Frecuencia PWM en Hz #(1000 Hz equilibrio, ya que la frec ni es muy baja para provocar mov bruscos, ni muy alta para sobrecalentamiento)

PWM_MAX = 1023           # Resolución típica ESP32 (MicroPython) #(PWM de 10bits= 2¹⁰ = 1024 → rango 0–1023)
PWM_MIN = 0


VELOCIDAD_DEFAULT = 600 # Velocidad base.  #(600 / 1023 ≈ 58% suficiente torque, evita saturar motor, evita caídas de voltaje)

VELOCIDAD_MAX = 1023     # Límite superior seguro

# -------- TIEMPOS (NO BLOQUEANTES) --------
TIEMPO_ELEVADOR = 2000   # ms (2 segundos) #(recorrido mecánico estimado, que se pueden reemplazar por sensores de final de carrera, pero como prototipo tiempo fijo)

TIEMPO_LOOP = 50         # ms (frecuencia de control) #(frec control, f=1/0.05=20 Hz que ni sature ni consuma innecesariamente, dando control por tiempo no bloqueante)


# -------- SEGURIDAD --------
TIMEOUT_COMUNICACION = 5000   # ms sin recibir datos → fail-safe. #(si en este tiempo no hay datos, es que probablemente se haya perdido la conexión)


# -------- DEBUG --------
DEBUG = True
