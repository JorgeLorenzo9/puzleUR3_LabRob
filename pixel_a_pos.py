modelo = {
    "coef_x": [
        0.0301261460888152,
        -0.5024140146130534
    ],
    "intercept_x": 189.61912556597025,
    "coef_y": [
        -0.505946641559293,
        0.0289523269904209
    ],
    "intercept_y": 508.06783211157216,
    "z_fija": -0.19
}

# Extraer coeficientes
a1, a2 = modelo["coef_x"]
b1, b2 = modelo["coef_y"]
intercept_x = modelo["intercept_x"]
intercept_y = modelo["intercept_y"]

# Coordenadas en píxeles
u, v = 142, 191

# Calcular posición en el espacio
x = a1 * u + a2 * v + intercept_x -20
y = b1 * u + b2 * v + intercept_y +25


# Mostrar resultados
print(f"x = {x:.6f} m")
print(f"y = {y:.6f} m")

