# 📡 Módulo de Comunicación (`comunicacion.py`)

## 📌 Descripción

Este módulo implementa la comunicación del AGV con el sistema central (WMS) mediante el protocolo MQTT.
Permite recibir comandos en tiempo real y enviar el estado del robot, utilizando mensajes estructurados en formato JSON.

---

## 🧠 Principio de Funcionamiento

El sistema utiliza el modelo **publish/subscribe** de MQTT:

```text
WMS → (TOPIC_CMD) → AGV
AGV → (TOPIC_STATUS) → WMS
```

---

## 📦 Importaciones

```python
from umqtt.simple import MQTTClient
import ujson
import config
import time
```

### 🧠 Explicación

* **MQTTClient**: cliente ligero MQTT para MicroPython

  * bajo consumo
  * ideal para ESP32

* **ujson**: parser JSON optimizado

  * menor uso de memoria
  * alta velocidad

* **config**: acceso a parámetros globales (broker, topics, timeout)

* **time**: manejo de tiempo no bloqueante

---

## 🌐 Variables Globales

```python
client = None

estado_actual = {
    "estado": "IDLE",
    "accion": None,
    "velocidad": 0
}

ultimo_mensaje = 0
```

---

### 🧠 Explicación

* **client**: instancia del cliente MQTT
* **estado_actual**: estructura que almacena el último comando recibido
* **ultimo_mensaje**: timestamp del último mensaje recibido

---

### 📌 Estructura de datos

```json
{
  "accion": "avanzar",
  "velocidad": 500
}
```

---

## 🔌 Conexión MQTT

```python
def conectar():
```

### 🧠 Funcionalidad

1. Crea el cliente MQTT
2. Configura callback de recepción
3. Se conecta al broker
4. Se suscribe al topic de comandos

---

### 🔍 Detalles clave

```python
client = MQTTClient(...)
```

👉 Inicializa el cliente con parámetros del archivo `config.py`.

---

```python
client.set_callback(_callback_mensaje)
```

👉 Define la función que se ejecutará cuando llegue un mensaje.

---

```python
client.subscribe(config.TOPIC_CMD)
```

👉 Permite recibir órdenes del sistema WMS.

---

## 📥 Recepción de Mensajes (Callback)

```python
def _callback_mensaje(topic, msg):
```

---

### 🧠 Función principal

Se ejecuta automáticamente cuando llega un mensaje MQTT.

---

### 🔍 Procesos realizados

1. **Registro de tiempo**

```python
ultimo_mensaje = time.ticks_ms()
```

👉 Permite detectar pérdida de comunicación.

---

2. **Parseo JSON**

```python
data = ujson.loads(msg)
```

---

3. **Extracción de datos**

```python
estado_actual["accion"] = data.get("accion")
estado_actual["velocidad"] = data.get("velocidad", config.VELOCIDAD_DEFAULT)
```

---

### 🧠 Importante

* `.get()` evita errores si faltan claves
* se usa velocidad por defecto si no se especifica

---

### ⚠️ Manejo de errores

```python
except Exception as e:
```

Evita que un mensaje mal formado detenga el sistema.

---

## 🔄 Actualización No Bloqueante

```python
def actualizar():
```

---

### 🧠 Propósito

Permitir la recepción de mensajes sin bloquear el sistema principal.

---

### 🔍 Funcionamiento

1. **Verificación de mensajes**

```python
client.check_msg()
```

👉 Procesa mensajes entrantes.

---

2. **Reconexión automática**

```python
except:
    reconectar()
```

👉 Maneja fallos de conexión.

---

3. **Timeout de seguridad**

```python
if tiempo > TIMEOUT:
    estado_actual["accion"] = "STOP"
```

---

### 🎯 Importancia

Si no hay comunicación:

👉 el AGV se detiene automáticamente

✔ comportamiento seguro

---

## 📤 Envío de Estado

```python
def enviar_estado(estado, extra=None):
```

---

### 🧠 Función

Envía el estado actual del AGV al sistema central.

---

### 🔍 Estructura del mensaje

```json
{
  "estado": "MOVIENDO",
  "timestamp": 123456
}
```

---

### 🔧 Extensibilidad

```python
if extra:
    payload.update(extra)
```

Permite agregar información adicional:

```json
{
  "estado": "MOVIENDO",
  "posicion": [10, 20]
}
```

---

## 🔁 Reconexión Automática

```python
def reconectar():
```

---

### 🧠 Propósito

Restablecer la conexión en caso de fallo.

---

### 🎯 Importancia

Las redes WiFi pueden fallar, por lo que:

✔ evita pérdida total del sistema
✔ mejora robustez

---

## 🔎 Consulta de Comando

```python
def obtener_comando():
```

---

### 🧠 Función

Devuelve:

```python
accion, velocidad
```

---

### 🎯 Uso

Permite que otros módulos (como `estados.py`) accedan a los comandos sin depender directamente de MQTT.

✔ desacoplamiento del sistema

---


## 🚀 Ventajas del Diseño

* no bloqueante
* robusto (reconexión automática)
* seguro (timeout → STOP)
* modular
* escalable

---

## 🧠 Conclusión

El módulo `comunicacion.py` implementa un sistema de comunicación basado en MQTT que permite la interacción en tiempo real entre el AGV y el sistema WMS.

Su diseño garantiza robustez, seguridad y escalabilidad, cumpliendo con los requisitos de un sistema distribuido moderno en aplicaciones tipo AS/RS.
