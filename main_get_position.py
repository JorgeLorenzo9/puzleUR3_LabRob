""" Acceder a la posición actual del robot"""
from ur3_module import UR3Module
import time
import shared_data

def main():
    ur3 = UR3Module()
    print(ur3.get_actual_pose())

if __name__ == "__main__":
    main()