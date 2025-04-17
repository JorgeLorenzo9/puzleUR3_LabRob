# vision_module.py
import shared_data

class VisionModule:
    def __init__(self):
        pass

    def detectar_pieza(self, pieza_num, pixel_x, pixel_y, rotacion):
        # Asignamos valores a las salidas como si fuera una detección real
        shared_data.vision_output_pixel_coords = (pixel_x, pixel_y)
        shared_data.vision_output_piece_number = pieza_num
        shared_data.vision_output_rotation = rotacion
