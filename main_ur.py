""" Módulo para realizar Pruebas Unitarias con el robot """
from ur3_module import UR3Module
import shared_data
import shared_data
import cv2
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
def main():
    ur3 = UR3Module()
    mirraz_puzzle = [-0.13673873456936142, 0.27734496123085284, 0.2751934240055127, -1.214052291499628, -1.1079593817250402, 1.2113744366474313]
    ur3.move_to(shared_data.HOME)
    # ur3.set_gripper(False)
    # ur3.move_to([0.08466545884173958, 0.2863416203890516, 0.158529264767416 , -1.2254897161735516, -1.1406743714057417, 1.2107779703462462])
    # ur3.set_gripper(True)
    # ur3.move_to(shared_data.HOME)
    # ur3.leave_puzzle()
    # ur3.catch_puzzle()
    # ur3.rotate()
    # ur3.catch_puzzle()
    # #aqui tengo que decirle si se va a l aposición del puzzle o no 
    # ur3.move_to_final_position(shared_data.path_1, shared_data.path_1_return)
    # ur3.move_to(shared_data.HOME)

    cap = cv2.VideoCapture(2)
    ret, frame = cap.read()
    cap.release()

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    plt.imshow(image_rgb)
    plt.show()

    
    # ur3.rotate()

if __name__ == "__main__":
    main()
