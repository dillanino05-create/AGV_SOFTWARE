import os
from ultralytics import YOLO
import cv2

# Obtener la ruta absoluta de la carpeta donde está este script
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'best.pt')

# 1. Cargar tu "cerebro"
print("Cargando modelo...")
model = YOLO(model_path) 

cap = cv2.VideoCapture(3)

print("Cámara encendida. Muestra el AGV. Presiona la tecla 'q' para salir.")

while cap.isOpened():
    # Leer un frame (una foto) del video
    success, frame = cap.read()
    if not success:
        print("Ignorando frame vacío de la cámara.")
        continue

    # 3. La IA analiza el frame
    resultados = model(frame, verbose=False)

    # 4. Dibujar el cuadrito sobre el video
    video_con_cuadritos = resultados[0].plot()

    # Mostrar la ventana con el video
    cv2.imshow("Vision Artificial - AGV Software", video_con_cuadritos)

    # Si presionas 'q', se cierra el programa
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Apagar cámara y cerrar ventanas
cap.release()
cv2.destroyAllWindows()