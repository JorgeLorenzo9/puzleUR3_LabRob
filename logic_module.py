# logic_module.py
import shared_data
from ur3_module import UR3Module

import numpy as np 

class LogicModule:
    def __init__(self):
        self.estado = 1
        self.ur3 = UR3Module()
        self.pose_tolerance = 0.005


    def run_state_machine(self):
        if self.estado == 1:
            print("[LOGIC] Estado 1: Volver a HOME")
            self.ur3.move_to(shared_data.HOME)
            actual_pose = np.array(self.ur3.get_actual_pose())
            target_pose = np.array(shared_data.HOME)
            distance = np.linalg.norm(actual_pose[:3] - target_pose[:3])  # Compara solo x,y,z
            if distance <= self.pose_tolerance:
                print("[LOGIC] Robot ha llegado a HOME. Avanzando al estado 2.")
                self.estado = 2
            else:
                print(f"[LOGIC] Esperando a que el robot llegue a HOME... (Distancia actual: {distance:.4f} m)")


        elif self.estado == 2:
            if shared_data.vision_output_pixel_coords is not None:
                print("[LOGIC] Estado 2: Conversión píxeles a mm")


        elif self.estado == 3:
            print("[LOGIC] Estado 3: Movimiento a posición pieza")
            self.ur3.move_to([0.08466545884173958, 0.2863416203890516, 0.158529264767416 , -1.2254897161735516, -1.1406743714057417, 1.2107779703462462])
            self.ur3.set_gripper(True)
            self.ur3.move_to(shared_data.HOME)
            actual_pose = np.array(self.ur3.get_actual_pose())
            target_pose = np.array(shared_data.HOME)
            distance = np.linalg.norm(actual_pose[:3] - target_pose[:3])  # Compara solo x,y,z
            if distance <= self.pose_tolerance:
                print("[LOGIC] Robot ha llegado a HOME. Avanzando al estado 2.")
                self.estado = 4
            else:
                print(f"[LOGIC] Esperando a que el robot llegue a HOME... (Distancia actual: {distance:.4f} m)")

    

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
