# main.py
from ur3_module import UR3Module
import time
import shared_data

def main():
    ur3 = UR3Module()
    target_pose =  shared_data.HOME
    ur3.move_to(target_pose)
    time.sleep(2)  
    ur3.move_to([0.08466545884173958, 0.2863416203890516, 0.158529264767416, -1.2254897161735516, -1.1406743714057417, 1.2107779703462462])
    time.sleep(2)  
    ur3.set_gripper(True)  
    time.sleep(2)  
    ur3.move_to(target_pose)
    # ur3.set_gripper(False)  
if __name__ == "__main__":
    main()
