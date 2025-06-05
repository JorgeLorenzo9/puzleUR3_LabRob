# logic_module.py
import shared_data



import numpy as np 

class LogicModule:
    def __init__(self):
        self.estado = 1
      


    def run_state_machine(self):
        if self.estado == 1:
            print("[LOGIC] Estado 1: Volver a HOME")
            #self.ur3.move_to(shared_data.HOME)
            print("[LOGIC] Robot ha llegado a HOME. Avanzando al estado 2.")
            self.estado = 2


        elif self.estado == 2:
            print("Detectando piezas ")
            print("conviertiendo pixeles a m ")
            self.estado = 3



        elif self.estado == 3:
            print("[LOGIC] Estado 3: Movimiento a posición pieza")
            print("[LOGIC] Robot ha llegado a HOME. Avanzando al estado 4.")
            self.estado = 4
            print(f"[LOGIC] Esperando a que el robot llegue a HOME... (Distancia actual:)")

    
        elif self.estado == 4:
            print("Llevando a la zona de rotación")
            self.estado = 5
    

        elif self.estado == 5:
            print("Comprobando si la cara es la correcta")
            print("La cara de la pieza es la correcta. Avanzando al estado 7.")
            self.estado = 6
            

        elif self.estado == 6:
            print("[Llevando la pieza a su sitio")
            numero_pieza = shared_data.numero_pieza_actual
            print(numero_pieza)


        elif self.estado == 7:
         
            print("Volviendo a HOME. Preparando para siguiente detección.")
            self.estado = 2
            


    
