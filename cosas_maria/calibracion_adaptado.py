import sys
import cv2
import numpy as np
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QInputDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import QTimer, Qt
from sklearn.linear_model import LinearRegression

# Ruta del archivo JSON para guardar la calibración
JSON_PATH = "calibracion_ur3.json"
# Altura fija del plano de trabajo en coordenadas del robot (en metros)
# ¡IMPORTANTE! Ajusta este valor a la altura real de tu mesa de trabajo respecto a la base del robot.
# Por ejemplo, si la mesa está a 24.13 cm de la base del robot en el eje Z.
Z_FIJA = 0.24130077681581635

def detectar_objetos(imagen, umbral_area=500):
    """
    Detecta objetos en la imagen basándose en rangos de color HSV.
    Esta función está diseñada para ser genérica y puede adaptarse para detectar cubos
    u otros objetos específicos. Actualmente, utiliza rangos de color comunes.

    Args:
        imagen (numpy.ndarray): El frame de la imagen de la cámara (BGR).
        umbral_area (int): El área mínima de un contorno para ser considerado un objeto.

    Returns:
        list: Una lista de tuplas (nombre_color, u, v) para cada objeto detectado,
              donde (u, v) son las coordenadas de píxeles del centro del objeto.
    """
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    # Define rangos de color para la detección.
    # Puedes ajustar estos rangos o añadir más colores según los cubos que vayas a usar.
    # Formato: "NombreColor": [(H_min, S_min, V_min), (H_max, S_max, V_max)]
    colores = {
        "Rojo1": [(0, 100, 100), (10, 255, 255)],
        "Rojo2": [(160, 100, 100), (179, 255, 255)],
        "Amarillo": [(10, 100, 100), (30, 255, 255)],
        "Verde": [(35, 80, 80), (85, 255, 255)],
        "Azul": [(90, 50, 50), (130, 255, 255)],
        "Naranja": [(5, 100, 100), (25, 255, 255)],
        "Morado": [(130, 50, 50), (160, 255, 255)],
    }

    objetos_detectados = []
    kernel = np.ones((5, 5), np.uint8) # Kernel para operaciones morfológicas (apertura y cierre)

    for color_nombre, (lower, upper) in colores.items():
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        mascara = cv2.inRange(hsv, lower, upper) # Crea una máscara binaria (blanco para el color, negro para el resto)

        # Aplicar operaciones morfológicas para limpiar la máscara (eliminar ruido y cerrar pequeños agujeros)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)

        # Encontrar contornos de los objetos en la máscara
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Filtrar contornos por área para eliminar ruido pequeño o falsas detecciones
        contornos_filtrados = [cnt for cnt in contornos if cv2.contourArea(cnt) > umbral_area]

        for contorno in contornos_filtrados:
            # Obtener el rectángulo delimitador del contorno y calcular el centro (u, v)
            x, y, w, h = cv2.boundingRect(contorno)
            u = x + w // 2
            v = y + h // 2
            objetos_detectados.append((color_nombre, u, v)) # Almacena el nombre del color y las coordenadas del centro

    return objetos_detectados

def entrenar_y_guardar(calibration_data):
    """
    Entrena un modelo de regresión lineal para mapear coordenadas de píxeles (u, v)
    a coordenadas del robot (x, y) y guarda el modelo en un archivo JSON.

    Args:
        calibration_data (list): Lista de puntos de calibración [u, v, x_robot, y_robot].

    Returns:
        bool: True si el entrenamiento y guardado fueron exitosos, False en caso contrario.
    """
    if len(calibration_data) < 3: # Se necesitan al menos 3 puntos para una regresión robusta en 2D
        QMessageBox.warning(None, "Error de Calibración", "Se necesitan al menos 3 puntos de calibración para entrenar el modelo.")
        return False

    data = np.array(calibration_data)
    # Extraer las coordenadas de píxeles (u, v) y las coordenadas del robot (x, y)
    u, v, x, y = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
    U = np.stack([u, v], axis=1) # Matriz de características para la regresión (píxeles)

    # Entrenar modelos de regresión lineal separados para X e Y
    # Esto asume una relación lineal entre píxeles y coordenadas del robot,
    # lo cual es común para una calibración de cámara plana.
    modelo_x = LinearRegression().fit(U, x)
    modelo_y = LinearRegression().fit(U, y)

    # Preparar los resultados para guardar en formato JSON
    resultado = {
        "coef_x": modelo_x.coef_.tolist(),      # Coeficientes del modelo para X
        "intercept_x": modelo_x.intercept_,     # Intercepto del modelo para X
        "coef_y": modelo_y.coef_.tolist(),      # Coeficientes del modelo para Y
        "intercept_y": modelo_y.intercept_,     # Intercepto del modelo para Y
        "z_fija": Z_FIJA,                       # La coordenada Z fija del plano de trabajo
    }

    try:
        with open(JSON_PATH, "w") as f:
            json.dump(resultado, f, indent=4) # Guarda el JSON con indentación para legibilidad
        QMessageBox.information(None, "Calibración Exitosa", f"✅ Calibración guardada en {JSON_PATH}")
        return True
    except Exception as e:
        QMessageBox.critical(None, "Error al Guardar", f"❌ Error al guardar la calibración: {e}")
        return False

