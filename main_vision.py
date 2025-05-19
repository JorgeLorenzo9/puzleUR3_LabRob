# main.py
from vision_module import VisionModule
import shared_data

def main():
    vision = VisionModule()

    # Llamada a la detección de piezas (los argumentos pueden ser opcionales)
    vision.detectar_pieza()

    # Mostrar resultados
    print("\n=== RESULTADOS DE VISIÓN ===")
    print(f"Centroides detectados: {shared_data.vision_output_pixel_coords}")
    print(f"Número de pieza: {shared_data.vision_output_piece_number}")
    print(f"Rotación: {shared_data.vision_output_rotation}")

if __name__ == "__main__":
    main()
