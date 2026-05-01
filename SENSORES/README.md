# Sensores

Esta carpeta está reservada para el código de adquisición de datos de los sensores físicos del AGV.
Posteriormente, se agregarán aquí los scripts para leer y procesar la información de hardware como sensores ultrasónicos, infrarrojos, LiDAR, encoders, etc., complementando así el sistema de visión artificial.

# Detección de Color con TCS34725 (Arduino)

Implementación de detección de colores utilizando el sensor **TCS34725** con Arduino, aplicando normalización de valores RGB para mejorar la precisión frente a variaciones de iluminación.

## Descripción

Este proyecto permite identificar colores (rojo, verde, azul y amarillo) a partir de las lecturas del sensor **TCS34725**.
Se emplea el canal **clear (C)** para normalizar los valores RGB, lo cual reduce errores causados por cambios en la intensidad de la luz.
---
## Funcionamiento
El sensor proporciona cuatro valores:

- **R** → Rojo  
- **G** → Verde  
- **B** → Azul  
- **C** → Clear (intensidad total de luz)


Luego se aplican condiciones (umbrales) para determinar el color detectado.

---

##  Colores detectados

- 🔴 Rojo  
- 🟢 Verde  
- 🔵 Azul  
- 🟡 Amarillo  
- ⚪ Ninguno (cuando no se cumplen condiciones)

  
## Calibración

Los valores de detección pueden variar según:

- Iluminación ambiente  
- Distancia al objeto  
- Tipo de superficie  

Se recomienda usar el monitor serial para ajustar los umbrales (`rf`, `gf`, `bf`) y mejorar la precisión.

---

## Consideraciones

- Si el valor de **C (clear)** es muy bajo, no se detectará color  
- Cambios bruscos de luz afectan las lecturas  
- Los umbrales deben ajustarse en condiciones reales  

---

## Mejoras futuras

- Implementación de filtros para reducir ruido  
- Clasificación más precisa mediante distancia de color  
- Detección de más colores
