# 🚀 Módulo Principal (`main.py`)

## 📌 Descripción

Este archivo implementa el ciclo principal del AGV, integrando todos los módulos del sistema:

* comunicación (MQTT)
* lógica de control (máquina de estados)
* ejecución de actuadores

Su diseño sigue un esquema **no bloqueante**, permitiendo operación en tiempo real y cumpliendo con los requerimientos de un sistema distribuido tipo AS/RS.

---

## 🧠 Arquitectura del Sistema

```text id="z6r2pf"
          MQTT (WMS)
              ↓
     comunicacion.py
              ↓
         estados.py
        ↙        ↘
 motores.py   elevador.py
```

---

## 📦 Importaciones

```python id="5cb7ff"
import time
import config
import comunicacion
import estados
```

### 🧠 Explicación

* **time** → control de temporización
* **config** → parámetros globales
* **comunicacion** → interfaz con WMS
* **estados** → cerebro lógico del AGV

---

## ⚙️ Inicialización del Sistema

```python id="2r2y2b"
def setup():
```

---

### 🧠 Función

Configura el sistema antes de iniciar el ciclo principal.

---

### 🔍 Flujo interno

1. **Mensaje de inicio (debug)**

```python id="d8z4pd"
print("Iniciando sistema AGV...")
```

---

2. **Conexión MQTT**

```python id="vub5l3"
comunicacion.conectar()
```

👉 Establece comunicación con el WMS.

---

3. **Inicialización de estados**

```python id="1uvc2g"
estados.inicializar()
```

👉 Define el estado inicial (`IDLE`).

---

4. **Confirmación de sistema listo**

```python id="dc1z6q"
print("Sistema listo")
```

---

## 🔄 Loop Principal

```python id="s9yx5o"
def loop():
    while True:
```

---

## 🧠 Este es el corazón del AGV

Se ejecuta continuamente y coordina todos los módulos.

---

## 🔍 Flujo de ejecución

---

### 1. Comunicación (MQTT)

```python id="c8qkz4"
comunicacion.actualizar()
```

👉 Recibe comandos del WMS.

✔ no bloqueante
✔ maneja reconexión
✔ aplica timeout de seguridad

---

### 2. Lógica del sistema (FSM)

```python id="qwxh7z"
estados.actualizar()
```

👉 Interpreta comandos y decide acciones.

✔ máquina de estados
✔ control centralizado

---

### 3. Envío de estado

```python id="zj6w8r"
comunicacion.enviar_estado(estados.obtener_estado())
```

👉 Reporta el estado actual al sistema central.

✔ monitoreo en tiempo real
✔ trazabilidad

---

### 4. Control de tiempo

```python id="ux1g9n"
time.sleep_ms(config.TIEMPO_LOOP)
```

---

### 🧠 Importante

Define la frecuencia del sistema:

[
f = \frac{1}{TIEMPO_LOOP}
]

Ejemplo:

[
50\ ms → 20\ Hz
]

---

### 🎯 Propósito

* evita saturación del CPU
* mantiene control estable
* permite multitarea

---

## ▶️ Ejecución del Sistema

```python id="5w7fl9"
try:
    setup()
    loop()
```

---

### 🧠 Flujo

1. Inicializa el sistema
2. entra en ejecución continua

---

## ⚠️ Manejo de Errores Críticos

```python id="c3h6c6"
except Exception as e:
```

---

### 🧠 Comportamiento

Si ocurre un error:

* se imprime diagnóstico (debug)
* se ejecuta estado seguro

---

### 🛑 Estado seguro

```python id="3l0yjl"
import motores
motores.detener()
```

👉 detiene el AGV inmediatamente

✔ seguridad física
✔ prevención de daños

---

## 🔗 Integración del Sistema

El `main.py` conecta todos los módulos:

| Módulo       | Función                 |
| ------------ | ----------------------- |
| comunicacion | recibe/envía datos MQTT |
| estados      | toma decisiones         |
| motores      | ejecuta movimiento      |
| elevador     | manipula carga          |

---

## ⚠️ Consideraciones Importantes

### 1. Sistema en tiempo real (soft real-time)

* respuesta rápida
* no determinismo absoluto

---

### 2. No bloqueante

No se utilizan delays largos:

✔ permite comunicación continua
✔ evita congelamiento del sistema

---

### 3. Dependencia del loop

Todo el sistema depende de:

```python id="yqv9w0"
while True:
```

👉 si falla, el sistema se detiene

---

## 🚀 Ventajas del Diseño

* arquitectura modular
* ejecución continua
* integración clara
* fácil mantenimiento
* escalable

---

## 🧠 Conclusión

El archivo `main.py` implementa el ciclo principal del AGV, integrando comunicación, lógica de control y ejecución de actuadores en un esquema no bloqueante.

Este enfoque permite una operación eficiente, segura y escalable, cumpliendo con los principios de diseño de sistemas mecatrónicos modernos y arquitecturas distribuidas tipo AS/RS.
