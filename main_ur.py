# main.py
from ur3_module import UR3Module
import time

def main():
    # Create an instance of the UR3Module
    ur3 = UR3Module()

    # Define a target pose [x, y, z, rx, ry, rz]
    target_pose = [0.3, 0.2, 0.4, 0, 3.14, 0]  # Example pose

    # Move the robot to the target pose
    ur3.move_to(target_pose, speed=0.5, acceleration=0.3)

    # Wait for a moment to ensure the movement is complete
    time.sleep(2)

    # Activate the gripper (vacuum ON)
    ur3.set_gripper(True)

    # Wait a bit
    time.sleep(1)

    # Move to another position
    second_pose = [0.2, 0.1, 0.3, 0, 3.14, 0]
    ur3.move_to(second_pose, speed=0.5, acceleration=0.3)

    # Wait again
    time.sleep(2)

    # Deactivate the gripper (vacuum OFF)
    ur3.set_gripper(False)

if __name__ == "__main__":
    main()
