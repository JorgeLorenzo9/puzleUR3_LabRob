# main.py
from vision_module import VisionModule
from logic_module import LogicModule

import time

if __name__ == "__main__":
    logic = LogicModule()



    # Ejecutamos la máquina de estados
    for _ in range(20):
        logic.run_state_machine()
        time.sleep(1)  # Pausa entre estados
