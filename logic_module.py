# logic_module.py
import shared_data
from ur3_module import UR3Module
from vision_module import VisionModule

vision = VisionModule()


import numpy as np 

class LogicModule:
    def __init__(self):
        self.estado = 1
        self.ur3 = UR3Module()
        self.vision = VisionModule()
        self.pose_tolerance = 0.005

    def __del__(self):
        print('se ha destruido el objeto logica')
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
                self.estado=1

        elif self.estado == 2:
            print("Detectando piezas ")
            print("Conviertiendo pixeles a m ")
            
            # if self.vision.detectar_pieza():
            detect=self.vision.detectar_pieza()
            print (f"se han detectado {detect}")
            if detect:
            # if len(shared_data.centroides_robot) == 9:
                self.estado = 3
                print("Conversión completada correctamente. Estado actualizado a 3.")
            else:
                print("Error: no se han convertido los 9 centroides.")



        elif self.estado == 3:
            print("[LOGIC] Estado 3: Movimiento a posición pieza")
            
            # Selección del centroide correspondiente
            pieza_id = shared_data.num_piezas_colocadas + 1
            print(shared_data.centroides_robot[pieza_id][0],shared_data.centroides_robot[pieza_id][1])
            target_pose_up = [shared_data.centroides_robot[pieza_id][0],shared_data.centroides_robot[pieza_id][1], 0.168529264767416 ,-1.2254897161735516, -1.1406743714057417, 1.2107779703462462]
            target_pose_up_up = [shared_data.centroides_robot[pieza_id][0],shared_data.centroides_robot[pieza_id][1], 0.2500529264767416,-1.2254897161735516, -1.1406743714057417, 1.2107779703462462]
            target_pose_down = [shared_data.centroides_robot[pieza_id][0],shared_data.centroides_robot[pieza_id][1], 0.158529264767416 ,-1.2254897161735516, -1.1406743714057417, 1.2107779703462462]
            self.ur3.move_to(shared_data.HOME_abajo)
            print("Moviendo a HOME_abajo")
            self.ur3.move_to(target_pose_up)
            print("Moviendo a target_pose_up")
            self.ur3.move_to(target_pose_down)
            print("Moviendo a target_pose_down")
            self.ur3.set_gripper(True)
            self.ur3.move_to(target_pose_up)
            # self.ur3.move_to(target_pose_up_up)
            self.ur3.move_to(shared_data.HOME)
  
            actual_pose = np.array(self.ur3.get_actual_pose())
            distance = np.linalg.norm(actual_pose[:3] - shared_data.HOME[:3])  # Compara solo x,y,z
            if distance <= self.pose_tolerance:
                print("[LOGIC] Robot ha llegado a HOME. Avanzando al estado 4.")
                self.estado = 4
            else:
                print(f"[LOGIC] Esperando a que el robot llegue a HOME... (Distancia actual: {distance:.4f} m)")

    
        elif self.estado == 4:
            print("[LOGIC] Estado 4")
            print("[LOGIC] Llevando a la zona de rotación")
            self.ur3.leave_puzzle()
            print("[LOGIC] Dejado el puzle")
            self.estado = 5
            print(f"estado: {self.estado}")
            # # actual_pose = np.array(self.ur3.get_actual_pose())
            # target_pose = np.array(shared_data.mirraz_puzzle)
            # # distance = np.linalg.norm(actual_pose[:3] - target_pose[:3])  # Compara solo x,y,z
            # if distance <= self.pose_tolerance:
            #     print("[LOGIC] Robot ha llegado a HOME. Avanzando al estado 4.")
            #     self.estado = 5
            # else:
            #     print(f"[LOGIC] Esperando a que el robot llegue a zona de dejada... (Distancia actual: {distance:.4f} m)")
    

        elif self.estado == 5:
            print("[LOGIC] Estado 5")
            print("Comprobando si la cara es la correcta")
            #self.vision.comparar_con_puzzle_completo = shared_data.numero_pieza_actual
            shared_data.numero_pieza_actual= self.vision.comparar_con_puzzle_completo()
            if shared_data.numero_pieza_actual != 0:
                print(f"[LOGIC] La cara de la pieza es la correcta se corresponde con {shared_data.numero_pieza_actual}. Avanzando al estado 6.")
                self.ur3.catch_puzzle()
                print("Se ha checho catch puzzle")
                print(shared_data.num_piezas_colocadas)
                self.estado = 6
            else:
                print("[LOGIC] Cara incorrecta. Girando la pieza...")

                # Giro completo de la pieza
                self.ur3.catch_puzzle()
                self.ur3.rotate()

                print("[LOGIC] Pieza girada. Avanzando al estado 5.")
                self.estado = 5

        elif self.estado == 6:
            print("[LOGIC] Estado 6")
            print("[LOGIC] Llevando la pieza a su sitio")
            numero_pieza = shared_data.numero_pieza_actual
            print(f"numero_pieza es {numero_pieza}")

            if 1 <= numero_pieza <= 9:
                # Construimos dinámicamente el nombre del path correspondiente
                print("[LOGIC] el numero de la pieza está entre 1 y 9")
                path_forward = getattr(shared_data, f'path_{numero_pieza}')
                path_return = getattr(shared_data, f'path_{numero_pieza}_return')
                self.ur3.move_to_final_position(path_forward, path_return)
                shared_data.num_piezas_colocadas += 1
                print(f"El numero de piezas colocadas: {shared_data.num_piezas_colocadas}")
                self.estado = 7

        elif self.estado == 7:
            if shared_data.num_piezas_colocadas < 9:
                # Aún quedan piezas: ir a HOME y volver al estado 2
                self.ur3.move_to(shared_data.HOME)
                print("Volviendo a HOME. Preparando para siguiente detección.")
                print(f"{self.estado} antes de cambiar")
                self.estado = 3
                print(f"{self.estado} despues de cambiar")
            else:
                # Todas las piezas colocadas
                print("Puzzle completado correctamente. Todas las piezas han sido colocadas.")
                self.estado = -1  # o cualquier otro estado de parada definida


    
