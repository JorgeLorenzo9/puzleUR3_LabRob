# ur3_module.py
import shared_data

class UR3Module:
    def __init__(self):
        self.current_pose = shared_data.ur3_current_cartesian

    def move_to(self, target_pose):
        shared_data.ur3_current_cartesian = target_pose
        print(f"[UR3] Moviendo a coordenadas: {target_pose}")

    def set_gripper(self, status):
        shared_data.ur3_gripper_status = status
        print(f"[UR3] Ventosa {'ACTIVADA' if status else 'DESACTIVADA'}")
