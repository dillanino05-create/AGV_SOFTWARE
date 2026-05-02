#main.py (INTEGRACIÓN)
# ================================
# MAIN: AGV - Sistema Principal
# ================================

import time
import config
import comunicacion
import estados

# -------- INICIALIZACIÓN --------

def setup():
    if config.DEBUG:
        print("Iniciando sistema AGV...")

    comunicacion.conectar()
    estados.inicializar()

    if config.DEBUG:
        print("Sistema listo")


# -------- LOOP PRINCIPAL --------

def loop():
    while True:

        # 1. Comunicación (MQTT)
        comunicacion.actualizar()

        # 2. Lógica del sistema (FSM)
        estados.actualizar()

        # 3. Enviar estado al servidor
        comunicacion.enviar_estado(estados.obtener_estado())

        # 4. Control de tiempo (NO BLOQUEANTE)
        time.sleep_ms(config.TIEMPO_LOOP)


# -------- EJECUCIÓN --------

try:
    setup()
    loop()

except Exception as e:
    if config.DEBUG:
        print("Error crítico:", e)

    # Estado seguro
    import motores
    motores.detener()


#POSBILE VISIÓN FINAL DEL SISTEMA
#          MQTT (WMS)
#              ↓
#     comunicacion.py
#              ↓
#         estados.py
#        ↙        ↘
# motores.py   elevador.py
#
#El archivo main implementa el ciclo principal del AGV, integrando comunicación, lógica de control y ejecución de actuadores en un esquema no bloqueante, permitiendo operación en tiempo real y cumpliendo con los requerimientos de un sistema distribuido tipo AS/RS.