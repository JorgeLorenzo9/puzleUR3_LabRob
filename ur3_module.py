# ur3_module.py
import shared_data
import rtde_control
import rtde_receive
import time

class UR3Module:
    def __init__(self):

        self.rtde_c = rtde_control.RTDEControlInterface('192.168.56.20')
        self.rtde_r = rtde_receive.RTDEReceiveInterface('192.168.56.20')
        self.current_pose = shared_data.ur3_current_cartesian
        self.target_pose = shared_data.ur3_target_cartesian
        self.gripper_status = shared_data.ur3_gripper_status
        # Parameters
        self.speed = 0.5        # Speed in rad/s
        self.acceleration = 0.3 # Acceleration in rad/s^2

    def move_to(self, target_pose):
        # self.shared_data.ur3_current_cartesian = target_pose
        self.target_pose = target_pose  # REVISAR UNIDADES
        # current pose
        self.current_pose = self.rtde_r.getActualTCPPose()
        #  Compute joints positions
        joint_positions = self.rtde_c.getInverseKinematics(target_pose)
        # move to target pose
        if joint_positions:
            print(f"[UR3] Calculadas articulaciones: {joint_positions}")
            # send joint positions to robot
            self.rtde_c.moveJ(joint_positions, self.speed, self.acceleration)
            # get current pose
            self.current_pose = self.rtde_r.getActualTCPPose() # pose in cartesian coordinates [x, y, z, rx, ry, rz]

        else:
            print("[UR3] No se pudo calcular la cinemática inversa para el target pose.")

        print(f"[UR3] Moviendo a coordenadas: {target_pose}")

    def set_gripper(self, status):
        self.gripper_status = status
        print(f"[UR3] Ventosa {'ACTIVADA' if status else 'DESACTIVADA'}")
        #use DO0 to control vacuum, and DI0 to check vacuum sensor   REVISAR
        gripper_output_id = 0  # Change to your actual Digital Output ID
        vacuum_sensor_input_id = 0  # Change to your actual Digital Input ID

        if status:
            # Activate vacuum
            self.rtde_c.setStandardDigitalOut(gripper_output_id, True)
            print("[UR3] Vacuum ON - Trying to pick up part...")

            # Wait a short time for vacuum to engage
            time.sleep(0.5)  # Adjust if necessary

            # Check if part is picked
            part_grabbed = self.rtde_r.getDigitalInputState(vacuum_sensor_input_id)
            if part_grabbed:
                print("[UR3] Part successfully picked!")
            else:
                print("[UR3] Warning: No part detected!")
        else:
            # Deactivate vacuum
            self.rtde_c.setStandardDigitalOut(gripper_output_id, False)
            print("[UR3] Vacuum OFF - Releasing part.")        
