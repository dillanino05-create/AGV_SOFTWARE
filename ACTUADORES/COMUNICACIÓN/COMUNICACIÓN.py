#comunicacion.py 
# ================================
# MODULO: comunicacion.py
# Comunicación AGV ↔ WMS (MQTT)
# ================================

from umqtt.simple import MQTTClient # cliente ligero MQTT para MicroPython para un bajo consumo e ideal para ESP32
import ujson # parser JSON rápido con menor uso de memoria, necesario para cumplir contrato (JSON)
import config
import time


# -------- VARIABLES GLOBALES --------

client = None
estado_actual = {
    "estado": "IDLE",
    "accion": None,
    "velocidad": 0
}

ultimo_mensaje = 0
#se utiliza un diccionario ya que se trabajan con múltiples datos, para poder tener una estructura que sea flexible.
# Ej:
#{
#  "accion": "avanzar",
#  "velocidad": 500
#}


# -------- CONEXIÓN --------

def conectar():
    global client

    client = MQTTClient(
        client_id=config.CLIENT_ID,
        server=config.MQTT_BROKER,
        port=config.MQTT_PORT
    )
#CRECAIÓN DEL CLIENTE

    client.set_callback(_callback_mensaje) # función que se ejecuta al recibir datos
    client.connect()
    client.subscribe(config.TOPIC_CMD) # RECIBE órdenes del WMS

    if config.DEBUG:
        print("Conectado a MQTT")


# -------- CALLBACK (RECEPCIÓN) --------

def _callback_mensaje(topic, msg):
    global estado_actual, ultimo_mensaje

    ultimo_mensaje = time.ticks_ms()

    try:
        data = ujson.loads(msg)

        estado_actual["accion"] = data.get("accion")
        estado_actual["velocidad"] = data.get("velocidad", config.VELOCIDAD_DEFAULT)

        if config.DEBUG:
            print("Mensaje recibido:", data)

    except Exception as e:
        if config.DEBUG:
            print("Error JSON:", e)


# -------- ACTUALIZACIÓN (NO BLOQUEANTE) --------

def actualizar():
    global ultimo_mensaje

    try:
        client.check_msg()
    except:
        reconectar()

    # Verificación de timeout
    tiempo_actual = time.ticks_ms()
    if time.ticks_diff(tiempo_actual, ultimo_mensaje) > config.TIMEOUT_COMUNICACION:
        estado_actual["accion"] = "STOP"


# -------- ENVÍO DE ESTADO --------

def enviar_estado(estado, extra=None):
    payload = {
        "estado": estado,
        "timestamp": time.ticks_ms()
    }

    if extra:
        payload.update(extra)

    try:
        client.publish(config.TOPIC_STATUS, ujson.dumps(payload))

        if config.DEBUG:
            print("Estado enviado:", payload)

    except:
        reconectar()


# -------- RECONEXIÓN --------

def reconectar():
    if config.DEBUG:
        print("Reconectando MQTT...")

    try:
        conectar()
    except:
        if config.DEBUG:
            print("Fallo reconexión")


# -------- CONSULTA --------

def obtener_comando():
    return estado_actual["accion"], estado_actual["velocidad"]
