import time
import numpy as np
import shared_data
from ur3_module import UR3Module
from vision_module import VisionModule

class LogicModule:
    def __init__(self):
        self.estado = 1
        self.ur3 = UR3Module()
        self.vision = VisionModule()
        self.pose_tolerance = 0.005

        self.state_methods = {
            1: self.estado_1,
            2: self.estado_2,
            3: self.estado_3,
            4: self.estado_4,
            5: self.estado_5,
            6: self.estado_6,
            7: self.estado_7
        }

    def run_state_machine(self):
        try:
            print(f"[DEBUG] Ejecutando estado: {self.estado}")
            if self.estado in self.state_methods:
                self.state_methods[self.estado]()
            elif self.estado == -1:
                print("[LOGIC] Máquina de estados finalizada.")
            else:
                print(f"[LOGIC] Estado desconocido: {self.estado}")
        except Exception as e:
            print(f"[ERROR] Ocurrió una excepción: {e}")

    def estado_1(self):
        print("[LOGIC] Estado 1: Volver a HOME")
        self.ur3.move_to(shared_data.HOME)
        actual_pose = np.array(self.ur3.get_actual_pose())
        distance = np.linalg.norm(actual_pose[:3] - np.array(shared_data.HOME)[:3])
        if distance <= self.pose_tolerance:
            print("[LOGIC] Robot ha llegado a HOME. Avanzando al estado 2.")
            self.estado = 2
        else:
            print(f"[LOGIC] Esperando llegada a HOME... (Distancia: {distance:.4f} m)")

    def estado_2(self):
        print("[LOGIC] Estado 2: Detectando piezas")
        detect = self.vision.detectar_pieza()
        print(f"[LOGIC] Se han detectado: {detect}")
        if detect:
            self.estado = 3
            print("Conversión completada. Avanzando al estado 3.")
        else:
            print("No se han detectado 9 centroides. Reintentando...")

    def estado_3(self):
        print("[LOGIC] Estado 3: Movimiento a posición de la pieza")
        pieza_id = shared_data.num_piezas_colocadas + 1

        x, y = shared_data.centroides_robot[pieza_id][0:2]
        pose_rot = [-1.2254897161735516, -1.1406743714057417, 1.2107779703462462]

        self.ur3.move_to(shared_data.HOME_abajo)
        self.ur3.move_to([x, y, 0.1605, *pose_rot])
        self.ur3.move_to([x, y, 0.1585, *pose_rot])
        self.ur3.set_gripper(True)
        self.ur3.move_to([x, y, 0.1605, *pose_rot])
        self.ur3.move_to(shared_data.HOME)

        actual_pose = np.array(self.ur3.get_actual_pose())
        distance = np.linalg.norm(actual_pose[:3] - np.array(shared_data.HOME)[:3])
        if distance <= self.pose_tolerance:
            print("[LOGIC] Robot ha llegado a HOME. Avanzando al estado 4.")
            self.estado = 4
        else:
            print(f"[LOGIC] Esperando llegada a HOME... (Distancia: {distance:.4f} m)")

    def estado_4(self):
        print("[LOGIC] Estado 4: Llevando a zona de rotación")
        self.ur3.leave_puzzle()
        print("[LOGIC] Pieza dejada. Avanzando al estado 5.")
        self.estado = 5

    def estado_5(self):
        print("[LOGIC] Estado 5: Verificando orientación")
        shared_data.numero_pieza_actual = self.vision.comparar_con_puzzle_completo()
        if shared_data.numero_pieza_actual != 0:
            print(f"[LOGIC] Cara correcta. Se corresponde con {shared_data.numero_pieza_actual}.")
            self.ur3.catch_puzzle()
            self.estado = 6
        else:
            print("[LOGIC] Cara incorrecta. Girando la pieza...")
            self.ur3.catch_puzzle()
            self.ur3.rotate()
            self.estado = 5

    def estado_6(self):
        print("[LOGIC] Estado 6: Llevando pieza a su posición final")
        numero_pieza = shared_data.numero_pieza_actual
        if 1 <= numero_pieza <= 9:
            try:
                path_forward = getattr(shared_data, f'path_{numero_pieza}')
                path_return = getattr(shared_data, f'path_{numero_pieza}_return')
                self.ur3.move_to_final_position(path_forward, path_return)
                shared_data.num_piezas_colocadas += 1
                print(f"[LOGIC] Pieza colocada. Total colocadas: {shared_data.num_piezas_colocadas}")
                self.estado = 7
            except AttributeError as e:
                print(f"[ERROR] No se encontró la ruta para la pieza {numero_pieza}: {e}")
        else:
            print("[ERROR] Número de pieza inválido. Abortando ciclo.")
            self.estado = -1

    def estado_7(self):
        print("[LOGIC] Estado 7: Comprobando si quedan piezas")
        if shared_data.num_piezas_colocadas < 9:
            print("[LOGIC] Quedan piezas. Volviendo a HOME.")
            self.ur3.move_to(shared_data.HOME)
            self.estado = 3
        else:
            print("[LOGIC] Puzzle completado. Finalizando máquina de estados.")
            self.estado = -1
