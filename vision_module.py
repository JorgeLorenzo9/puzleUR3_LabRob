import shared_data
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops

class VisionModule:
    def __init__(self):
        pass

    def detectar_pieza(self, pieza_num=None, pixel_x=None, pixel_y=None, rotacion=0):
        # Captura desde la cámara
        cap = cv2.VideoCapture(1)

        if not cap.isOpened():
            print("Error: no se pudo acceder a la cámara.")
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Error: no se pudo capturar la imagen.")
            return

        # Convertir a RGB (OpenCV usa BGR por defecto)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        plt.figure("Paso 1 - Imagen original")
        plt.imshow(image_rgb)
        plt.title("Imagen original (RGB)")
        plt.axis('off')

        # Recorte (si es necesario)
        img_crop = image_rgb

        plt.figure("Paso 2 - Imagen recortada")
        plt.imshow(img_crop)
        plt.title("Imagen recortada")
        plt.axis('off')

        # Conversión a HSV
        img_crop_bgr = cv2.cvtColor(img_crop, cv2.COLOR_RGB2BGR)
        hsv_img = cv2.cvtColor(img_crop_bgr, cv2.COLOR_BGR2HSV)

        # Filtro HSV con tus valores iniciales (puedes ajustar aquí si quieres)
        lower_bound = np.array([0, 35, 119])
        upper_bound = np.array([180, 195, 255])
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)

        plt.figure("Paso 3 - Máscara HSV")
        plt.imshow(mask, cmap='gray')
        plt.title("Máscara tras umbral HSV")
        plt.axis('off')

        # Erosión y dilatación
        kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12))

        im_erode = cv2.erode(mask, kernel_erode, iterations=1)
        plt.figure("Paso 4 - Erosión")
        plt.imshow(im_erode, cmap='gray')
        plt.title("Erosión")
        plt.axis('off')

        im_fill = cv2.dilate(im_erode, kernel_dilate, iterations=1)
        plt.figure("Paso 5 - Dilatación")
        plt.imshow(im_fill, cmap='gray')
        plt.title("Dilatación")
        plt.axis('off')

        # Binarización
        im_bin = im_fill > 127
        plt.figure("Paso 6 - Imagen binarizada")
        plt.imshow(im_bin, cmap='gray')
        plt.title("Imagen binarizada")
        plt.axis('off')

        # Etiquetado y propiedades
        labels = label(im_bin)
        props = sorted(regionprops(labels), key=lambda x: -x.area)  # Ordenar por área descendente

        centroides = []

        fig, ax = plt.subplots()
        ax.imshow(img_crop)
        ax.set_title("Paso 7 - Centroides detectados")
        ax.axis('off')

        for prop in props:
            if prop.area < 1500:
                continue

            cy, cx = prop.centroid
            cx, cy = int(cx), int(cy)

            # Verificar que esté suficientemente alejado de los ya seleccionados
            cercano = False
            for (px, py) in centroides:
                if abs(cx - px) < 70 and abs(cy - py) < 70:
                    cercano = True
                    break

            if not cercano:
                centroides.append((cx, cy))
                ax.plot(cx, cy, 'r*', markersize=10)
                ax.text(cx + 5, cy, f"({cx}, {cy})", color='red', fontsize=10)

            if len(centroides) == 9:
                break  # Alcanzado el máximo

        # Guardar los datos
        shared_data.vision_output_pixel_coords = centroides
        shared_data.vision_output_piece_number = pieza_num
        shared_data.vision_output_rotation = rotacion

        print(f"Centroides detectados: {centroides}")

        plt.show()
