# ⚙️ Configuración Global del AGV (`config.py`)

## 📌 Descripción

Este archivo define los parámetros globales del sistema AGV, incluyendo comunicación, control de motores, temporización y seguridad.
Su propósito es centralizar la configuración para facilitar la escalabilidad, mantenimiento y ajuste del sistema sin modificar la lógica principal.

---

## 🌐 Configuración de Comunicación (MQTT)

```python
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
CLIENT_ID = "AGV_01"
```

### 🧠 Explicación

* **MQTT_BROKER**: Dirección IP del servidor MQTT dentro de la red local (LAN).
  Se utiliza una IP del rango `192.168.x.x`, típica en redes domésticas o de laboratorio, lo que garantiza:

  * baja latencia
  * independencia de internet

* **MQTT_PORT**: Puerto estándar (1883) para MQTT sin cifrado.
  Es ideal para prototipos por ser:

  * simple
  * rápido
  * ligero

* **CLIENT_ID**: Identificador único del AGV dentro del sistema.
  Permite distinguir múltiples robots en un entorno distribuido:

  * AGV_01
  * AGV_02
  * AGV_03

### 🎯 Cumplimiento del sistema

Este bloque permite:

* comunicación por red
* identificación única del AGV
* integración con sistemas WMS

---

## 📡 Topics MQTT

```python
TOPIC_CMD = "agv/cmd"
TOPIC_STATUS = "agv/status"
```

### 🧠 Explicación

Se define una arquitectura basada en publicación/suscripción:

* **TOPIC_CMD** → canal de entrada (comandos del sistema central)
* **TOPIC_STATUS** → canal de salida (estado del AGV)

### 🎯 Importancia

Esta separación permite:

* desacoplamiento del sistema
* comunicación bidireccional
* integración en sistemas AS/RS distribuidos

---

## 🧾 Formato de Mensajes

```python
USE_JSON = True
```

### 🧠 Explicación

Se utiliza JSON como formato estándar de comunicación, lo que permite estructurar los datos de forma clara y extensible.

### 📌 Ejemplo

```json
{
  "accion": "avanzar",
  "velocidad": 600
}
```

### 🎯 Ventajas

* legibilidad
* interoperabilidad
* escalabilidad

---

## ⚡ Configuración de Motores (PWM)

```python
PWM_FREQ = 1000
PWM_MAX = 1023
PWM_MIN = 0
```

### 🧠 Explicación

* **PWM_FREQ = 1000 Hz**
  Frecuencia seleccionada como punto de equilibrio:

  * evita vibraciones (frecuencias bajas)
  * evita pérdidas y calentamiento (frecuencias altas)

* **PWM_MAX = 1023**
  Resolución de 10 bits del ESP32:
  [
  2^{10} = 1024 \Rightarrow 0 - 1023
  ]

* **PWM_MIN = 0**
  Valor mínimo (motor detenido)

---

## 🚗 Configuración de Velocidad

```python
VELOCIDAD_DEFAULT = 600
VELOCIDAD_MAX = 1023
```

### 🧠 Explicación

* **VELOCIDAD_DEFAULT = 600**
  Aproximadamente el 58% del máximo:
  [
  \frac{600}{1023} \approx 0.58
  ]

  Esto permite:

  * suficiente torque
  * estabilidad en movimiento
  * evitar caídas de voltaje

* **VELOCIDAD_MAX**
  Límite físico del sistema PWM

---

## ⏱️ Tiempos del Sistema (No Bloqueante)

```python
TIEMPO_ELEVADOR = 2000
TIEMPO_LOOP = 50
```

### 🧠 Explicación

* **TIEMPO_ELEVADOR = 2000 ms**
  Tiempo estimado para completar el recorrido del elevador.
  En sistemas avanzados puede reemplazarse por sensores de fin de carrera.

* **TIEMPO_LOOP = 50 ms**
  Define la frecuencia de ejecución del sistema:

[
f = \frac{1}{0.05} = 20 \text{ Hz}
]

### 🎯 Importancia

* permite control no bloqueante
* mantiene equilibrio entre rendimiento y consumo

---

## 🛡️ Seguridad del Sistema

```python
TIMEOUT_COMUNICACION = 5000
```

### 🧠 Explicación

Si el AGV no recibe comandos en 5 segundos:

👉 se asume pérdida de comunicación

### 🎯 Acción esperada

* detener el robot
* evitar comportamientos peligrosos

---

## 🐞 Modo Debug

```python
DEBUG = True
```

### 🧠 Explicación

Activa mensajes de diagnóstico en consola.

### 🎯 Uso

* desarrollo
* pruebas
* monitoreo

En producción se recomienda:

```python
DEBUG = False
```

---

## 🧠 Conclusión

El archivo `config.py` centraliza todos los parámetros críticos del AGV, permitiendo:

* modularidad
* escalabilidad
* fácil mantenimiento
* cumplimiento de requisitos de comunicación y control

Esto es fundamental en sistemas mecatrónicos modernos basados en arquitectura distribuida.
