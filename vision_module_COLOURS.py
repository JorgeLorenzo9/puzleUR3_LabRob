import cv2
import numpy as np
import matplotlib.pyplot as plt

# Diccionario de colores con nombres y rangos HSV iniciales
colores = {
    "Rosa":    {"bajo": [160, 50, 80], "alto": [180, 200, 255]},
    "Naranja": {"bajo": [5, 150, 150], "alto": [15, 255, 255]},
    "Amarillo":{"bajo": [20, 100, 100], "alto": [35, 255, 255]},
    "Verde":   {"bajo": [40, 50, 50], "alto": [90, 255, 255]},
    "Azul":    {"bajo": [100, 150, 50], "alto": [130, 255, 255]},
    "Lila":    {"bajo": [130, 80, 80], "alto": [160, 255, 255]}
}

# Distancia mínima entre centroides
DISTANCIA_MINIMA = 100

def filtrar_centroides(centroides, distancia_min=DISTANCIA_MINIMA):
    final = []
    for c in centroides:
        if all(np.linalg.norm(np.array(c) - np.array(f)) >= distancia_min for f in final):
            final.append(c)
        if len(final) == 9:
            break
    return final

def detectar_por_color(frame, nombre_color, bajo, alto):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(bajo), np.array(alto))
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centroides = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 800:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centroides.append((cX, cY))
    
    return mask, centroides

def ajustar_color_live(nombre_color, frame):
    def nothing(x): pass
    cv2.namedWindow(f"Ajustar {nombre_color}")

    color = colores[nombre_color]
    for c in ["H", "S", "V"]:
        cv2.createTrackbar(f"{c} min", f"Ajustar {nombre_color}", color["bajo"]["HSV".index(c)], 180 if c == "H" else 255, nothing)
        cv2.createTrackbar(f"{c} max", f"Ajustar {nombre_color}", color["alto"]["HSV".index(c)], 180 if c == "H" else 255, nothing)

    while True:
        h_min = cv2.getTrackbarPos("H min", f"Ajustar {nombre_color}")
        s_min = cv2.getTrackbarPos("S min", f"Ajustar {nombre_color}")
        v_min = cv2.getTrackbarPos("V min", f"Ajustar {nombre_color}")
        h_max = cv2.getTrackbarPos("H max", f"Ajustar {nombre_color}")
        s_max = cv2.getTrackbarPos("S max", f"Ajustar {nombre_color}")
        v_max = cv2.getTrackbarPos("V max", f"Ajustar {nombre_color}")

        mask, _ = detectar_por_color(frame, nombre_color, [h_min, s_min, v_min], [h_max, s_max, v_max])
        resultado = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.imshow(f"Ajustar {nombre_color}", resultado)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # Esc o 'q' para salir
            colores[nombre_color]["bajo"] = [h_min, s_min, v_min]
            colores[nombre_color]["alto"] = [h_max, s_max, v_max]
            break

    cv2.destroyWindow(f"Ajustar {nombre_color}")

def main():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Error: No se pudo capturar imagen.")
        return

    frame_mostrar = frame.copy()
    todos_centroides = []

    for nombre_color in colores.keys():
        ajustar_color_live(nombre_color, frame)
        mask, centroides = detectar_por_color(frame, nombre_color, colores[nombre_color]["bajo"], colores[nombre_color]["alto"])

        for cx, cy in centroides:
            cv2.circle(frame_mostrar, (cx, cy), 7, (0, 255, 0), -1)
            cv2.putText(frame_mostrar, nombre_color, (cx+10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Mostrar máscara de cada color
        plt.figure()
        plt.imshow(mask, cmap='gray')
        plt.title(f'Máscara - {nombre_color}')
        plt.axis('off')

        todos_centroides.extend(centroides)

    centroides_finales = filtrar_centroides(todos_centroides)

    # Dibujar sólo los centroides finales
    for cx, cy in centroides_finales:
        cv2.drawMarker(frame_mostrar, (cx, cy), (255, 0, 0), markerType=cv2.MARKER_CROSS, markerSize=15, thickness=2)

    plt.figure()
    plt.imshow(cv2.cvtColor(frame_mostrar, cv2.COLOR_BGR2RGB))
    plt.title("Centroides finales (máx 9, filtrados)")
    plt.axis('off')
    plt.show()

    print(f"Centroides detectados (filtrados): {centroides_finales}")

if __name__ == "__main__":
    main()
