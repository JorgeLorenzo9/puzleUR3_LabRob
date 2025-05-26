# logic_module.py
import shared_data
from vision_module import VisionModule

import numpy as np
import cv2 

class LogicModule:   
    def __init__(self):
        self.estado = 0
        self.vision = VisionModule()
        self.tipo_puzzle = None

    @staticmethod
    def pixel_to_mm(pixel_coords):
        """
        Transforma coordenadas de píxeles (pixel_coords) a coordenadas en milímetros
        utilizando una matriz de homografía basada en 4 puntos de referencia conocidos.

        Parámetros:
            pixel_coords: tupla (px, py) del centroide detectado en píxeles

        Retorna:
            (x_mm, y_mm): coordenadas físicas en milímetros
        """
        import numpy as np
        import cv2

        # Coordenadas de las 4 esquinas del área de trabajo en la imagen (en píxeles)
        pixel_points = [
            (597, 440),   # esquina superior izquierda
            (196, 445),   # esquina superior derecha
            (195, 45),  # esquina inferior derecha
            (600, 40)    # esquina inferior izquierda
        ]

        # Coordenadas físicas reales correspondientes (en milímetros)
        real_points = [
            (0.20199798160382304, 0.476085595716464),       # esquina superior izquierda
            (0.20199798160382304, 0.476085595716464),     # esquina superior derecha
            (-0.03233289065041634, 0.2984046079386768),   # esquina inferior derecha
            (-0.01500268344637711, 0.49672099354183596)      # esquina inferior izquierda
        ]

        # Conversión a arrays tipo float32
        pixel_points_np = np.array(pixel_points, dtype=np.float32)
        real_points_np = np.array(real_points, dtype=np.float32)

        # Calcular la matriz de homografía
        homography_matrix, _ = cv2.findHomography(pixel_points_np, real_points_np)

        # Transformar el punto del centroide
        px, py = pixel_coords
        point = np.array([[px, py]], dtype=np.float32).reshape(-1, 1, 2)
        transformed_point = cv2.perspectiveTransform(point, homography_matrix)

        # Extraer las coordenadas en mm
        x_m, y_m = transformed_point[0][0]
        pose = (x_m,y_m,0.1585, -1.2254897161735516, -1.1406743714057417, 1.2107779703462462)
      # Imprimir la pose calculada
        print(f"[INFO] Pose generada para píxel {pixel_coords}:")
        print(f"       x = {x_m:.6f} m")
        print(f"       y = {y_m:.6f} m")
        print(f"       z = 0.158500 m")
        print(f"       rx = -1.225490 rad")
        print(f"       ry = -1.140674 rad")
        print(f"       rz = 1.210778 rad\n")
        return pose 


   
