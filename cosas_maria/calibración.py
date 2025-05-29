import cv2
import numpy as np
import matplotlib.pyplot as plt

# Parámetros del tablero
chessboard_size = (7, 7)
square_size = 0.025  # en metros

# Puntos 3D del mundo (z = 0)
objp = np.zeros((chessboard_size[0]*chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0],
                      0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size

# Captura de imagen
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Detección de esquinas
ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

if ret:
    # Mejora precisión
    corners2 = cv2.cornerSubPix(
        gray, corners, (11, 11), (-1, -1),
        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    )

    # Calibración con una sola imagen (no ideal, pero posible)
    ret_calib, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        [objp], [corners2], gray.shape[::-1], None, None
    )

    # Mostrar resultados
    print("Matriz intrínseca (K):\n", K)
    print("Distorsión:\n", dist.ravel())

    # Mostrar imagen con esquinas detectadas
    frame_corners = cv2.drawChessboardCorners(frame, chessboard_size, corners2, True)
    image_rgb = cv2.cvtColor(frame_corners, cv2.COLOR_BGR2RGB)

    plt.imshow(image_rgb)
    plt.title("Tablero detectado")
    plt.axis('off')
    plt.show()

else:
    print("No se detectaron esquinas del tablero. Asegúrate de que el tablero esté visible y bien iluminado.")

