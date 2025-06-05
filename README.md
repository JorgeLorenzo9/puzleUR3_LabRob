# puzleUR3_LabRob
Este repositorio ha sido creado para subir todo el material relacionado con el proyecto "Montaje de un Puzle de dimensiones conocidas a través de un manipulador UR3" de la asignatura Laboratorio de Robótica, perteneciente al Máster Universitario en Automática y Robótica

En este archivo se recogen una serie de pasos para el uso de la interfaz creada para el usuario, que permite el entendimiento y manipulación de la interfaz a través de la introducción de una foto del puzle a formar.
## Tabla de contenido
## Arquitectura del Software
## Clases
- Shared_data: "Esto no es una clase como tal"
- UR3Module():
- VisionModule():
- LogicModule():
### Módulo del UR3
- __init__(): 
    -Se establece la conexión del robot con el sistema a traves de la ip para controlar la interfaz, recibir datos de ella y controlar las E/S.
    - Se establecen los parametros de velocidad y aceleración.
- move_to(target_pose): Recibe las coordenadas cartesianas "poner (x,y,z...)"donde ha de estar el efector final respecto a la base en metros "revisar", realiza la cinemática inversa transformandolas a coordenadas articulares y mueve el robot.
- set_gripper(status): si recibe un true activa la succión del gripper y si recibe un false la desactiva.
- rotate() mueve el robot gracias a tener almacenada la secuencia para rotar la pieza.
- catch_puzzle(): coge la pieza de la zona de rotación.
- leave_puzzle(): deja la pieza en la zona de rotación.
- move_to_final_position(path, return_path): recibe dos conjuntos de puntos de paso para llevar las piezas desde la zona de rotación a su posición final, dejar la pieza y retornar a la posición intermedia.
- get_actual_pose(): devuelve la posición del efector respecto  a la base en coordenadas cartesianas.
### Módulo de lógica
- __init__(): iniciamos módulos de control del UR3 y Visión
- run_state_machine(): Máquina de estados para controlar el proceso.
    - Estado 1: LLevar al robot a la posición de HOME
    - Estado 2: Detectar la pieza:
        - vision.detectar_pieza() devuelve true si ha almacenado todos los centroides (x,y) de todas las piezas del puzzle en el area de trabajo.
        - visión actualiza la variable global centroides_robot (aqui revisar porque creo que hay variables duplicadas)
### Módulo de visión
- __init__(): Se carga la imagen del puzzle y se establecen los parámetros del detector.
- detectar_pieza(self)->bool: True si detecta los 9 centroides.
Actualiza las variable:
    - centroides_robot: (9,2) "revisar esto que nose si se pone asi o asi (2,9)"
-comparar_con_puzzle_completo(self, pieza_num=None)-> float: devuelve el numero de la pieza a la que corresponde si pertenece a ese puzzle y 0 si la pieza no es correcta o surge cualquier otra excepción.

## Calibración