def cargar_modelo():
    """
    Carga el modelo de calibración desde el archivo JSON.

    Returns:
        dict or None: El diccionario del modelo si se carga correctamente, None en caso de error.
    """
    try:
        with open(JSON_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Informar al usuario si el archivo no existe
        QMessageBox.warning(None, "Archivo no Encontrado", f"El archivo de calibración '{JSON_PATH}' no existe. Por favor, calibra primero.")
        return None
    except json.JSONDecodeError:
        # Informar al usuario si el archivo JSON está corrupto
        QMessageBox.critical(None, "Error de JSON", f"Error al leer el archivo de calibración '{JSON_PATH}'. El formato es incorrecto.")
        return None

def predecir_tcp(modelo, u, v):
    """
    Predice las coordenadas del robot (X, Y, Z) a partir de las coordenadas de píxeles (u, v)
    utilizando el modelo de calibración cargado.

    Args:
        modelo (dict): El diccionario del modelo de calibración.
        u (float): Coordenada u (horizontal) del píxel.
        v (float): Coordenada v (vertical) del píxel.

    Returns:
        tuple or (None, None, None): Las coordenadas (X, Y, Z) del robot en metros,
                                     o (None, None, None) si el modelo no está cargado.
    """
    if modelo is None:
        return None, None, None

    # Calcular X e Y usando los coeficientes e interceptos del modelo
    # X = coef_x[0]*u + coef_x[1]*v + intercept_x
    X = np.dot(modelo["coef_x"], [u, v]) + modelo["intercept_x"]
    Y = np.dot(modelo["coef_y"], [u, v]) + modelo["intercept_y"]
    Z = modelo["z_fija"] # Utiliza la Z fija definida en la calibración

    return X, Y, Z

class DetectorGUI(QMainWindow):
    """
    Clase de la interfaz gráfica de usuario para la detección de objetos y calibración
    de la cámara con el robot UR.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibración Cámara-Robot UR")
        self.setGeometry(100, 100, 1000, 700) # Aumentar el tamaño de la ventana para mejor visualización

        # Etiqueta para mostrar el feed de la cámara
        self.label_camara = QLabel("Cámara")
        self.label_camara.setScaledContents(True) # Escala la imagen para ajustarse al tamaño del QLabel
        self.label_camara.setAlignment(Qt.AlignCenter) # Centra la imagen en el QLabel

        # Botones de control para el proceso de calibración
        self.btn_add_point = QPushButton("1. Añadir Punto de Calibración")
        self.btn_add_point.clicked.connect(self.add_calibration_point)
        # Estilos CSS para los botones para una mejor apariencia
        self.btn_add_point.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")

        self.btn_train_model = QPushButton("2. Entrenar Modelo")
        self.btn_train_model.clicked.connect(self.train_model)
        self.btn_train_model.setStyleSheet("background-color: #2196F3; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")

        self.btn_predict = QPushButton("3. Probar Predicción")
        self.btn_predict.clicked.connect(self.test_prediction)
        self.btn_predict.setStyleSheet("background-color: #FFC107; color: black; font-size: 16px; padding: 10px; border-radius: 8px;")

        self.btn_clear_points = QPushButton("Limpiar Puntos de Calibración")
        self.btn_clear_points.clicked.connect(self.clear_calibration_points)
        self.btn_clear_points.setStyleSheet("background-color: #f44336; color: white; font-size: 14px; padding: 8px; border-radius: 6px;")

        # Etiqueta de estado para informar al usuario sobre el progreso
        self.label_status = QLabel("Estado: Listo para calibrar.")
        self.label_status.setFont(QFont("Arial", 12))
        self.label_status.setStyleSheet("color: #333; margin-top: 10px;")

        # Layout horizontal para los botones principales
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_add_point)
        button_layout.addWidget(self.btn_train_model)
        button_layout.addWidget(self.btn_predict)

        # Layout principal vertical que contiene la cámara, los botones y el estado
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label_camara)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.btn_clear_points)
        main_layout.addWidget(self.label_status)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Inicialización de la captura de vídeo
        # Intenta con el índice 2 y el backend V4L2 (común en Linux para webcams)
        self.cap = cv2.VideoCapture(2, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0) # Si falla, intenta con el índice 0 (cámara predeterminada)
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Error de Cámara", "No se pudo abrir la cámara. Asegúrate de que esté conectada y no esté en uso.")
                sys.exit(1) # Sale de la aplicación si no se puede abrir la cámara

        # Configuración del temporizador para actualizar el frame de la cámara
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30) # Actualizar cada 30 ms (aproximadamente 33 FPS)

        self.modelo = cargar_modelo() # Cargar el modelo de calibración al inicio si ya existe
        self.calibration_points = [] # Lista para almacenar los puntos de calibración [u, v, x_robot, y_robot]
        self.detected_objects_current_frame = [] # Almacena los objetos detectados en el frame actual

        # Actualizar el estado inicial de la GUI
        if self.modelo:
            self.label_status.setText("Estado: Modelo de calibración cargado. Listo para probar.")
        else:
            self.label_status.setText("Estado: No hay modelo de calibración. Por favor, añade puntos y entrena.")


    def actualizar_frame(self):
        """
        Captura un frame de la cámara, detecta objetos, dibuja la información
        y actualiza la visualización en la GUI.
        """
        ret, frame = self.cap.read()
        if not ret:
            self.label_status.setText("Error: No se pudo leer el frame de la cámara.")
            return

        # Detectar objetos en el frame actual
        self.detected_objects_current_frame = detectar_objetos(frame)

        # Crear una copia del frame para dibujar sobre ella y no modificar el original
        display_frame = frame.copy()

        # Dibujar los objetos detectados y sus coordenadas de píxeles
        for i, (color, u, v) in enumerate(self.detected_objects_current_frame):
            # Dibujar el punto en el centro del objeto
            cv2.circle(display_frame, (u, v), 7, (0, 255, 255), -1) # Amarillo, relleno
            # Dibujar un círculo exterior para mayor visibilidad
            cv2.circle(display_frame, (u, v), 10, (0, 0, 255), 2) # Rojo, contorno

            # Mostrar texto con el índice, color y coordenadas de píxeles
            text = f"{i+1} ({color}): ({u},{v})"
            cv2.putText(display_frame, text, (u + 15, v - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA) # Azul claro

        # Si hay puntos de calibración recolectados, dibujarlos también para referencia
        for i, (u_cal, v_cal, x_rob, y_rob) in enumerate(self.calibration_points):
            cv2.circle(display_frame, (int(u_cal), int(v_cal)), 10, (255, 0, 0), -1) # Azul, relleno
            cv2.putText(display_frame, f"Punto {i+1} Calibrado", (int(u_cal) + 15, int(v_cal) + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)


        # Convertir el frame de OpenCV (BGR) a formato QImage (RGB) para PyQt
        rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        img_qt = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label_camara.setPixmap(QPixmap.fromImage(img_qt)) # Muestra la imagen en el QLabel

    def add_calibration_point(self):
        """
        Permite al usuario añadir un punto de calibración de forma interactiva.
        El usuario selecciona un objeto detectado en la cámara y luego proporciona
        sus coordenadas correspondientes en el espacio del robot.
        """
        if not self.detected_objects_current_frame:
            QMessageBox.warning(self, "No hay objetos", "No se detectaron objetos en el frame actual. Asegúrate de que un cubo esté visible.")
            return

        # Construir una lista de opciones para el QInputDialog, mostrando los objetos detectados
        items = [f"{i+1}: {color} (u={u}, v={v})" for i, (color, u, v) in enumerate(self.detected_objects_current_frame)]
        item, ok = QInputDialog.getItem(self, "Seleccionar Objeto", "Selecciona el objeto para calibrar:", items, 0, False)

        if ok and item:
            selected_index = items.index(item)
            _, u_px, v_px = self.detected_objects_current_frame[selected_index] # Obtener las coordenadas de píxeles del objeto seleccionado

            # Pedir las coordenadas del robot al usuario
            robot_coords_str, ok_coords = QInputDialog.getText(self, "Coordenadas del Robot",
                                                               f"Introduce las coordenadas X,Y del robot (ej. 0.123, -0.456) para el objeto en ({u_px},{v_px}):")

            if ok_coords and robot_coords_str:
                try:
                    # Parsear las coordenadas del robot de la entrada del usuario
                    x_robot, y_robot = map(float, robot_coords_str.strip().split(","))
                    # Añadir el punto de calibración a la lista
                    self.calibration_points.append([u_px, v_px, x_robot, y_robot])
                    self.label_status.setText(f"Punto añadido: ({u_px},{v_px}) -> ({x_robot:.3f},{y_robot:.3f}). Total: {len(self.calibration_points)} puntos.")
                    print(f"Punto de calibración añadido: Píxel ({u_px}, {v_px}), Robot ({x_robot:.3f}, {y_robot:.3f})")
                except ValueError:
                    QMessageBox.warning(self, "Entrada Inválida", "Formato de coordenadas del robot incorrecto. Usa X,Y (ej. 0.123,-0.456).")
            else:
                QMessageBox.information(self, "Calibración Cancelada", "Entrada de coordenadas del robot cancelada.")
        else:
            QMessageBox.information(self, "Calibración Cancelada", "Selección de objeto cancelada.")

    def clear_calibration_points(self):
        """
        Limpia todos los puntos de calibración recolectados y resetea el modelo.
        """
        reply = QMessageBox.question(self, 'Confirmar', '¿Estás seguro de que quieres limpiar todos los puntos de calibración?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.calibration_points = []
            self.modelo = None # Resetear el modelo también
            self.label_status.setText("Estado: Puntos de calibración limpiados. Por favor, añade nuevos puntos y entrena.")
            QMessageBox.information(self, "Puntos Limpiados", "Todos los puntos de calibración han sido eliminados.")

    def train_model(self):
        """
        Entrena el modelo de calibración con los puntos recolectados.
        """
        if entrenar_y_guardar(self.calibration_points):
            self.modelo = cargar_modelo() # Recargar el modelo recién guardado
            if self.modelo:
                self.label_status.setText("Estado: Modelo entrenado y cargado. Listo para probar predicciones.")
            else:
                self.label_status.setText("Estado: Error al cargar el modelo después del entrenamiento.")

    def test_prediction(self):
        """
        Permite al usuario probar el modelo de calibración introduciendo coordenadas de píxeles
        y viendo las coordenadas del robot predichas.
        """
        if self.modelo is None:
            QMessageBox.warning(self, "Modelo no Calibrado", "El modelo de calibración no ha sido entrenado o cargado. Por favor, calibra primero.")
            return

        while True:
            entrada, ok = QInputDialog.getText(self, "Probar Predicción", "Introduce coordenadas u,v de un objeto detectado (ej. 300,200) o 'salir' para finalizar:")
            if not ok or entrada.lower() == "salir":
                break
            try:
                u_px, v_px = map(float, entrada.strip().split(","))
                X, Y, Z = predecir_tcp(self.modelo, u_px, v_px)
                if X is not None:
                    QMessageBox.information(self, "Predicción", f"→ Coordenadas TCP: X = {X:.4f} m, Y = {Y:.4f} m, Z = {Z:.4f} m")
                    print(f"→ Coordenadas TCP: X = {X:.4f} m, Y = {Y:.4f} m, Z = {Z:.4f} m")
                else:
                    QMessageBox.critical(self, "Error de Predicción", "No se pudo realizar la predicción. Asegúrate de que el modelo esté cargado.")
            except ValueError:
                QMessageBox.warning(self, "Entrada Inválida", "Formato de entrada incorrecto. Usa u,v (ej. 300,200).")
            except Exception as e:
                QMessageBox.critical(self, "Error Inesperado", f"❌ Error inesperado durante la predicción: {e}")

    def closeEvent(self, event):
        """
        Libera la cámara cuando la aplicación se cierra para evitar problemas de acceso.
        """
        if self.cap.isOpened():
            self.cap.release()
        event.accept() # Acepta el evento de cierre de la ventana

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = DetectorGUI()
    ventana.show()
    sys.exit(app.exec_())
