# main.py
from vision_module import VisionModule
from logic_module import LogicModule
from ur3_module import UR3Module
import time
import shared_data

import time

if __name__ == "__main__":
    vision = VisionModule()
    logic = LogicModule()
    ur3 = UR3Module()
    # Simulamos una detección manual
    #vision.detectar_pieza(pieza_num=3, pixel_x=640, pixel_y=360, rotacion=45)

    pos= logic.pixel_to_mm (553,95)
    
    ur3.move_to(pos)

    # Ejecutamos la máquina de estados
    for _ in range(20):
        logic.run_state_machine()
        time.sleep(1)  # Pausa entre estados
