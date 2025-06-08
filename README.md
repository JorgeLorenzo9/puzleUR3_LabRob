
# 🤖 Puzzle Solver con UR3 y Visión 
Este repositorio ha sido creado para subir todo el material relacionado con el proyecto "Montaje de un Puzle de dimensiones conocidas a través de un manipulador UR3" de la asignatura Laboratorio de Robótica, perteneciente al Máster Universitario en Automática y Robótica.

![Mi foto](puzzles/Screenshot%20from%202025-06-08%2009-45-17.png)



Este proyecto implementa un sistema modular en Python para resolver automáticamente un puzzle 3x3 utilizando un **robot UR3**, **visión** y control mediante **RTDE**. El sistema detecta, recoge, orienta y coloca las piezas del puzzle de forma autónoma.

## 📁 Estructura del proyecto

- `main.py` – Punto de entrada del sistema. Gestiona la lógica principal mediante una máquina de estados.
- `logic.py` – Controla la secuencia de estados del proceso.
- `robot_controller.py` – Control del robot UR3 usando RTDE.
- `vision.py` – Procesamiento de imagen y detección de piezas.
- `shared_data.py` – Variables globales y trayectorias predefinidas compartidas entre módulos.

## ⚙️ Requisitos

- Python 3.8 o superior
- Librería RTDE (de Universal Robots)
- OpenCV (`opencv-python`)
- NumPy

## Modo de uso
Antes de iniciar el sistema, asegúrate de cargar en el módulo de visión una imagen del puzzle completo que se desea resolver. Esta imagen se utiliza como referencia para verificar la orientación de las piezas.

Coloca las nueve piezas del puzzle en el área de trabajo, justo debajo de la posición HOME del robot UR3. Esta posición permite una vista cenital adecuada para que la cámara pueda detectar correctamente las piezas.

En el archivo donde se inicializa la cámara, asegúrate de verificar y ajustar el valor en la línea:

```python
cap = cv2.VideoCapture(2)
```

El número entre paréntesis representa el índice de la cámara.Si la cámara no se activa correctamente, prueba a cambiar este valor hasta que se muestre la imagen esperada.

En el módulo del robot, es necesario modificar las siguientes líneas para que coincidan con la dirección IP del UR3 que se está utilizando:

```python
self.rtde_c = rtde_control.RTDEControlInterface("169.254.12.28")
self.rtde_r = rtde_receive.RTDEReceiveInterface("169.254.12.28")
self.rtde_io = rtde_io.RTDEIOInterface("169.254.12.28")
```
Sustituye "169.254.12.28" por la IP correcta del robot UR3. Si no conoces cuál es, conecta el robot mediante un cable Ethernet directamente al ordenador y ejecuta el comando ifconfig (en Linux/macOS) o ipconfig (en Windows) para ver qué IP se asigna en la interfaz Ethernet.

```
ping <IP_DEL_UR3>
```
Si el código da errores por problemas de conexión, prueba a desactivar la conexión Wi-Fi y dejar únicamente activa la conexión por cable Ethernet. Esto evita conflictos de red y asegura una comunicación estable con el UR3.