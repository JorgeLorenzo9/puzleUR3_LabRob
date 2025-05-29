import shared_data
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops

class VisionModule:
    
    def cargar_calibracion(self, path):
        with np.load(path) as data:
            self.mtx = data['mtx']
            self.dist = data['dist']
        print("Calibración cargada correctamente.")

    def __init__(self):

        # Cargar imagen del puzle completo una sola vez
        self.imagen_puzzle_completo = cv2.imread("PuzleAzulCOMPLETO.jpg", cv2.IMREAD_COLOR_RGB)
        if self.imagen_puzzle_completo is None:
            print("Error: no se pudo cargar la imagen del puzle completo.")
        else:
            print("Imagen del puzle completo cargada correctamente.")

        # Puedes cambiar a cv2.SIFT_create() si tienes OpenCV contrib y lo prefieres
        self.detector = cv2.ORB_create(
            nfeatures=3000,
            scaleFactor=1.1,         # Escala entre niveles en la pirámide
            nlevels=12,               # Número de niveles en la pirámide
            edgeThreshold=15,        # Distancia al borde para evitar bordes de imagen
            patchSize=15,            # Tamaño del parche para descriptores
            fastThreshold=10         # Umbral del detector FAST
        )
        self.matcher = cv2.BFMatcher()

        # Cargar parámetros de calibración
        self.cargar_calibracion("calibration_data.npz")

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

        if self.mtx is not None and self.dist is not None:
            Z = 0.362  # Distancia de la cámara al plano en metros
            fx = self.mtx[0, 0]
            fy = self.mtx[1, 1]
            cx = self.mtx[0, 2]
            cy = self.mtx[1, 2]

            centroides_mundo = []

            for cx_pix, cy_pix in centroides:
                pixel = np.array([[[cx_pix, cy_pix]]], dtype=np.float32)
                undistorted = cv2.undistortPoints(pixel, self.mtx, self.dist, P=self.mtx)
                x_norm, y_norm = undistorted[0][0]

                #X = x_norm * Z
                #Y = y_norm * Z

                X = (((cx_pix - cx) * Z / fx) + 0.075) * 1000 # Convertir a mm
                Y = ((cy_pix - cy) * Z / fy) * 1000 # Convertir a mm


                centroides_mundo.append((X, Y))

            shared_data.vision_output_real_coords = centroides_mundo
            print(f"Coordenadas reales en metros: {centroides_mundo}")
        else:
            shared_data.vision_output_real_coords = None



        plt.show()

    
    def comparar_con_puzzle_completo(self):
        cap = cv2.VideoCapture(1)

        if not cap.isOpened():
            print("Error: no se pudo acceder a la cámara.")
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Error: no se pudo capturar la imagen.")
            return

        # Convertir a escala de grises
        imagen_pieza = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #imagen_pieza = cv2.equalizeHist(imagen_pieza)

        # Detectar y describir características
        kp1, des1 = self.detector.detectAndCompute(imagen_pieza, None)
        kp2, des2 = self.detector.detectAndCompute(self.imagen_puzzle_completo, None)

        if des1 is None or des2 is None:
            print("No se encontraron descriptores suficientes.")
            return

        # Matching usando KNN y ratio test de Lowe
        matches = self.matcher.knnMatch(des1, des2, k=2)
        good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

        print(f"Número de coincidencias válidas: {len(good_matches)}")

        # Calcular posición si hay suficientes coincidencias
        if len(good_matches) > 10:
            # Extraer puntos emparejados
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Calcular homografía
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if M is not None:
                # Centro de la pieza capturada
                h_pieza, w_pieza = imagen_pieza.shape[:2]
                centro_pieza = np.array([[[w_pieza / 2, h_pieza / 2]]], dtype=np.float32)

                # Transformar al sistema de coordenadas del puzle completo
                centro_transformado = cv2.perspectiveTransform(centro_pieza, M)
                x_aprox, y_aprox = centro_transformado[0][0]

                print(f"Posición aproximada de la pieza en el puzle completo: ({int(x_aprox)}, {int(y_aprox)})")

                h_total, w_total = self.imagen_puzzle_completo.shape[:2]
                col = int(x_aprox // (w_total / 3))
                row = int(y_aprox // (h_total / 3))

                # Evitar salirse de rango
                col = min(col, 2)
                row = min(row, 2)

                # Cálculo de casilla (1 a 9)
                casilla = row * 3 + col + 1

                print(f"La pieza corresponde aproximadamente a la casilla: {casilla} (fila {row + 1}, columna {col + 1})")


                # Mostrar coincidencias
                img_matches = cv2.drawMatches(imagen_pieza, kp1, self.imagen_puzzle_completo, kp2, good_matches, None, flags=2)
                cv2.imshow("Coincidencias entre pieza y puzle completo", img_matches)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                return (int(x_aprox), int(y_aprox), casilla)
            else:
                print("No se pudo calcular la homografía.")
                return None
        else:
            print("No hay suficientes coincidencias válidas.")
            # Mostrar coincidencias
            img_matches = cv2.drawMatches(imagen_pieza, kp1, self.imagen_puzzle_completo, kp2, good_matches, None, flags=2)
            cv2.imshow("Coincidencias entre pieza y puzle completo", img_matches)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            return None
