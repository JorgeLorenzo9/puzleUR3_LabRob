# ur3_module.py
import shared_data
import rtde_control
import rtde_receive
import rtde_io
import time

class UR3Module:
    def __init__(self):

        self.rtde_c = rtde_control.RTDEControlInterface("169.254.12.28")
        self.rtde_r = rtde_receive.RTDEReceiveInterface("169.254.12.28")
        self.rtde_io = rtde_io.RTDEIOInterface("169.254.12.28")
        self.current_pose = shared_data.ur3_current_cartesian
        self.target_pose = shared_data.ur3_target_cartesian
        self.gripper_status = shared_data.ur3_gripper_status
        # Parameters
        self.speed = 0.9        # Speed in rad/s
        self.acceleration = 0.9 # Acceleration in rad/s^2

    def move_to(self, target_pose):
        self.target_pose = target_pose
        self.current_pose = self.rtde_r.getActualTCPPose()
        joint_positions = self.rtde_c.getInverseKinematics(target_pose)
        if joint_positions:
            self.rtde_c.moveJ(joint_positions, self.speed, self.acceleration)
            self.current_pose = self.rtde_r.getActualTCPPose() # pose in cartesian coordinates [x, y, z, rx, ry, rz]

        else:
            print("[UR3] No se pudo calcular la cinemática inversa para el target pose.")

    def set_gripper(self, status):
        self.gripper_status = status
        if status:
            self.rtde_io.setStandardDigitalOut(4, True) 
        else:
            self.rtde_io.setStandardDigitalOut(4, False)

    def rotate(self):
        self.set_gripper(True)
        self.move_to(shared_data.mirrar_arriba)
        self.move_to(shared_data.coger_en_caja)
        self.set_gripper(False)
        self.move_to(shared_data.mirrar_arriba)
        self.move_to(shared_data.no_chocar)
        self.move_to(shared_data.rot_medio)
        self.move_to(shared_data.rot_coger)
        
        self.set_gripper(True)
        self.move_to(shared_data.no_chocar_2)
        self.move_to(shared_data.echarse_atras)
        self.move_to(shared_data.no_chocar)
        self.move_to(shared_data.mirrar_arriba)
        self.move_to(shared_data.coger_en_caja)
        self.set_gripper(False)
        self.move_to(shared_data.mirrar_arriba)
    
    def catch_puzzle(self):
        self.move_to(shared_data.mirraz_puzzle_arriba)
        self.move_to(shared_data.mirrar_arriba)
        self.move_to(shared_data.coger_en_caja)
        self.set_gripper(True)
        self.move_to(shared_data.mirrar_arriba)
    def leave_puzzle(self):
        self.move_to(shared_data.mirrar_arriba)
        self.move_to(shared_data.coger_en_caja)
        self.set_gripper(False)
        self.move_to(shared_data.mirrar_arriba)
        self.move_to(shared_data.mirraz_puzzle_arriba)
        self.move_to(shared_data.mirraz_puzzle)

    def move_to_final_position(self,path, return_path):
        for wp in path:
            self.move_to(wp)
    
        self.set_gripper(False)
        for wp in return_path:
            self.move_to(wp)
     
    def get_actual_pose(self):
        self.current_pose = self.rtde_r.getActualTCPPose()
        return self.current_pose
