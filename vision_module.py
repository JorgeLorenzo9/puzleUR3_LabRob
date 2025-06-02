# vision_module.py
import shared_data

class VisionModule:
    def __init__(self):
        pass

    def detectar_piezas(self):
        """
        Simula la detección de 9 piezas en el área de trabajo.

        Returns:
            list: Lista de 9 tuplas con coordenadas (x, y) en píxeles.
        """

        # Simulación simple (puedes sustituir esta lógica por tu función real)
        centroides_pixeles = [
            (200, 100), (400, 100), (600, 100),
            (200, 300), (400, 300), (600, 300),
            (200, 500), (400, 500), (600, 500),
        ]
        return centroides_pixeles

    def convertir_centroides_a_robot(self, centroides_pixeles):
        """
        Convierte los centroides de píxeles a coordenadas físicas del robot tipo HOME
        y guarda los resultados en shared_data.centroides_robot.

        Args:
            centroides_pixeles (list): Lista de 9 tuplas (x, y) en píxeles.
        """

        for i, (px, py) in enumerate(centroides_pixeles, start=1):
            # Conversión a milímetros físicos relativos al origen del área de trabajo
            x_mm = self.origen_mm[0] + px * self.mm_por_pixel_x
            y_mm = self.origen_mm[1] + py * self.mm_por_pixel_y

            # Si el robot trabaja en metros, convertir a metros
            x = x_mm / 1000
            y = y_mm / 1000
            z = 0.15  # z constante
            rx = ry = rz = 0  # sin rotación

            # Guardamos en shared_data una lista tipo HOME
            shared_data.centroides_robot[i] = [x, y, z, rx, ry, rz]

    def es_cara_correcta(self):
        """
        Determina si la cara de la pieza detectada es la correcta.

        Returns:
            bool: True si la cara es la correcta, False si no lo es.
        """
        if shared_data.vision_output_face_correcta:
            shared_data.numero_pieza_actual = 1
            print(f"Cara correcta detectada para la pieza número.")
            return shared_data.vision_output_face_correcta

