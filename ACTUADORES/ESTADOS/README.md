# 🧠 Módulo de Máquina de Estados (`estados.py`)

## 📌 Descripción

Este módulo implementa la lógica de control del AGV mediante una **máquina de estados finita (FSM - Finite State Machine)**.
Actúa como el cerebro del sistema, transformando comandos recibidos en decisiones y acciones coordinadas sobre los actuadores.

---

## 🧠 Principio de Funcionamiento

El módulo sigue el flujo:

```text
COMANDOS (MQTT) → DECISIONES (FSM) → ACCIONES (Motores / Elevador)
```

---

## 📦 Importaciones

```python
import motores
import elevador
import comunicacion
import config
import time
```

### 🧠 Explicación

Este módulo **no controla hardware directamente**, sino que coordina:

* `motores` → movimiento
* `elevador` → manipulación de carga
* `comunicacion` → recepción de comandos

✔ separación de responsabilidades
✔ diseño modular

---

## 🔄 Definición de Estados

```python
IDLE = "IDLE"
MOVIENDO = "MOVIENDO"
CARGANDO = "CARGANDO"
DESCARGANDO = "DESCARGANDO"
ERROR = "ERROR"
```

---

### 🧠 Interpretación

| Estado      | Descripción             |
| ----------- | ----------------------- |
| IDLE        | AGV detenido            |
| MOVIENDO    | AGV en desplazamiento   |
| CARGANDO    | Elevador subiendo carga |
| DESCARGANDO | Elevador bajando carga  |
| ERROR       | Estado de fallo         |

---

## ⚙️ Variables de Estado

```python
estado_actual = IDLE
tiempo_estado = 0
```

### 🧠 Explicación

* **estado_actual**: indica qué está haciendo el AGV
* **tiempo_estado**: registra cuándo se entró al estado

---

### 🎯 Uso de `tiempo_estado`

Permite implementar:

* temporizadores
* detección de bloqueos
* watchdogs
* lógica de seguridad

---

## 🔁 Cambio de Estado

```python
def cambiar_estado(nuevo_estado):
```

---

### 🧠 Función

* actualiza el estado actual
* registra el tiempo de cambio

```python
estado_actual = nuevo_estado
tiempo_estado = time.ticks_ms()
```

---

### 🎯 Importancia

Permite:

* trazabilidad del sistema
* control temporal de estados
* depuración (debug)

---

## 🚀 Inicialización

```python
def inicializar():
    cambiar_estado(IDLE)
```

---

### 🧠 Propósito

Define el estado inicial seguro del sistema.

---

## 🔄 Lógica Principal (FSM)

```python
def actualizar():
```

---

### 🧠 Este es el núcleo del sistema

Se ejecuta continuamente desde `main.py`.

---

### 🔍 Flujo interno

1. **Lectura de comandos**

```python
accion, velocidad = comunicacion.obtener_comando()
```

---

2. **Evaluación del estado actual**

```python
if estado_actual == IDLE:
```

Cada estado tiene su propia lógica.

---

3. **Actualización de módulos dependientes**

```python
elevador.actualizar_elevador()
```

✔ ejecución concurrente
✔ sistema no bloqueante

---

## 🔧 Implementación de Estados

---

### 🔹 Estado IDLE

```python
def _estado_idle(accion, velocidad):
```

---

#### 🧠 Comportamiento

* detiene el AGV
* espera comandos

---

#### 🔄 Transiciones

| Comando         | Nuevo Estado |
| --------------- | ------------ |
| avanzar         | MOVIENDO     |
| retroceder      | MOVIENDO     |
| girar_izquierda | MOVIENDO     |
| girar_derecha   | MOVIENDO     |
| cargar          | CARGANDO     |
| descargar       | DESCARGANDO  |

---

### 🔹 Estado MOVIENDO

```python
def _estado_moviendo(accion, velocidad):
```

---

#### 🧠 Comportamiento

Ejecuta el movimiento según el comando recibido.

---

#### 🛑 Condición de parada

```python
if accion == "STOP" or accion is None:
```

👉 detiene el AGV y regresa a `IDLE`.

---

#### 🚗 Acciones

* avanzar
* retroceder
* girar izquierda
* girar derecha

---

### 🔹 Estado CARGANDO

```python
def _estado_cargando():
```

---

#### 🧠 Comportamiento

Espera a que el elevador termine su operación.

---

#### 🔄 Transición

```python
if elevador.obtener_estado() == "IDLE":
```

👉 vuelve a `IDLE`.

---

### 🔹 Estado DESCARGANDO

```python
def _estado_descargando():
```

---

#### 🧠 Comportamiento

Similar a `CARGANDO`, pero para descenso.

---

### 🔹 Estado ERROR

```python
def _estado_error():
```

---

#### 🧠 Comportamiento

* detiene el sistema
* permite implementar lógica futura

---

## 🔎 Consulta de Estado

```python
def obtener_estado():
```

---

### 🧠 Propósito

Permite que otros módulos (como `main.py` o MQTT) consulten el estado actual del AGV.

---

## 🔗 Integración del Sistema

```text
comunicacion → estados → motores / elevador
```

---

### 🧠 Arquitectura

* desacoplada
* modular
* escalable

---

## ⚠️ Consideraciones Importantes

### 1. Sistema reactivo

El AGV responde a eventos (comandos), no a secuencias fijas.

---

### 2. No bloqueante

No se utilizan `sleep()` largos, lo que permite:

* multitarea
* comunicación continua
* control fluido

---

### 3. Control centralizado

Toda la lógica pasa por este módulo, lo que facilita:

* mantenimiento
* escalabilidad
* depuración

---

## 🚀 Ventajas del Diseño

* arquitectura profesional (FSM)
* fácil integración
* control claro y estructurado
* preparado para expansión

---

## 🧠 Conclusión

El módulo `estados.py` implementa una máquina de estados finita que coordina los diferentes subsistemas del AGV, permitiendo un comportamiento reactivo, organizado y seguro ante los comandos recibidos.

Este enfoque es estándar en sistemas robóticos e industriales, y constituye la base para el desarrollo de funcionalidades avanzadas como navegación autónoma y control inteligente.
