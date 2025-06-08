import sys
import json
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QInputDialog, QLabel
)
from sklearn.linear_model import LinearRegression

JSON_PATH = "calibracion_ur3.json"
Z_FIJA = -0.19

def entrenar_y_guardar(calibration_data):
    data = np.array(calibration_data)
    u, v, x, y = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
    U = np.stack([u, v], axis=1)

    modelo_x = LinearRegression().fit(U, x)
    modelo_y = LinearRegression().fit(U, y)

    resultado = {
        "coef_x": modelo_x.coef_.tolist(),
        "intercept_x": modelo_x.intercept_,
        "coef_y": modelo_y.coef_.tolist(),
        "intercept_y": modelo_y.intercept_,
        "z_fija": Z_FIJA,
    }

    with open(JSON_PATH, "w") as f:
        json.dump(resultado, f, indent=4)

    print("✅ Calibración guardada en", JSON_PATH)

def cargar_modelo():
    with open(JSON_PATH, "r") as f:
        return json.load(f)

def predecir_tcp(modelo, u, v):
    X = np.dot(modelo["coef_x"], [u, v]) + modelo["intercept_x"]
    Y = np.dot(modelo["coef_y"], [u, v]) + modelo["intercept_y"]
    Z = modelo["z_fija"]
    return X, Y, Z

class AppManual(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Predicción Manual de Coordenadas TCP")
        self.setGeometry(200, 200, 400, 200)

        self.label = QLabel("Presiona un botón", self)
        self.btn_pred = QPushButton("Predecir desde (u,v)")
        self.btn_cal = QPushButton("Entrenar y Guardar Modelo")

        self.btn_pred.clicked.connect(self.predecir_uv)
        self.btn_cal.clicked.connect(self.entrenar_modelo)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_pred)
        layout.addWidget(self.btn_cal)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.modelo = None

    def predecir_uv(self):
        try:
            self.modelo = cargar_modelo()
        except:
            self.label.setText("❌ No se pudo cargar el modelo.")
            return

        while True:
            entrada, ok = QInputDialog.getText(self, "Predicción", "Introduce coordenadas u,v:")
            if not ok or entrada.lower() == "salir":
                break
            try:
                u_px, v_px = map(float, entrada.strip().split(","))
                X, Y, Z = predecir_tcp(self.modelo, u_px, v_px)
                resultado = f"TCP → X: {X:.2f} m, Y: {Y:.2f} m, Z: {Z:.2f} m"
                print(resultado)
                self.label.setText(resultado)
            except Exception as e:
                self.label.setText("❌ Entrada inválida.")
                print("❌ Error:", e)

    def entrenar_modelo(self):
        # Modifica esta lista con tus datos de calibración
        calibration_data = [
            [85, 79, 155, 469],
            [251, 104, 145, 379],
            [394, 84, 159, 313],
            [79, 274, 47, 476],
            [194, 232, 80, 419],
            [63, 399, -5, 487],
            
        ]
        entrenar_y_guardar(calibration_data)
        self.label.setText("✅ Modelo entrenado y guardado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AppManual()
    ventana.show()
    sys.exit(app.exec_())
