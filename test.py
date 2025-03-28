import cv2
import numpy as np
import os

# --- Configuración y carga de la imagen "1.png" ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(directorio_actual, 'capturas', '18.png')

if not os.path.isfile(ruta_imagen):
    print(f'La imagen no se encontró en la ruta: {ruta_imagen}')
    exit()

# Cargar la imagen térmica original en 16 bits
imagen_original_full = cv2.imread(ruta_imagen, cv2.IMREAD_UNCHANGED)
if imagen_original_full is None:
    print('Error al cargar la imagen.')
    exit()

# --- Dividir la imagen verticalmente en dos mitades (izquierda y derecha) ---
ancho_total = imagen_original_full.shape[1]
imagen_original_left = imagen_original_full[:, :ancho_total // 2]
imagen_original_right = imagen_original_full[:, ancho_total // 2:]

# --- Función para procesar una mitad ---
def procesar_mitad(imagen_original, lado='Izquierda'):
    # Normalizar para visualización (8 bits)
    imagen_visualizacion = cv2.normalize(imagen_original, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # Obtener imagen en escala de grises
    if len(imagen_visualizacion.shape) == 3 and imagen_visualizacion.shape[2] == 3:
        imagen_gris = cv2.cvtColor(imagen_visualizacion, cv2.COLOR_BGR2GRAY)
    else:
        imagen_gris = imagen_visualizacion.copy()

    # Preparar imagen para dibujar resultados (convertida a BGR)
    if len(imagen_visualizacion.shape) == 2 or imagen_visualizacion.shape[2] == 1:
        imagen_dibujo = cv2.cvtColor(imagen_visualizacion, cv2.COLOR_GRAY2BGR)
    else:
        imagen_dibujo = imagen_visualizacion.copy()

    # Preprocesamiento: desenfoque y umbralización (Otsu)
    imagen_suavizada = cv2.GaussianBlur(imagen_gris, (5, 5), 0)
    _, imagen_binaria = cv2.threshold(imagen_suavizada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Invertir la imagen binaria si el área blanca es muy pequeña
    area_blanca = cv2.countNonZero(imagen_binaria)
    area_total = imagen_binaria.shape[0] * imagen_binaria.shape[1]
    if area_blanca < 0.1 * area_total:
        imagen_binaria = cv2.bitwise_not(imagen_binaria)
    
    # Encontrar contornos en la imagen binaria
    contornos, _ = cv2.findContours(imagen_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_botellas = [cnt for cnt in contornos if cv2.contourArea(cnt) > 1000]
    if len(contornos_botellas) == 0:
        print(f"No se encontró ninguna botella en la mitad {lado}.")
        return None
    # Seleccionar el contorno de mayor área (se asume que es la botella)
    contorno_botella = max(contornos_botellas, key=cv2.contourArea)
    
    # Dibujar el contorno en verde
    cv2.drawContours(imagen_dibujo, [contorno_botella], -1, (0, 255, 0), 2)

    # Obtener la caja delimitadora del contorno
    x, y, w, h = cv2.boundingRect(contorno_botella)
    
    # Dividir el área interna del contorno en tres regiones horizontales.
    # Se asume que: 
    #  - La parte superior (valores de y menores) es "Pico y Cuello"
    #  - La parte central es "Cuerpo"
    #  - La parte inferior (valores de y mayores) es "Base"
    altura_region = h // 3
    regiones = {
        'Pico y Cuello': (y, y + altura_region),
        'Cuerpo': (y + altura_region, y + 2 * altura_region),
        'Base': (y + 2 * altura_region, y + h)
    }
    
    print(f"\nResultados para la botella en la mitad {lado}:")
    
    # Definir un kernel para erosionar la máscara y evitar valores extremos en los bordes
    kernel_erode = np.ones((5, 5), np.uint8)
    
    for nombre_region, (inicio, fin) in regiones.items():
        # Dibujar línea divisoria para visualizar (línea azul)
        cv2.line(imagen_dibujo, (x, fin), (x + w, fin), (255, 0, 0), 2)
        # Colocar etiqueta básica en el centro de la región
        pos_texto = (x + 5, inicio + (fin - inicio) // 2)
        cv2.putText(imagen_dibujo, nombre_region, pos_texto, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Crear una máscara que cubra el contorno de la botella
        mascara_botella = np.zeros(imagen_gris.shape, dtype=np.uint8)
        cv2.drawContours(mascara_botella, [contorno_botella], -1, 255, thickness=cv2.FILLED)
        # Limitar la máscara a la franja horizontal de la región
        mascara_botella[:inicio, :] = 0
        mascara_botella[fin:, :] = 0
        
        # Erosionar la máscara para evitar que los bordes introduzcan valores extremos
        mascara_region = cv2.erode(mascara_botella, kernel_erode, iterations=1)
        
        # Extraer los valores de la imagen original (16 bits) en la región
        valores_region = imagen_original[mascara_region == 255]
        
        if valores_region.size > 0:
            temp_promedio = np.mean(valores_region)
            temp_maxima = np.max(valores_region)
            temp_minima = np.min(valores_region)
            temp_mediana = np.median(valores_region)
            
            etiqueta_stats = f"Prom={temp_promedio:.1f} Max={temp_maxima:.1f} Min={temp_minima:.1f} Med={temp_mediana:.1f}"
            pos_stats = (x + 5, inicio + (fin - inicio) // 2 + 25)
            cv2.putText(imagen_dibujo, etiqueta_stats, pos_stats, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            print(f"\n  Región: {nombre_region}")
            print(f"    Temperatura promedio: {temp_promedio:.2f}")
            print(f"    Temperatura máxima:   {temp_maxima:.2f}")
            print(f"    Temperatura mínima:   {temp_minima:.2f}")
            print(f"    Temperatura mediana:  {temp_mediana:.2f}")
        else:
            print(f"\n  Región: {nombre_region} - No se encontraron datos.")
    
    return imagen_dibujo

# --- Procesar sólo la imagen 1.png ---
ruta_imagen = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capturas', '1.png')
imagen_original_full = cv2.imread(ruta_imagen, cv2.IMREAD_UNCHANGED)
if imagen_original_full is None:
    print("Error al cargar la imagen 1.png.")
    exit()

# Dividir la imagen en dos mitades verticales
ancho_total = imagen_original_full.shape[1]
imagen_original_left = imagen_original_full[:, :ancho_total // 2]
imagen_original_right = imagen_original_full[:, ancho_total // 2:]

print("\n--- Procesando la mitad Izquierda ---")
imagen_dibujo_left = procesar_mitad(imagen_original_left, lado='Izquierda')

print("\n--- Procesando la mitad Derecha ---")
imagen_dibujo_right = procesar_mitad(imagen_original_right, lado='Derecha')

if imagen_dibujo_left is None or imagen_dibujo_right is None:
    print("No se pudo procesar alguna de las mitades.")
    exit()

# Combinar horizontalmente ambas mitades
imagen_final = cv2.hconcat([imagen_dibujo_left, imagen_dibujo_right])

# Mostrar la imagen final con contornos, líneas divisorias y etiquetas con estadísticas
cv2.imshow('Imagen final con contornos y etiquetas', imagen_final)
cv2.waitKey(0)
cv2.destroyAllWindows()