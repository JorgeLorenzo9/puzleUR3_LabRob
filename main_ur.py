# main.py
from ur3_module import UR3Module
import time
import shared_data
import shared_data
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
def main():
    # ur3 = UR3Module()
    # ur3.move_to(shared_data.HOME)
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
    cap = cv2.VideoCapture(1)
    ret, frame = cap.read()
    cap.release()

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    plt.figure("Paso 1 - Imagen original")
    plt.imshow(image_rgb)
    plt.title("Imagen original (RGB)")
    plt.axis('off')


    
    # ur3.rotate()

if __name__ == "__main__":
    main()
