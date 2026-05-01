# Visión Computacional - Red Neuronal (AGV)

Esta carpeta contiene todo lo relacionado al subsistema de visión artificial para la detección del AGV utilizando Inteligencia Artificial.

## Contenido

- `dataset/`: Carpeta que contiene las fotografías (más de 200 imágenes) recolectadas para entrenar el modelo. Estas imágenes sirven como base para que la red neuronal aprenda a reconocer el vehículo y el entorno.
- `best.pt`: Archivo de pesos del modelo entrenado. Este archivo es el resultado final del entrenamiento de la red neuronal (YOLOv8) y contiene el "conocimiento" necesario para detectar el AGV con precisión.
- `entrenamiento_agv.py`: Script de Python utilizado para realizar el entrenamiento de la red. En este código puedes explorar y modificar los parámetros de entrenamiento (mapeo, épocas, tamaño de imagen, conexión con Roboflow y uso de la librería Ultralytics) de donde se obtiene el modelo `best.pt`.
- `detectar_en_vivo.py`: Script de prueba que utiliza el modelo ya entrenado (`best.pt`) para detectar el AGV en tiempo real a través de una cámara (webcam o cámara conectada por USB). Al ejecutar este archivo, se abrirá una ventana mostrando lo que capta la cámara junto con los cuadros de detección sobre el objetivo.

## Uso

Para probar la red neuronal en vivo:
1. Asegúrate de tener instaladas las librerías necesarias (`ultralytics`, `opencv-python`).
2. Conecta la cámara y ejecuta:
   ```bash
   python detectar_en_vivo.py
   ```
3. Presiona la tecla `q` para salir de la ventana de detección.
