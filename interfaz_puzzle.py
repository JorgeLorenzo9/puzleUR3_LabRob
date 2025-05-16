import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading

# Clase principal
class PuzzleUR3App:
    def __init__(self, root):
        self.root = root
        self.root.title("Resolviendo puzzle con UR3")
        self.root.geometry("800x600")
        self.selected_puzzle = None

        # Inicia en la pantalla de bienvenida
        self.show_welcome_screen()

    def show_welcome_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Crear un canvas para fondo
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        # Cargar imagen de fondo (opcional)
        try:
            fondo_img = Image.open("assets/fondo_bienvenida.jpg")
            fondo_img = fondo_img.resize((800, 600))
            self.bg_image = ImageTk.PhotoImage(fondo_img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        except Exception as e:
            print(f"No se pudo cargar la imagen de fondo: {e}")
            self.canvas.configure(bg="#D6EAF8")  # Color azul claro si no hay imagen

        # Texto de bienvenida
        self.canvas.create_text(
            400, 100,
            text="Bienvenido a Resolviendo Puzzle con UR3",
            font=("Helvetica", 28, "bold"),
            fill="#154360"
        )

        # Imagen decorativa (robot, puzzle, etc.)
        try:
            decor_img = Image.open("assets/robot_ur3.jpg")
            decor_img = decor_img.resize((200, 200))
            self.robot_img = ImageTk.PhotoImage(decor_img)
            self.canvas.create_image(400, 250, image=self.robot_img)
        except Exception as e:
            print(f"No se pudo cargar imagen decorativa: {e}")

        # Botón continuar
        continuar_btn = ttk.Button(self.root, text="Comenzar", command=self.show_puzzle_selection)
        continuar_window = self.canvas.create_window(400, 500, window=continuar_btn)


    def show_puzzle_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        title_label = ttk.Label(self.root, text="Selecciona un puzzle", font=("Helvetica", 18))
        title_label.pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        self.puzzle_imgs = []

        # Crear 6 puzzles (2 filas de 3)
        total_puzzles = 6
        cols = 3

        for i in range(total_puzzles):
            fila = i // cols
            columna = i % cols

            # Crear sub-frame para cada puzzle
            sub_frame = tk.Frame(frame)
            sub_frame.grid(row=fila, column=columna, padx=20, pady=15)

            # Cargar imagen
            try:
                img = Image.open(f"puzzles/puzzle{i+1}.jpg")
                img = img.resize((200, 200))
                img_tk = ImageTk.PhotoImage(img)
                self.puzzle_imgs.append(img_tk)
            except Exception as e:
                print(f"No se pudo cargar puzzle{i+1}.jpg: {e}")
                continue

            # Botón con imagen
            btn = tk.Button(sub_frame, image=self.puzzle_imgs[i],
                            command=lambda i=i: self.select_puzzle(i+1))
            btn.pack()

            # Nombre del puzzle
            lbl = tk.Label(sub_frame, text=f"Puzzle {i+1}", font=("Helvetica", 12))
            lbl.pack(pady=5)



    def select_puzzle(self, puzzle_number):
        self.selected_puzzle = puzzle_number
        print(f"Puzzle {puzzle_number} seleccionado")
        self.show_camera_feed()

    def show_camera_feed(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.running = True

        # Frame general con 2 columnas: cámara (izquierda) + cuadrícula (derecha)
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # === CÁMARA ===
        camera_frame = tk.Frame(main_frame)
        camera_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        camera_label = ttk.Label(camera_frame, text=f"Resolviendo Puzzle {self.selected_puzzle} - Cámara")
        camera_label.pack()

        self.video_label = tk.Label(camera_frame)
        self.video_label.pack()

        self.cap = cv2.VideoCapture(0)
        threading.Thread(target=self.update_camera_feed, daemon=True).start()

        # === CUADRÍCULA DE PIEZAS ===
        grid_frame = tk.Frame(main_frame)
        grid_frame.grid(row=0, column=1, padx=30, pady=10)

        grid_title = ttk.Label(grid_frame, text="Progreso del Puzzle", font=("Helvetica", 14))
        grid_title.pack()

        self.piece_frames = []
        self.piece_imgs = []

        grid_container = tk.Frame(grid_frame)
        grid_container.pack()

        for i in range(3):
            for j in range(3):
                piece_label = tk.Label(grid_container, width=100, height=100, borderwidth=2, relief="solid")
                piece_label.grid(row=i, column=j, padx=5, pady=5)
                self.piece_frames.append(piece_label)
                self.piece_imgs.append(None)

        # Botón salir
        exit_button = ttk.Button(self.root, text="Salir", command=self.exit_app)
        exit_button.pack(pady=10)
    def update_puzzle_grid(self, pieza_id):
        """
        Actualiza la imagen correspondiente a la celda del puzzle resuelto.
        :param pieza_id: int de 1 a 9
        """
        if not (1 <= pieza_id <= 9):
            print(f"ID de pieza inválido: {pieza_id}")
            return

        index = pieza_id - 1
        try:
            img = Image.open(f"piezas/pieza{pieza_id}.jpg")
            img = img.resize((100, 100), Image.ANTIALIAS)
            img_tk = ImageTk.PhotoImage(img)

            self.piece_frames[index].configure(image=img_tk)
            self.piece_frames[index].image = img_tk  # Referencia para evitar recolección de basura
            print(f"Pieza {pieza_id} colocada en la cuadrícula.")
        except Exception as e:
            print(f"Error cargando pieza {pieza_id}: {e}")


    def update_camera_feed(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (320, 240))  # Tamaño reducido
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)


    def exit_app(self):
        self.running = False
        if hasattr(self, 'cap'):
            self.cap.release()
        self.root.destroy()

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleUR3App(root)
    root.mainloop()
