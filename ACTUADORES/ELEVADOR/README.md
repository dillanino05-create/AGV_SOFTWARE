# ⬆️ Módulo de Elevación (`elevador.py`)

## 📌 Descripción

Este módulo controla el actuador de elevación del AGV, encargado de subir y bajar la carga.
Implementa una lógica basada en máquina de estados y control temporal no bloqueante, permitiendo su integración con el sistema principal sin afectar la ejecución concurrente.

---

## 🧠 Principio de Funcionamiento

El sistema se basa en:

* control digital de dirección (subir/bajar)
* temporización no bloqueante
* máquina de estados

### 🔄 Flujo de control

```text id="v0zjmk"
ESP32 → Señales digitales → Driver / Relé → Actuador → Movimiento vertical
```

---

## 📦 Importaciones

```python id="p6fp8k"
from machine import Pin
import time
import config
```

### 🧠 Explicación

* **Pin**: permite controlar salidas digitales del ESP32
* **time**: permite medir tiempo sin bloquear el sistema (`ticks_ms`)
* **config**: acceso a parámetros globales como `TIEMPO_ELEVADOR`

---

## 🔌 Configuración de Pines

```python id="j7z5d9"
motor_subir = Pin(25, Pin.OUT)
motor_bajar = Pin(26, Pin.OUT)
```

---

## ⚙️ Lógica de Control (Puente H / Relé)

| Subir | Bajar | Resultado  |
| ----- | ----- | ---------- |
| 1     | 0     | Sube       |
| 0     | 1     | Baja       |
| 0     | 0     | Stop       |
| 1     | 1     | ⚠️ PELIGRO |

### 🧠 Interpretación

* Se controla el sentido del actuador mediante dos señales digitales
* Activar ambas salidas simultáneamente puede generar:

  * cortocircuito
  * daño del hardware

✔ El diseño evita este estado

---

## 🔄 Máquina de Estados

```python id="4l9r68"
estado_elevador = "IDLE"
tiempo_inicio = 0
```

### 🧠 Estados definidos

| Estado   | Descripción            |
| -------- | ---------------------- |
| IDLE     | Elevador detenido      |
| SUBIENDO | Movimiento ascendente  |
| BAJANDO  | Movimiento descendente |

---

## 🛑 Control Básico

### 🔹 Detener elevador

```python id="g9i4c5"
def detener_elevador():
```

Desactiva ambas salidas → estado seguro.

---

### 🔹 Iniciar subida

```python id="bnr4dw"
def iniciar_subida():
```

Acciones:

* activa señal de subida
* desactiva señal de bajada
* cambia estado a `SUBIENDO`
* registra tiempo inicial

---

### 🔹 Iniciar bajada

```python id="1q7t7z"
def iniciar_bajada():
```

Acciones:

* activa señal de bajada
* desactiva señal de subida
* cambia estado a `BAJANDO`
* registra tiempo inicial

---

## ⏱️ Control No Bloqueante

```python id="3r7u2k"
def actualizar_elevador():
```

### 🧠 Propósito

Actualizar el estado del elevador en cada ciclo del sistema sin detener la ejecución del programa.

---

### 🔍 Funcionamiento

1. **Verificación de estado**

```python id="9df2c8"
if estado_elevador == "IDLE":
    return
```

Si no hay movimiento, no se ejecuta lógica adicional.

---

2. **Medición de tiempo**

```python id="p6p0ml"
tiempo_actual = time.ticks_ms()
tiempo_transcurrido = time.ticks_diff(tiempo_actual, tiempo_inicio)
```

### 🧠 Importante

* `ticks_diff` evita errores por overflow del contador
* método recomendado en sistemas embebidos

---

3. **Condición de parada**

```python id="bkj0kp"
if tiempo_transcurrido >= config.TIEMPO_ELEVADOR:
```

Cuando se cumple el tiempo estimado:

* se detiene el elevador
* se vuelve a estado `IDLE`

---

## 🔎 Consulta de Estado

```python id="2tfqjr"
def obtener_estado():
```

### 🧠 Propósito

Permite conocer el estado actual del elevador desde otros módulos.

---

## 🔗 Integración con el Sistema

Este módulo se integra con:

* **main.py** → ejecución principal
* **estados.py** → control lógico del AGV
* **comunicacion.py** → envío de estado por MQTT
* **HMI / SCADA** → visualización

---

## ⚠️ Consideraciones Importantes

### 1. Control en lazo abierto

El sistema no utiliza sensores, por lo que:

* no detecta posición real
* depende de un tiempo estimado

---

### 2. Precisión limitada

El tiempo de operación puede variar por:

* carga
* desgaste mecánico
* variaciones de voltaje

---

### 3. Mejora futura recomendada

Implementar sensores de fin de carrera:

```python id="y3r4o8"
sensor_arriba = Pin(...)
sensor_abajo = Pin(...)
```

---

## 🚀 Ventajas del Diseño

* no bloqueante
* modular
* seguro
* integrable
* escalable

---

## 🧠 Conclusión

El módulo `elevador.py` implementa un sistema de control de elevación basado en máquina de estados y temporización no bloqueante, permitiendo una operación segura y coordinada dentro del AGV.

Su diseño facilita la evolución hacia sistemas más avanzados mediante la incorporación de sensores y control en lazo cerrado.
