import numpy as np
import cv2

#  Tu matriz intrínseca K
K = np.array([[318.27250276,   0.        , 270.],
              [  0.        , 317.36291031, 250.],
              [  0.        ,   0.        ,   1.]])

#  Tu vector de distorsión
dist = np.array([ 0.01609359, -0.0019421,   0.00013425, -0.00270436, -0.05199842])

#  Punto en píxeles que quieres transformar (ejemplo)
pixel = np.array([[0.0, 0.0]], dtype=np.float32)  # (u, v)

#  Asumimos una profundidad conocida
Z = 0.33  # en metros (ajústala según tu caso)

#  1. Corregimos distorsión y normalizamos
undistorted = cv2.undistortPoints(pixel, K, dist, P=K)
x_norm, y_norm = undistorted[0][0]

#  2. Convertimos a coordenadas en el sistema de la cámara
X = x_norm * Z
Y = y_norm * Z

#  Resultado
print("Coordenadas 3D en el sistema de la cámara:")
print(f"X = {X:.4f} m")
print(f"Y = {Y:.4f} m")
print(f"Z = {Z:.4f} m (asumido)")