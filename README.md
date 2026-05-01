# Proyecto AGV - Software

Bienvenido al repositorio principal de software para el proyecto de Vehículo Guiado Autónomo (AGV). 
Este repositorio centraliza todos los componentes de código necesarios para el funcionamiento del AGV, estructurados en módulos especializados.

## Estructura del Proyecto

El código está dividido en las siguientes carpetas:

- **RED_NEURONAL**: Contiene todo lo relacionado con la Inteligencia Artificial y Visión Computacional. Aquí se encuentra el dataset de imágenes, el modelo entrenado (`best.pt`) y los scripts para entrenamiento y detección en vivo del AGV usando YOLOv8.
- **ACTUADORES**: (En desarrollo) Contendrá el código para el manejo de motores y cualquier otro componente de acción física del vehículo.
- **CONTROL**: (En desarrollo) Alojará la lógica de navegación, control de trayectorias, y algoritmos de estabilización o evasión de obstáculos.
- **SENSORES**: (En desarrollo) Incluirá los drivers y scripts para la adquisición de datos de sensores adicionales (ultrasónicos, infrarrojos, LiDAR, etc.).

## Estado Actual
Actualmente, el sistema principal implementado es la **Red Neuronal** para detección por visión artificial. Las secciones de control, actuadores y sensores se irán completando a medida que se desarrolle e integre el hardware correspondiente.
