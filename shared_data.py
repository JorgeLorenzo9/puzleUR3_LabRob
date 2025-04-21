# shared_data.py
# =================== PARÁMETROS DE INICIO ===================
HOME = [0.08466545884173958, 0.2863416203890516, 0.3500529264767416, -1.2254897161735516, -1.1406743714057417, 1.2107779703462462]
# =================== COORDENADAS ============================
z_catch = 0.158529264767416  # mm
# =================== ENTRADAS Y SALIDAS DE VISIÓN ===========
vision_output_pixel_coords = None     # (x, y) en píxeles
vision_output_piece_number = None     # número de pieza (1 a 9)
vision_output_rotation = None         # ángulo en grados (o radianes)

# =================== ENTRADAS DE UR3 ========================
ur3_current_cartesian = (0, 0, 0, 0, 0, 0)  # (x, y, z, yaw, pitch, roll)
ur3_gripper_status = False  # True: sujeta, False: suelta

# =================== SALIDAS A UR3 ==========================
ur3_target_cartesian = None   # (x, y, z, yaw, pitch, roll)
ur3_gripper_command = None    # True: cerrar, False: abrir

# =================== PARÁMETROS DEFINIDOS ===================
# Resolución cámara
camera_resolution = (1280, 720)

# Área de trabajo y área de solución
area_trabajo = {
    "dim_mm": (300, 300),     # ancho x alto
    "corner_origin_mm": (100, 100)
}
area_solucion = {
    "dim_mm": (300, 300),
    "corner_origin_mm": (500, 100),
    "positions": {            # asignación pieza->posición en el puzzle
        1: (0, 0),
        2: (100, 0),
        3: (200, 0),
        4: (0, 100),
        5: (100, 100),
        6: (200, 100),
        7: (0, 200),
        8: (100, 200),
        9: (200, 200),
    }
}

altura_home = 300  # mm
altura_coger_pieza = 50  # mm por debajo de home
