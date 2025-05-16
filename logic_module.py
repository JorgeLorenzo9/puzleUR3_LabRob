# logic_module.py
import shared_data
from ur3_module import UR3Module

class LogicModule:
    def __init__(self):
        self.estado = 1
        self.ur3 = UR3Module()

    def pixel_to_mm(self, pixel_coords):
        (px, py) = pixel_coords
        cam_w, cam_h = shared_data.camera_resolution
        area_w, area_h = shared_data.area_trabajo["dim_mm"]
        x_mm = shared_data.area_trabajo["corner_origin_mm"][0] + (px / cam_w) * area_w
        y_mm = shared_data.area_trabajo["corner_origin_mm"][1] + (py / cam_h) * area_h
        return (x_mm, y_mm)

    def run_state_machine(self):
        if self.estado == 1:
            print("[LOGIC] Estado 1: Volver a HOME")
            self.ur3.move_to(shared_data.HOME)
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
            self.pieza_num = shared_data.vision_output_piece_number
            self.rotacion = shared_data.vision_output_rotation
            self.estado = 5

        elif self.estado == 5:
            print("[LOGIC] Estado 5: Rotación de muñeca")
            if self.rotacion != 0:
                print(f"[LOGIC] Rotando muñeca a {self.rotacion}° (simulado)")
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
