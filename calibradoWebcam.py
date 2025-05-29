import cv2
import numpy as np
import os
import glob

# ---------- PARÁMETROS ----------
chessboard_size = (7, 7)     # Esquinas interiores (horizontal, vertical)
square_size = 2.5            # Tamaño real de cada cuadro del tablero (cm, mm, etc.)
save_path = "calibration_images"
os.makedirs(save_path, exist_ok=True)

# ---------- CAPTURA CON DETECCIÓN EN VIVO ----------
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
count = 0

print("Presiona 's' para guardar imágenes con el tablero detectado, 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] No se pudo leer la cámara.")
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    vis = frame.copy()
    if found:
        cv2.drawChessboardCorners(vis, chessboard_size, corners, found)

    cv2.imshow("Vista previa - pulsa 's' para guardar", vis)
    key = cv2.waitKey(1)

    if key == ord("s") and found:
        img_name = f"{save_path}/img_{count}.png"
        cv2.imwrite(img_name, frame)
        print(f"[OK] Imagen guardada: {img_name}")
        count += 1
    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

# ---------- CALIBRACIÓN ----------
print("\n[INFO] Iniciando calibración...")

objp = np.zeros((np.prod(chessboard_size), 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size

objpoints = []  # Puntos 3D en el mundo real
imgpoints = []  # Puntos 2D en la imagen

images = glob.glob(f'{save_path}/*.png')
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        print(f"[OK] Esquinas detectadas en {fname}")
    else:
        print(f"[ERROR] No se detectaron esquinas en {fname}")

# ---------- VERIFICACIÓN ANTES DE CALIBRAR ----------
if len(objpoints) == 0 or len(imgpoints) == 0:
    print("[ERROR] No se detectaron suficientes esquinas. Asegúrate de capturar imágenes válidas.")
    exit()

# ---------- EJECUCIÓN DE CALIBRACIÓN ----------
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print("\n--- RESULTADOS DE CALIBRACIÓN ---")
print("Matriz de cámara:\n", mtx)
print("Coeficientes de distorsión:\n", dist.ravel())

np.savez("calibration_data.npz", mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

# ---------- PRUEBA DE CORRECCIÓN DE DISTORSIÓN ----------
img = cv2.imread(images[0])
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]

cv2.imshow("Original", img)
cv2.imshow("Corregida", dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
