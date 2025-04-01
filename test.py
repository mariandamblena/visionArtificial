import cv2
import numpy as np
import os

# --- Configuración y carga de la imagen "1.png" ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(directorio_actual, 'capturas', '1.png')

if not os.path.isfile(ruta_imagen):
    print(f'La imagen no se encontró en la ruta: {ruta_imagen}')
    exit()

# Cargar la imagen térmica original en 16 bits (se espera que contenga los datos radiométricos crudos)
imagen_original_full = cv2.imread(ruta_imagen, cv2.IMREAD_UNCHANGED)
if imagen_original_full is None:
    print('Error al cargar la imagen.')
    exit()

def procesar_imagen(imagen_original):
    """
    Detecta una sola botella en la imagen, la segmenta y calcula la temperatura
    (promedio y mediana en °C) en tres regiones: "Pico y Cuello", "Cuerpo" y "Base".
    
    La segmentación se realiza sobre una versión normalizada a 8 bits para encontrar
    contornos, pero el análisis se efectúa sobre la imagen original en 16 bits aplicando:
    
        T(°C) = 0.1639 * raw + 14.9353
    """
    # Normalizar para segmentación y visualización (8 bits)
    imagen_seg = cv2.normalize(imagen_original, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # Convertir a escala de grises para segmentación
    if len(imagen_seg.shape) == 3 and imagen_seg.shape[2] == 3:
        imagen_gris = cv2.cvtColor(imagen_seg, cv2.COLOR_BGR2GRAY)
    else:
        imagen_gris = imagen_seg.copy()
    
    # Preparar imagen para dibujar resultados (convertida a BGR)
    if len(imagen_seg.shape) == 2 or imagen_seg.shape[2] == 1:
        imagen_dibujo = cv2.cvtColor(imagen_seg, cv2.COLOR_GRAY2BGR)
    else:
        imagen_dibujo = imagen_seg.copy()
    
    # Preprocesamiento: desenfoque y umbralización (Otsu) sobre la imagen de segmentación (8 bits)
    imagen_suavizada = cv2.GaussianBlur(imagen_gris, (5, 5), 0)
    _, imagen_binaria = cv2.threshold(imagen_suavizada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Invertir la imagen binaria si el área blanca es muy pequeña
    area_blanca = cv2.countNonZero(imagen_binaria)
    area_total_bin = imagen_binaria.shape[0] * imagen_binaria.shape[1]
    if area_blanca < 0.1 * area_total_bin:
        imagen_binaria = cv2.bitwise_not(imagen_binaria)
    
    # Encontrar contornos en la imagen binaria (8 bits)
    contornos, _ = cv2.findContours(imagen_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_botellas = [cnt for cnt in contornos if cv2.contourArea(cnt) > 1000]
    if not contornos_botellas:
        print("No se encontró ninguna botella en la imagen completa.")
        return None
    
    # Seleccionar el contorno de mayor área (se asume que es la botella)
    contorno_botella = max(contornos_botellas, key=cv2.contourArea)
    cv2.drawContours(imagen_dibujo, [contorno_botella], -1, (0, 255, 0), 2)
    
    # Obtener la caja delimitadora del contorno
    x, y, w, h = cv2.boundingRect(contorno_botella)
    
    # Dividir el área interna del contorno en tres regiones horizontales:
    # "Pico y Cuello": zona superior (valores de y menores)
    # "Cuerpo": zona central
    # "Base": zona inferior (valores de y mayores)
    altura_region = h // 3
    regiones = {
        'Pico y Cuello': (y, y + altura_region),
        'Cuerpo': (y + altura_region, y + 2 * altura_region),
        'Base': (y + 2 * altura_region, y + h)
    }
    
    print("\nResultados para la botella detectada:")
    
    # Coeficientes de calibración:
    # T(°C) = 0.1639 * raw + 14.9353
    scale = 0.1639
    offset = 14.9353

    kernel_erode = np.ones((8, 8), np.uint8)
    
    for nombre_region, (inicio, fin) in regiones.items():
        cv2.line(imagen_dibujo, (x, fin), (x + w, fin), (255, 0, 0), 2)
        pos_texto = (x + 5, inicio + (fin - inicio) // 2)
        cv2.putText(imagen_dibujo, nombre_region, pos_texto, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        mascara_botella = np.zeros(imagen_gris.shape, dtype=np.uint8)
        cv2.drawContours(mascara_botella, [contorno_botella], -1, 255, thickness=cv2.FILLED)
        mascara_botella[:inicio, :] = 0
        mascara_botella[fin:, :] = 0
        
        mascara_region = cv2.erode(mascara_botella, kernel_erode, iterations=1)
        valores_region = imagen_original[mascara_region == 255]
        
        if valores_region.size > 0:
            # Calcular la temperatura promedio y mediana usando la fórmula de calibración
            temp_promedio = scale * np.mean(valores_region) + offset
            temp_mediana = scale * np.median(valores_region) + offset
            
            etiqueta_stats = f"Prom={temp_promedio:.1f}°C Med={temp_mediana:.1f}°C"
            pos_stats = (x + 5, inicio + (fin - inicio) // 2 + 25)
            cv2.putText(imagen_dibujo, etiqueta_stats, pos_stats, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            print(f"\n  Región: {nombre_region}")
            print(f"    Temperatura promedio: {temp_promedio:.2f} °C")
            print(f"    Temperatura mediana:  {temp_mediana:.2f} °C")
        else:
            print(f"\n  Región: {nombre_region} - No se encontraron datos.")
    
    return imagen_dibujo

# Procesar la imagen completa (una sola botella)
imagen_dibujo = procesar_imagen(imagen_original_full)
if imagen_dibujo is None:
    print("No se pudo procesar la botella en la imagen.")
    exit()

# Mostrar la imagen final con contornos, líneas divisorias y etiquetas con las temperaturas
cv2.namedWindow('Imagen final', cv2.WINDOW_NORMAL)
cv2.imshow('Imagen final', imagen_dibujo)
cv2.resizeWindow('Imagen final', 1200, 1200)  # Ajusta la resolución según sea necesario
cv2.waitKey(0)
cv2.destroyAllWindows()
