# vision_module.py
import shared_data
import cv2
import numpy as np
import matplotlib.pyplot as plt

class VisionModule:
    def __init__(self):
        pass

    def detectar_pieza(self, pieza_num=None, rotacion=0):
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("Error: no se pudo acceder a la cámara.")
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Error: no se pudo capturar la imagen.")
            return

        # Convertir a RGB y escala de grises
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Preprocesado: suavizado + detección de bordes
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 20, 90)

        # Crear una copia para visualizar resultados
        output = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        height, width = edges.shape

        # Buscar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        centroides = []

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            area = cv2.contourArea(cnt)

            if len(approx) == 4 and area > 1000:
                x, y, w, h = cv2.boundingRect(cnt)

                # Ignorar si toca los bordes de la imagen (figura incompleta)
                if x <= 5 or y <= 5 or (x + w) >= (width - 5) or (y + h) >= (height - 5):
                    continue

                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    centroides.append((cX, cY))
                    cv2.drawContours(output, [approx], 0, (0, 255, 0), 2)
                    cv2.circle(output, (cX, cY), 4, (0, 0, 255), -1)
                    cv2.putText(output, f"{cX},{cY}", (cX + 5, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        # Mostrar resultados
        plt.figure(figsize=(8, 8))
        plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
        plt.title("Centroides detectados")
        plt.axis("off")
        plt.show()

        print("Centroides encontrados:", centroides)




'''# Copia para dibujar resultados
        output = image_rgb.copy()


        # Detección de esquinas (Shi-Tomasi)
        corners = cv2.goodFeaturesToTrack(edges, maxCorners=100, qualityLevel=0.01, minDistance=10)
        if corners is not None:
            corners = np.intp(corners)
            for i in corners:
                x, y = i.ravel()
                cv2.circle(output, (x, y), 3, (255, 0, 0), -1)  # círculos azules en las esquinas

        # Detección de contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        centroides = []

        for cnt in contours:
            # Aproximar contorno a polígono
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            area = cv2.contourArea(cnt)

            # Filtrar cuadrados de tamaño adecuado
            if len(approx) == 4 and area > 1000:
                cv2.drawContours(output, [approx], 0, (0, 255, 0), 2)
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    centroides.append((cX, cY))
                    cv2.circle(output, (cX, cY), 5, (0, 0, 255), -1)
                    cv2.putText(output, f"{cX},{cY}", (cX+5, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Mostrar resultados
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 3, 1)
        plt.imshow(gray, cmap='gray')
        plt.title("Escala de grises")
        plt.axis('off')

        plt.subplot(1, 3, 2)
        plt.imshow(edges, cmap='gray')
        plt.title("Bordes (Canny)")
        plt.axis('off')

        plt.subplot(1, 3, 3)
        plt.imshow(output)
        plt.title("Esquinas y centroides")
        plt.axis('off')
        plt.show()

        # Guardado en shared_data
        shared_data.vision_output_pixel_coords = centroides
        shared_data.vision_output_piece_number = pieza_num
        shared_data.vision_output_rotation = rotacion

        print(f"Centroides detectados: {centroides}")
'''