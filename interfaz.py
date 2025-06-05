import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import shared_data
from logic_module import LogicModule
import cv2
import os
import time


class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("UR3 Puzzle GUI")
        self.root.geometry("800x600")

        self.logic = LogicModule()
        self.selected_puzzle = None
        self.running = True

        style = ttk.Style()

        style.configure("Stop.TButton",
                        font=("Helvetica", 18, "bold"),
                        padding=20,
                        foreground="#B1544D",
                        background="#C0392B")
        
        style.map("Stop.TButton",
                  background=[('active', '#922B21')])


        
        style.configure("Big.TButton",
                        font=("Helvetica", 18, "bold"),
                        padding=20,
                        foreground="#5F97CF",
                        background="#2980B9")  # Azul bonito
        style.map("Big.TButton",
                background=[('active', '#1F618D')])

        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.attributes('-fullscreen', True)

        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen(False))
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen(True))

        self.logic_thread = threading.Thread(target=self.run_logic_loop, daemon=True)
        self.logic_thread.start()

        self.show_welcome_screen()

    def toggle_fullscreen(self, enable=True):
        if enable:
            try:
                self.root.state('zoomed')
            except tk.TclError:
                self.root.attributes('-fullscreen', True)
        else:
            self.root.attributes('-fullscreen', False)
            self.root.state('normal')
            self.root.geometry("1000x700")

    def run_logic_loop(self):
        while self.running and self.logic.estado != -1:
            if self.logic.estado == 1:
                if shared_data.num_puzzle != 0:
                    self.logic.run_state_machine()
            elif self.logic.estado == 9:
                self.update_puzzle_display()
                self.logic.run_state_machine()
            else:
                self.logic.run_state_machine()
            threading.Event().wait(1)

    def show_welcome_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        try:
            fondo_img = Image.open("assets/fondo_bienvenida.png").resize((1920, 1000))
            self.bg_image = ImageTk.PhotoImage(fondo_img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        except:
            self.canvas.configure(bg="#D6EAF8")

        self.canvas.create_text(800, 100, text="Resolviendo Puzzle con UR3",
                                font=("Helvetica", 28, "bold"), fill="#154360")
        pass

        continuar_btn = ttk.Button(self.root, text="Comenzar",
                           style="Big.TButton",
                           command=self.show_puzzle_selection)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.canvas.create_window(screen_width // 2,
                                screen_height - 250,
                                window=continuar_btn)


    def show_puzzle_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        title_label = ttk.Label(self.root,
                        text="Selecciona un puzzle para resolver con UR3",
                        font=("Helvetica", 28, "bold"),
                        foreground="#154360",
                        background="#EBF5FB",
                        anchor="center")
        title_label.pack(pady=20, fill="x")

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
                img = Image.open(f"puzzles/puzzle{i+1}.png").resize((200, 200))
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

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(main_frame)
        self.left_frame.pack(side="left", fill="both", expand=True)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        label = ttk.Label(self.left_frame, text=f"Resolviendo Puzzle {self.selected_puzzle} - Vista de cámara",
                        font=("Helvetica", 16))
        label.pack(pady=10)

        self.video_label = tk.Label(self.left_frame)
        self.video_label.pack()

        self.console = tk.Text(self.left_frame, height=10)
        self.console.pack(pady=10, fill="x")

        self.puzzle_frame = tk.Frame(right_frame)
        self.puzzle_frame.pack(padx=20, pady=20)
        self.puzzle_cells = {}

        for row in range(3):
            for col in range(3):
                frame = tk.Frame(self.puzzle_frame, width=150, height=150, relief="sunken", borderwidth=2)
                frame.grid(row=row, column=col, padx=5, pady=5)
                self.puzzle_cells[row*3+col+1] = frame
        # Botón de STOP abajo a la derecha
        stop_button = ttk.Button(self.root, text="🛑 PARAR", command=self.stop_robot, style="Stop.TButton")
        stop_button.place(x=1100, y=700)

        # MOSTRAR INTERFAZ PRIMERO, luego iniciar lo demás
        self.root.after(100, self.init_camera_and_threads)

    def init_camera_and_threads(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.redirect_stdout_to_console()

        threading.Thread(target=self.update_camera_feed, daemon=True).start()
        threading.Thread(target=self.simulate_update, daemon=True).start()

    import time

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
        pieza_id = shared_data.vision_output_piece_number
        num_puzzle = shared_data.num_puzzle

        if pieza_id in self.puzzle_cells and num_puzzle != 0:
            img_path = f"assets/piezas/pieza{num_puzzle}_{pieza_id}.jpg"
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((140, 140))
                img_tk = ImageTk.PhotoImage(img)
                label = tk.Label(self.puzzle_cells[pieza_id], image=img_tk)
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

    def stop_robot(self):
        print("[UI] Botón STOP pulsado. Enviando parada al sistema.")
        self.logic.estado = 99  # Estado especial de parada de emergencia

    def simulate_update(self):
        time.sleep(3)
        shared_data.num_puzzle = 1
        for i in range(1, 10):
            shared_data.vision_output_piece_number = i
            self.update_puzzle_display()
            time.sleep(1)
