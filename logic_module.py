# logic_module.py
import shared_data
from ur3_module import UR3Module
from vision_module import VisionModule

class LogicModule:
    def __init__(self):
        self.estado = 0  # Cambiamos el estado inicial
        self.ur3 = UR3Module()
        self.vision = VisionModule()
        self.tipo_puzzle = None  # Se definirá desde la interfaz

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
            (120, 340),   # esquina superior izquierda
            (980, 320),   # esquina superior derecha
            (1000, 720),  # esquina inferior derecha
            (100, 740)    # esquina inferior izquierda
        ]

        # Coordenadas físicas reales correspondientes (en milímetros)
        real_points = [
            (0.0, 0.0),       # esquina superior izquierda
            (300.0, 0.0),     # esquina superior derecha
            (300.0, 200.0),   # esquina inferior derecha
            (0.0, 200.0)      # esquina inferior izquierda
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
        x_mm, y_mm = transformed_point[0][0]
        return (x_mm, y_mm)


    def run_state_machine(self):
        def run_state_machine(self):
            if shared_data.selected_puzzle is None:
                return  # Esperar a que el usuario seleccione un puzzle desde la interfaz

        if self.estado == 1:
            print("[LOGIC] Estado 1: Volver a HOME")
            self.ur3.move_to(shared_data.HOME)
            self.vision.detectar_pieza()
            self.estado = 2


        elif self.estado == 2:
            if shared_data.vision_output_pixel_coords is not None:
                print("[LOGIC] Estado 2: Conversión píxeles a mm")
                x_mm, y_mm = self.pixel_to_mm(shared_data.vision_output_pixel_coords)
                self.target_coords = (x_mm, y_mm, shared_data.altura_home, 0, 0, 0)
                self.estado = 3

        elif self.estado == 3:
            print("[LOGIC] Estado 3: Movimiento a posición pieza")
            self.ur3.move_to(self.target_coords)
            self.estado = 4

        elif self.estado == 4:
            print("[LOGIC] Estado 4: Recibiendo número y rotación")
            # Aqui se le llamaria a la segunda función de visión donde nos devuelve el numero de pieza final que es y la rotación para pillarla bien
            self.pieza_num = shared_data.vision_output_piece_number
            self.rotacion = shared_data.vision_output_rotation
            self.estado = 5

        elif self.estado == 5:
            print("[LOGIC] Estado 5: Rotación de muñeca")
            if self.rotacion != 0:
                print(f"[LOGIC] Rotando muñeca a {self.rotacion}° (simulado)")
                # añadir moviemiento de rotar 
                # habria uqe llamar a la funcion de vision para saber si es correcto la cara o no sino es corecto vuelve a rotar 
            self.estado = 6

        elif self.estado == 6:
            print("[LOGIC] Estado 6: Bajando a coger pieza")
            x, y, _, yaw, pitch, roll = self.target_coords
            z_coger = shared_data.z_catch
            self.ur3.move_to((x, y, z_coger, yaw, pitch, roll))
            self.ur3.set_gripper(True)
            self.estado = 7

        elif self.estado == 7:
            print("[LOGIC] Estado 7: Posicionar en área solución")
            dx, dy = shared_data.area_solucion["positions"][self.pieza_num]
            origin_x, origin_y = shared_data.area_solucion["corner_origin_mm"]
            destino = (origin_x + dx, origin_y + dy, shared_data.altura_home, 0, 0, 0)
            self.ur3.move_to(destino)
            self.estado = 8

        elif self.estado == 8:
            print("[LOGIC] Estado 8: Soltando pieza")
            z_bajar = shared_data.altura_home - shared_data.altura_coger_pieza
            self.ur3.move_to((destino[0], destino[1], z_bajar, 0, 0, 0))
            self.ur3.set_gripper(False)
            self.estado = 9

        elif self.estado == 9:
            print("[LOGIC] Estado 9: Volver a HOME")
            self.ur3.move_to((0, 0, shared_data.altura_home, 0, 0, 0))
            print("[LOGIC] Reiniciando ciclo")
            self.estado = 1
