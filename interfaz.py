import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import shared_data
from logic_module import LogicModule
import cv2
import os

class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("UR3 Puzzle GUI")
        self.root.geometry("800x600")

        self.logic = LogicModule()
        self.selected_puzzle = None
        self.running = True

        try:
            # Windows suele entender 'zoomed'
            self.root.state('zoomed')
        except tk.TclError:
            # fallback universal
            self.root.attributes('-fullscreen', True)

        # 3️⃣  (Opcional) Tecla Esc para salir de fullscreen
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen(False))
        self.root.bind('<F11>',   lambda e: self.toggle_fullscreen(True))

        # Iniciar la máquina de estados en un hilo aparte
        self.logic_thread = threading.Thread(target=self.run_logic_loop, daemon=True)
        self.logic_thread.start()

        self.show_welcome_screen()

    def run_logic_loop(self):
        while self.running and self.logic.estado != -1:
            if self.logic.estado == 1:
                if shared_data.num_puzzle != 0:
                    self.logic.run_state_machine()
                # Si num_puzzle es 0, esperamos selección desde GUI
            elif self.logic.estado == 9:
                self.update_puzzle_display()
                self.logic.run_state_machine()
            else:
                self.logic.run_state_machine()
            threading.Event().wait(1)

            
        def toggle_fullscreen(self, enable=True):
            if enable:
                try:
                    self.root.state('zoomed')
                except tk.TclError:
                    self.root.attributes('-fullscreen', True)
            else:
                # Vuelve a ventana normal de un tamaño razonable
                self.root.attributes('-fullscreen', False)
                self.root.state('normal')
                self.root.geometry("1000x700")  # o lo que prefieras


    def show_welcome_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        try:
            fondo_img = Image.open("assets/fondo_bienvenida.jpg").resize((800, 600))
            self.bg_image = ImageTk.PhotoImage(fondo_img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        except:
            self.canvas.configure(bg="#D6EAF8")

        self.canvas.create_text(400, 100, text="Bienvenido a Resolviendo Puzzle con UR3",
                                font=("Helvetica", 28, "bold"), fill="#154360")

        try:
            decor_img = Image.open("assets/robot_ur3.jpg").resize((200, 200))
            self.robot_img = ImageTk.PhotoImage(decor_img)
            self.canvas.create_image(400, 250, image=self.robot_img)
        except:
            pass

        continuar_btn = ttk.Button(self.root, text="Comenzar", command=self.show_puzzle_selection)
        self.canvas.create_window(400, 500, window=continuar_btn)

    def show_puzzle_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        title_label = ttk.Label(self.root, text="Selecciona un puzzle", font=("Helvetica", 18))
        title_label.pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        self.puzzle_imgs = []
        total_puzzles = 6
        cols = 3

        for i in range(total_puzzles):
            fila = i // cols
            columna = i % cols

            sub_frame = tk.Frame(frame)
            sub_frame.grid(row=fila, column=columna, padx=20, pady=15)

            try:
                img = Image.open(f"puzzles/puzzle{i+1}.jpg").resize((200, 200))
                img_tk = ImageTk.PhotoImage(img)
                self.puzzle_imgs.append(img_tk)
            except:
                continue

            btn = tk.Button(sub_frame, image=self.puzzle_imgs[i],
                            command=lambda i=i: self.select_puzzle(i+1))
            btn.pack()

            lbl = tk.Label(sub_frame, text=f"Puzzle {i+1}", font=("Helvetica", 12))
            lbl.pack(pady=5)

    def select_puzzle(self, puzzle_number):
        self.selected_puzzle = puzzle_number
        shared_data.num_puzzle = puzzle_number
        print(f"Puzzle {puzzle_number} seleccionado")
        self.show_camera_feed()

    def show_camera_feed(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        label = ttk.Label(self.root, text=f"Resolviendo Puzzle {self.selected_puzzle} - Vista de cámara",
                          font=("Helvetica", 16))
        label.pack(pady=10)

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        # Panel derecho para simular puzzle 3x3
        self.puzzle_frame = tk.Frame(self.root)
        self.puzzle_frame.pack(side="right", padx=20)
        self.puzzle_cells = {}

        for row in range(3):
            for col in range(3):
                frame = tk.Frame(self.puzzle_frame, width=80, height=80, relief="sunken", borderwidth=1)
                frame.grid(row=row, column=col, padx=5, pady=5)
                label = tk.Label(frame, text=f"{row*3+col+1}")
                label.pack()
                self.puzzle_cells[row*3+col+1] = frame

        # Zona consola
        self.console = tk.Text(self.root, height=10, width=100)
        self.console.pack(pady=10)

        self.cap = cv2.VideoCapture(0)
        self.running = True
        threading.Thread(target=self.update_camera_feed, daemon=True).start()
        self.redirect_stdout_to_console()

    def update_camera_feed(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = img.resize((500, 400))
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            threading.Event().wait(0.05)

    def update_puzzle_display(self):
        pieza = shared_data.numero_pieza_actual
        if pieza in self.puzzle_cells:
            img_path = f"assets/piezas/pieza{pieza}.jpg"
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((80, 80))
                img_tk = ImageTk.PhotoImage(img)
                label = tk.Label(self.puzzle_cells[pieza], image=img_tk)
                label.image = img_tk
                label.pack()

    def redirect_stdout_to_console(self):
        import sys
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, s):
                self.text_widget.insert(tk.END, s)
                self.text_widget.see(tk.END)

            def flush(self):
                pass

        sys.stdout = StdoutRedirector(self.console)
        sys.stderr = StdoutRedirector(self.console)
