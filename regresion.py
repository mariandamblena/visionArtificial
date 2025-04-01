import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

# Cargar la imagen (se asume "1.png" en la carpeta "capturas")
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(directorio_actual, 'capturas', '1.png')
if not os.path.isfile(ruta_imagen):
    print(f'La imagen no se encontró en la ruta: {ruta_imagen}')
    exit()
image = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
if image is None:
    print("Error al cargar la imagen.")
    exit()

# Crear una imagen en color para visualizar y dibujar los puntos
display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

# Listas para almacenar los valores crudos e ingresados de temperatura
raw_values = []
temp_values = []

def click_event(event, x, y, flags, param):
    global display_image, raw_values, temp_values, image
    if event == cv2.EVENT_LBUTTONDOWN:
        # Obtener la intensidad en el punto clickeado
        intensity = image[y, x]
        print(f"Se hizo clic en ({x}, {y}), intensidad = {intensity}")
        # Solicitar al usuario la temperatura para ese punto
        temp_input = input("Ingrese la temperatura en °C para este punto: ")
        try:
            temp = float(temp_input)
        except ValueError:
            print("Valor de temperatura inválido, se omite este punto.")
            return
        raw_values.append(intensity)
        temp_values.append(temp)
        # Dibujar el punto y la etiqueta en la imagen de visualización
        cv2.circle(display_image, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(display_image, f"{temp:.1f}", (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imshow("Imagen", display_image)

# Configurar la ventana y asignar la función de callback
cv2.namedWindow("Imagen", cv2.WINDOW_NORMAL)
cv2.imshow("Imagen", display_image)
cv2.setMouseCallback("Imagen", click_event)

print("Seleccione puntos haciendo clic en la imagen e ingrese la temperatura correspondiente.")
print("Cuando haya terminado, presione Ctrl+C en la terminal para finalizar.")

# Esperar a que el usuario interrumpa con Ctrl+C
try:
    while True:
        cv2.waitKey(1)
except KeyboardInterrupt:
    print("Ctrl+C detectado, finalizando la captura de puntos.")
finally:
    cv2.destroyAllWindows()

# Verificar que se hayan seleccionado al menos dos puntos
if len(raw_values) < 2:
    print("No se han seleccionado suficientes puntos para la calibración.")
    exit()

raw_arr = np.array(raw_values)
temp_arr = np.array(temp_values)

# Realizar la regresión lineal: T(°C) = scale * raw + offset
coef = np.polyfit(raw_arr, temp_arr, 1)
scale_coef, offset_coef = coef

print("\nEcuación de calibración obtenida:")
print(f"T(°C) = {scale_coef:.4f} * raw + {offset_coef:.4f}")

# Visualizar los puntos y la línea de ajuste
plt.figure(figsize=(8, 6))
plt.scatter(raw_arr, temp_arr, label="Puntos de calibración", color="blue")
x_fit = np.linspace(raw_arr.min(), raw_arr.max(), 100)
y_fit = scale_coef * x_fit + offset_coef
plt.plot(x_fit, y_fit, 'r-', label="Ajuste lineal")
plt.xlabel("Valor crudo (raw)")
plt.ylabel("Temperatura (°C)")
plt.title("Calibración lineal")
plt.legend()
plt.grid(True)
plt.show()
