import cv2
import numpy as np
from skimage.morphology import disk, erosion, dilation

# Inicializar la webcam
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convertir a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Rango para color morado (ajustar según necesidad)
    lower_purple = np.array([120, 50, 50])
    upper_purple = np.array([130, 200, 200])
    
    # Crear máscara
    mask = cv2.inRange(hsv, lower_purple, upper_purple)
    
    # Operaciones morfológicas
    se = disk(5)
    mask_eroded = erosion(mask, se)
    se2 = disk(15)
    mask_dilated = dilation(mask_eroded, se2)
    
    # Convertir a tipo uint8 para visualización
    mask_eroded = (mask_eroded).astype(np.uint8)
    mask_dilated = (mask_dilated).astype(np.uint8)
    
    # Aplicar máscara al frame original
    res = cv2.bitwise_and(frame, frame, mask=mask_dilated)
    
    # Encontrar contornos en la máscara dilatada
    contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Dibujar contornos y centroides
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # Filtrar por área mínima
            # Dibujar contorno
            cv2.drawContours(frame, [cnt], -1, (255, 0, 0), 2)
            
            # Calcular centroide
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
    
    # Mostrar todas las ventanas
    cv2.imshow('Original', frame)
    cv2.imshow('HSV', hsv)
    cv2.imshow('Mask', mask)
    cv2.imshow('Eroded', mask_eroded)
    cv2.imshow('Dilated', mask_dilated)
    cv2.imshow('Result', res)
    
    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()