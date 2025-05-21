# main.py
import threading
import time
import tkinter as tk

from interfaz_puzzle import PuzzleUR3App
from vision_module import VisionModule
from logic_module import LogicModule
import shared_data


def run_logic(logic):
    """
    Ejecuta la lógica en segundo plano (máquina de estados).
    """
    while True:
        logic.run_state_machine()
        time.sleep(1)


if __name__ == "__main__":
    # Crear módulo de lógica y visión
    logic = LogicModule()
    vision = VisionModule()

    # Simulación de una pieza detectada
    vision.detectar_pieza(pieza_num=3, pixel_x=640, pixel_y=360, rotacion=45)

    # Crear GUI en el hilo principal
    root = tk.Tk()
    app = PuzzleUR3App(root)

    # Iniciar hilo de lógica
    logic_thread = threading.Thread(target=run_logic, args=(logic,), daemon=True)
    logic_thread.start()

    # Ejecutar GUI
    root.mainloop()
