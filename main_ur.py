# main.py
from ur3_module import UR3Module
import time
import shared_data

def main():
    ur3 = UR3Module()
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_1, shared_data.path_1_return)
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_2, shared_data.path_2_return)
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_3, shared_data.path_3_return)
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_4, shared_data.path_4_return)
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_5, shared_data.path_5_return)
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_6, shared_data.path_6_return)
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_7, shared_data.path_7_return)
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_8, shared_data.path_8_return)
    ur3.move_to(shared_data.HOME)
    ur3.set_gripper(True)
    ur3.move_to_final_position(shared_data.path_9, shared_data.path_9_return)
    ur3.move_to(shared_data.HOME)

    
    # ur3.rotate()

if __name__ == "__main__":
    main()
