import cv2
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0)

ret, frame = cap.read()
cap.release()


# Convertir a RGB (OpenCV usa BGR por defecto)
image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

plt.figure("Paso 1 - Imagen original")
plt.imshow(image_rgb)
plt.title("Imagen original (RGB)")
plt.axis('off')

plt.show()