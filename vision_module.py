import shared_data
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops

class VisionModule:
    def __init__(self):

        # Cargar imagen del puzle completo una sola vez
        #self.imagen_puzzle_completo = cv2.imread("PuzleAzulCOMPLETO.jpg", cv2.IMREAD_COLOR_RGB)
        self.imagen_puzzle_completo = cv2.imread("PuzleAzulCOMPLETO_recortado.jpg")
        #plt.imshow(self.imagen_puzzle_completo)
        #plt.show()
        if self.imagen_puzzle_completo is None:
            print("Error: no se pudo cargar la imagen del puzle completo.")
        else:
            print("[VISION] Imagen del puzle completo cargada correctamente.")

        # Puedes cambiar a cv2.SIFT_create() si tienes OpenCV contrib y lo prefieres
        self.detector = cv2.ORB_create(
            nfeatures=8000,
            scaleFactor=1.05,         # Escala entre niveles en la pirámide
            nlevels=16,               # Número de niveles en la pirámide
            edgeThreshold=31,        # Distancia al borde para evitar bordes de imagen
            patchSize=31,            # Tamaño del parche para descriptores
            fastThreshold=5         # Umbral del detector FAST
        )
        self.matcher = cv2.BFMatcher()

        self.casillas_visitadas = set()

    def detectar_pieza(self)->bool:
        # Captura desde la cámara
        cap = cv2.VideoCapture(2)
        print("[VISION] Imagen capturada para analisis")
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

        # plt.figure("Paso 1 - Imagen original")
        # plt.imshow(image_rgb)
        # plt.title("Imagen original (RGB)")
        # plt.axis('off')

        # Recorte (si es necesario)
        img_crop = image_rgb

        # plt.figure("Paso 2 - Imagen recortada")
        # plt.imshow(img_crop)
        # plt.title("Imagen recortada")
        # plt.axis('off')

        # Conversión a HSV
        img_crop_bgr = cv2.cvtColor(img_crop, cv2.COLOR_RGB2BGR)
        hsv_img = cv2.cvtColor(img_crop_bgr, cv2.COLOR_BGR2HSV)

        # Filtro HSV con tus valores iniciales (puedes ajustar aquí si quieres)
        lower_bound = np.array([0, 35, 119])
        upper_bound = np.array([180, 195, 255])
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)

        # plt.figure("Paso 3 - Máscara HSV")
        # plt.imshow(mask, cmap='gray')
        # plt.title("Máscara tras umbral HSV")
        # plt.axis('off')

        # Erosión y dilatación
        kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12))

        im_erode = cv2.erode(mask, kernel_erode, iterations=1)
        # plt.figure("Paso 4 - Erosión")
        # plt.imshow(im_erode, cmap='gray')
        # plt.title("Erosión")
        # plt.axis('off')

        im_fill = cv2.dilate(im_erode, kernel_dilate, iterations=1)
        # plt.figure("Paso 5 - Dilatación")
        # plt.imshow(im_fill, cmap='gray')
        # plt.title("Dilatación")
        # plt.axis('off')

        # Binarización
        im_bin = im_fill > 127
        #plt.figure("Paso 6 - Imagen binarizada")
        #plt.imshow(im_bin, cmap='gray')
        #plt.title("Imagen binarizada")
        #plt.axis('off')

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
                
                ax.plot(cx, cy, 'r*', markersize=10)
                ax.text(cx + 5, cy, f"({cx}, {cy})", color='red', fontsize=10)

                modelo = {
                    "coef_x": [
                        0.0301261460888152,
                        -0.5024140146130534
                    ],
                    "intercept_x": 189.61912556597025,
                    "coef_y": [
                        -0.505946641559293,
                        0.0289523269904209
                    ],
                    "intercept_y": 508.06783211157216,
                    "z_fija": -0.19
                }

                # Extraer coeficientes
                a1, a2 = modelo["coef_x"]
                b1, b2 = modelo["coef_y"]
                intercept_x = modelo["intercept_x"]
                intercept_y = modelo["intercept_y"]

                # Coordenadas en píxeles
                # u, v = 142, 191

                # Calcular posición en el espacio
                x = (a1 * cx + a2 * cy + intercept_x ) /1000
                y = (b1 * cx + b2 * cy + intercept_y)/1000

                centroides.append((x, y))
                centroides_shared = centroides
            
            if len(centroides) == 9:
                print("[VISION] Los 9 centroides has sido detectados correctamente")
                plt.show()
                shared_data.centroides_robot = centroides_shared
                return True  # Alcanzado el máximo
            
    
    def comparar_con_puzzle_completo(self)-> float:
        print("[VISION]  HEMOS ENTRADO EN COMPARAR PUZLE !! ")
        cap = cv2.VideoCapture(2)
        
        if not cap.isOpened():
            print("Error: no se pudo acceder a la cámara.")
            return 0

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Error: no se pudo capturar la imagen.")
            return 0

        x,y,w,h = 90, 90, 360, 360
        frame = frame[y:y+h, x:x+w]
    
        # Convertir a escala de grises
        imagen_pieza = frame
        #imagen_pieza = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        print("Imagen de la pieza a comparar")
        plt.imshow(imagen_pieza)
        plt.show()

        # Detectar y describir características
        kp1, des1 = self.detector.detectAndCompute(imagen_pieza, None)
        kp2, des2 = self.detector.detectAndCompute(self.imagen_puzzle_completo, None)

        if des1 is None or des2 is None:
            print("[VISION] No se encontraron descriptores suficientes.")
            return 0

        # Matching usando KNN y ratio test de Lowe
        matches = self.matcher.knnMatch(des1, des2, k=2)
        good_matches = [m for m, n in matches if m.distance < 0.8 * n.distance]

        print(f"[VISION] Número de coincidencias válidas: {len(good_matches)}")

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

                print(f"[VISION] Posición aproximada de la pieza en el puzle completo: ({int(x_aprox)}, {int(y_aprox)})")

                h_total, w_total = self.imagen_puzzle_completo.shape[:2]
                col = int(x_aprox // (w_total / 3))
                row = int(y_aprox // (h_total / 3))

                # Evitar salirse de rango
                col = min(col, 2)
                row = min(row, 2)

                # Cálculo de casilla (1 a 9)
                casilla = row * 3 + col + 1

                print(f"[VISION] La pieza corresponde aproximadamente a la casilla: {casilla} (fila {row + 1}, columna {col + 1})")

                if row+1 == 1:
                    if col + 1 == 1:
                        pieza_num = 1
                    elif col + 1 == 2:
                        pieza_num = 2
                    elif col + 1 == 3:
                        pieza_num = 3
                if row+1 == 2:
                    if col + 1 == 1:
                        pieza_num = 4
                    elif col + 1 == 2:
                        pieza_num = 5
                    elif col + 1 == 3:
                        pieza_num = 6
                if row+1 == 3:
                    if col + 1 == 1:
                        pieza_num = 7
                    elif col + 1 == 2:
                        pieza_num = 8
                    elif col + 1 == 3:
                        pieza_num = 9

                print("[VISION] Numero pieza asignado")
                if pieza_num in self.casillas_visitadas:
                    print("YA VISITADA, REINTENTAR")
                    return self.comparar_con_puzzle_completo()
                
                self.casillas_visitadas.add(pieza_num)
                shared_data.numero_pieza_actual= pieza_num
                print("[VISION] Numero pieza asignado en share_data")
                # Mostrar coincidencias
                img_matches = cv2.drawMatches(imagen_pieza, kp1, self.imagen_puzzle_completo, kp2, good_matches, None, flags=2)
                plt.imshow(img_matches)
                plt.show()
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

                print(f"[VISON] num pieza: {pieza_num}")
                return pieza_num
            else:
                print("[VISION] No se pudo calcular la homografía.")
                return 0
                
        else:
            print("[VISION] No hay suficientes coincidencias válidas.")
            img_matches = cv2.drawMatches(imagen_pieza, kp1, self.imagen_puzzle_completo, kp2, good_matches, None, flags=2)
            cv2.imshow("Coincidencias entre pieza y puzle completo", img_matches)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


            return 0
