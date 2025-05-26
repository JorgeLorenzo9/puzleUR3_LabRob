from logic_module import LogicModule

def main():
    # Crear instancia de la lógica principal
    logic = LogicModule()

    # Definir coordenadas del centroide en píxeles (ejemplo)
    centroide_px = (553, 95)

    # Llamar a la función para convertir píxeles a coordenadas del robot
    pose = logic.pixel_to_mm(553,95)

    # (La función ya imprime la pose internamente)
    # Si quieres usarla directamente con el robot:
    # logic.ur3.move_to(pose)

if __name__ == "__main__":
    main()
