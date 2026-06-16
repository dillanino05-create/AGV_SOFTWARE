# Sensor de Línea QTR-8A

## Descripción

El sensor **QTR-8A** es un módulo de detección de líneas desarrollado por Pololu, utilizado principalmente en proyectos de robótica móvil como robots seguidores de línea. Está compuesto por una matriz de **8 sensores infrarrojos reflectivos** que permiten identificar diferencias de color o reflectancia en una superficie.

Su funcionamiento se basa en emitir luz infrarroja hacia la superficie y medir la cantidad de luz reflejada. Cuando el sensor apunta hacia una superficie clara, la reflexión es mayor; mientras que sobre una línea oscura, la reflexión disminuye. Con esta información el robot puede determinar la posición de una línea y corregir su trayectoria.

---

## Características principales

- **Cantidad de sensores:** 8 sensores infrarrojos.
- **Tipo de salida:** Analógica.
- **Voltaje de alimentación:** 3.3V a 5V.
- **Distancia de detección aproximada:** 0.5 mm a 4 mm.
- **Comunicación:** Lectura mediante entradas analógicas del microcontrolador.
- **Aplicaciones:** Robots seguidores de línea, sistemas de detección de objetos y automatización.

---

## Funcionamiento

Cada sensor infrarrojo del QTR-8A posee un emisor y un receptor:

1. El LED infrarrojo emite luz hacia la superficie.
2. La superficie refleja una cantidad de luz determinada.
3. El receptor mide esa reflexión.
4. El módulo entrega un valor analógico proporcional a la reflectancia.

Ejemplo:

- Superficie blanca → mayor reflexión → valor de lectura alto.
- Línea negra → menor reflexión → valor de lectura bajo.

El microcontrolador interpreta estos valores para conocer la posición de la línea.

---

## Pines del módulo

| Pin | Descripción |
|---|---|
| VCC | Alimentación del sensor (3.3V - 5V) |
| GND | Tierra |
| OUT 1 - OUT 8 | Salidas analógicas de cada sensor |

