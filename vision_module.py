# vision_module.py
import shared_data
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import disk, erosion, dilation
from skimage.color import rgb2hsv
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

        # Mostrar imagen original
        plt.figure("Paso 1 - Imagen original")
        plt.imshow(image_rgb)
        plt.title("Imagen original (RGB)")
        plt.axis('off')

        # Recorte
        rect = (350, 32, 1114, 769)
        x, y, w, h = rect
        #img_crop = image_rgb[y:y+h, x:x+w]
        img_crop = image_rgb

        plt.figure("Paso 2 - Imagen recortada")
        plt.imshow(img_crop)
        plt.title("Imagen recortada")
        plt.axis('off')

        # Conversión a HSV y selección del canal H
        hsv = rgb2hsv(img_crop)
        canal_h = hsv[:, :, 0]

        plt.figure("Paso 3 - Canal H (HSV)")
        plt.imshow(canal_h, cmap='gray')
        plt.title("Canal H - Espacio HSV")
        plt.axis('off')

        # Erosión
        se = disk(6)
        im_erode = erosion(canal_h, se)

        plt.figure("Paso 4 - Erosión")
        plt.imshow(im_erode, cmap='gray')
        plt.title("Erosión del canal H")
        plt.axis('off')

        # Dilatación
        se2 = disk(5)
        im_fill = dilation(im_erode, se2)

        plt.figure("Paso 5 - Dilatación")
        plt.imshow(im_fill, cmap='gray')
        plt.title("Dilatación después de erosión")
        plt.axis('off')

        # Binarización
        im_bin = im_fill > 0.5

        plt.figure("Paso 6 - Imagen binarizada")
        plt.imshow(im_bin, cmap='gray')
        plt.title("Imagen binarizada")
        plt.axis('off')

        # Etiquetado de regiones
        labels = label(im_bin)
        props = regionprops(labels)

        centroides = []

        # Mostrar imagen con centroides
        fig, ax = plt.subplots()
        ax.imshow(img_crop)
        ax.set_title("Paso 7 - Centroides detectados")
        ax.axis('off')

        for prop in props:
            if prop.area >= 1500:
                cy, cx = prop.centroid
                centroides.append((int(cx), int(cy)))
                ax.plot(cx, cy, 'r*', markersize=10)
                ax.text(cx + 5, cy, f"({int(cx)}, {int(cy)})", color='red', fontsize=10)

        # Guardar resultados en shared_data
        shared_data.vision_output_pixel_coords = centroides
        shared_data.vision_output_piece_number = pieza_num
        shared_data.vision_output_rotation = rotacion

        print(f"Centroides detectados: {centroides}")

        # Mostrar todas las ventanas
        plt.show()
