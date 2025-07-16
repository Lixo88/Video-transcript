import numpy as np
import matplotlib.pyplot as plt

"""
Inequality Plot Script

Este script genera una gráfica comparativa entre una función exponencial
F(año) = coef_inicial * (tasa_base)**(año - 1) y una función lineal
C(año) = ordenada_origen + pendiente * (año - 1),
asegurando que las condiciones iniciales (año 1) sean (1, coef_inicial) y (1, ordenada_origen).

También detecta y anota el primer punto de cruce donde F(año) supera a C(año).

Parámetros configurables:
- tasa_base (float): base de la exponencial.
- coef_inicial (float): población de Franklin en año 1.
- pendiente (float): crecimiento fijo de Chester por año.
- ordenada_origen (float): población de Chester en año 1.
- año_min, año_max (int): rango de años a evaluar (enteros).
- resolucion (int): número de puntos para interpolación continua.

Uso:
    Ejecutar el script en un entorno con NumPy y Matplotlib.

Salida:
    - Ventana gráfica con ambas curvas y el punto de cruce marcado.
    - Mensaje en consola con el valor continuo de t_cruce y su valor poblacional.
"""
# 1. Parámetros de la función exponencial
tasa_base = 3                # crecimiento 5% anual
coef_inicial = 2           # Franklin, año 1

# 2. Parámetros de la función lineal
pendiente = 11                # incremento fijo anual de Chester
ordenada_origen = 5        # Chester, año 1

# 3. Dominio de años (año 1 hasta año 15)
año_min, año_max = 1, 15        # evaluar de año 1 a 15
resolucion = 10000             # resolución de la interpolación

# 4. Generar array de años con inicio en 1
años = np.linspace(año_min, año_max, resolucion)

# 5. Calcular valores ajustados al desplazamiento (año-1)
y_exp = coef_inicial * tasa_base ** (años - 1)
y_lin = ordenada_origen + pendiente * (años - 1)

# 6. Calcular diferencia
diff = y_exp - y_lin

# 7. Encontrar punto de cruce continuo
t_cruce = None
y_cruce = None
for i in range(resolucion - 1):
    if diff[i] <= 0 < diff[i+1]:
        t0, t1 = años[i], años[i+1]
        d0, d1 = diff[i], diff[i+1]
        # interpolación lineal para aproximar t_cruce
        t_cruce = t0 + (0 - d0) * (t1 - t0) / (d1 - d0)
        y_cruce = coef_inicial * tasa_base ** (t_cruce - 1)
        break

# 8. Graficar con Matplotlib
plt.figure(figsize=(8,6))
plt.plot(años, y_exp, label='Franklin: F(año)')
plt.plot(años, y_lin, label='Chester: C(año)')
if t_cruce is not None:
    plt.plot(t_cruce, y_cruce, 'ro', label=f'Cruce ≈ año {t_cruce:.2f}')
plt.xlabel('Año')
plt.ylabel('Población')
plt.title('Crecimiento exponencial vs lineal')
plt.legend()
plt.grid(True)
plt.show()

# 9. Mostrar resultado en consola
if t_cruce is not None:
    print(f"Primer cruce continuo en año ≈ {t_cruce:.4f}, población ≈ {y_cruce:.2f}")
else:
    print("No se detectó cruce en el rango dado.")