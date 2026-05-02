# ⚙️ Módulo de Control de Motores (`motores.py`)

## 📌 Descripción

Este módulo implementa el control de tracción del AGV utilizando un driver L298N y un microcontrolador ESP32.
Permite controlar dirección y velocidad de cada motor de forma independiente mediante señales digitales y PWM.

---

## 🧠 Principio de Funcionamiento

El sistema separa el control en dos niveles:

* **Dirección** → controlada por pines digitales
* **Velocidad** → controlada por PWM

### 🔄 Flujo de control

```text
ESP32 → Señales digitales + PWM → Driver L298N → Motores
```

---

## 📦 Importaciones

```python
from machine import Pin, PWM
import config
```

### 🧠 Explicación

* **Pin**: permite controlar salidas digitales del ESP32
* **PWM**: genera señales moduladas para controlar velocidad
* **config**: centraliza parámetros como frecuencia PWM y límites de velocidad

---

## 🔌 Configuración de Pines

### 🔹 Motor Izquierdo (Canal A)

```python
IN1 = Pin(5, Pin.OUT)
IN2 = Pin(18, Pin.OUT)
ENA = PWM(Pin(23), freq=config.PWM_FREQ)
```

### 🔹 Motor Derecho (Canal B)

```python
IN3 = Pin(19, Pin.OUT)
IN4 = Pin(21, Pin.OUT)
ENB = PWM(Pin(22), freq=config.PWM_FREQ)
```

---

## ⚙️ Lógica de Dirección (Puente H - L298N)

| IN1 | IN2 | Resultado |
| --- | --- | --------- |
| 1   | 0   | Avanza    |
| 0   | 1   | Retrocede |
| 0   | 0   | Stop      |

### 🧠 Interpretación

El L298N invierte la polaridad del motor según la combinación de entradas, lo que permite cambiar el sentido de giro.

---

## 🚫 Limitación de Velocidad

```python
def _limitar_velocidad(vel):
```

### 🧠 Propósito

Garantiza que la velocidad se mantenga dentro del rango permitido:

[
-VELOCIDAD_MAX \leq vel \leq VELOCIDAD_MAX
]

### 🎯 Importancia

Evita:

* valores fuera de rango
* comportamientos erráticos
* posibles daños en hardware

### 📌 Ejemplo

```python
avanzar(5000) → se limita automáticamente a 1023
```

---

## 🔄 Control de Motores Individuales

### 🔹 Motor Izquierdo

```python
def motor_izquierdo(vel):
```

### 🔹 Motor Derecho

```python
def motor_derecho(vel):
```

---

## 🧠 Lógica de Funcionamiento

### 1. Limitación de velocidad

```python
vel = _limitar_velocidad(vel)
```

---

### 2. Dirección

* **vel > 0** → avance
* **vel < 0** → reversa
* **vel = 0** → stop

---

### 3. Conversión de signo

```python
vel = -vel
```

Se convierte a valor positivo porque:

* el PWM no acepta valores negativos
* la dirección ya está definida por los pines

---

### 4. Aplicación de PWM

```python
ENA.duty(int(vel))
```

### 🧠 Importante

* PWM en ESP32 trabaja con valores enteros
* rango típico: 0 – 1023

---

## 🚗 Movimientos del AGV

### 🔹 Avanzar

```python
def avanzar(vel=config.VELOCIDAD_DEFAULT):
```

Ambos motores giran en el mismo sentido.

---

### 🔹 Retroceder

```python
def retroceder(vel=config.VELOCIDAD_DEFAULT):
```

Ambos motores giran en sentido inverso.

---

### 🔹 Girar Izquierda

```python
def girar_izquierda(vel=config.VELOCIDAD_DEFAULT):
```

* motor izquierdo → reversa
* motor derecho → avance

---

### 🔹 Girar Derecha

```python
def girar_derecha(vel=config.VELOCIDAD_DEFAULT):
```

* motor izquierdo → avance
* motor derecho → reversa

---

### 🔹 Detener

```python
def detener():
```

Ambos motores se desactivan.

---

## ⚙️ Control Diferencial (Nivel Avanzado)

```python
def mover_diferencial(vel_izq, vel_der):
```

### 🧠 Propósito

Permite controlar cada rueda de forma independiente.

---

## 🚀 Aplicaciones

Esta función es la base para:

* navegación autónoma
* control de trayectoria
* seguimiento de línea
* integración con encoders
* implementación de control PID

---

## 🔥 Arquitectura del Movimiento

```text
vel_izq ≠ vel_der → cambio de trayectoria
vel_izq = vel_der → movimiento recto
```

---

## ⚠️ Consideraciones Importantes

### 1. Control en lazo abierto

Este módulo NO utiliza retroalimentación:

* no mide velocidad real
* no corrige desviaciones

---

### 2. Dependencia mecánica

El comportamiento real depende de:

* fricción
* peso de carga
* estado de baterías

---

### 3. PWM no lineal

La relación PWM–velocidad no es perfectamente proporcional.

---

## 🧠 Conclusión

El módulo `motores.py` implementa un sistema de control de tracción robusto y modular, basado en control PWM y lógica de puente H, permitiendo el movimiento diferencial del AGV.

Su diseño facilita la integración futura de sistemas de control avanzados como navegación autónoma y control en lazo cerrado mediante encoders.
