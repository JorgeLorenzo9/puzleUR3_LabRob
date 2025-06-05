# main.py
from logic_module import LogicModule
from interfaz import Interfaz
import tkinter as tk
import time
2
if __name__ == "__main__":
    logic = LogicModule()
    root = tk.Tk()
    app = Interfaz(root)
    root.mainloop()
    # Ejecutamos la máquina de estados
    # for _ in range(20):
    #     logic.run_state_machine()
    #     time.sleep(1)  # Pausa entre estados
