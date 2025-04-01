# Calibración y Cálculo de Temperaturas en Imágenes Termográficas

Este repositorio contiene dos scripts en Python que te permiten trabajar con imágenes termográficas radiométricas:

1. **Script de Cálculo de Temperaturas**  
   Este script carga una imagen radiométrica (por ejemplo, `1.png` en la carpeta `capturas`), detecta la botella en la imagen y la segmenta en tres regiones (Pico y Cuello, Cuerpo y Base).  
   Para cada región, se extraen los valores crudos (de la imagen original en 16 bits) y se aplican los coeficientes de calibración predefinidos para convertir esos valores a temperatura en °C.  
   La ecuación de calibración utilizada es, por ejemplo:  
   \[
   T(°C) = 0.1639 \times \text{raw} + 14.9353
   \]
   El script imprime en consola únicamente los valores de temperatura (promedio y mediana) en °C para cada región y muestra la imagen con contornos y etiquetas.

2. **Script de Regresión Lineal para Calibración**  
   Este script interactivo te permite abrir una imagen (en escala de grises) y seleccionar puntos de calibración haciendo clic en ella.  
   Por cada clic, se te solicita que ingreses la temperatura real (en °C) para ese punto.  
   Se almacenan los valores crudos (intensidad del píxel) y las temperaturas ingresadas, y una vez finalizada la captura (por ejemplo, presionando Ctrl+C o 'q'), se calcula la ecuación de calibración mediante regresión lineal.  
   La ecuación obtenida tiene la forma:
   \[
   T(°C) = \text{scale} \times \text{raw} + \text{offset}
   \]
   y se muestra junto con un gráfico de dispersión con la línea de ajuste, para que puedas validar el modelo.

## Requisitos

- Python 3.x
- [OpenCV](https://opencv.org/) (`opencv-python`)
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/) (solo para el script de regresión, si se usa CSV)
- [Matplotlib](https://matplotlib.org/)

## Instalación

Puedes instalar las dependencias necesarias utilizando `pip`:

```bash
pip install opencv-python numpy matplotlib pandas
Uso
1. Cálculo de Temperaturas
Coloca la imagen radiométrica 1.png en la carpeta capturas y ejecuta el script:

bash
Copiar
python temperature_calculation.py
El script realizará los siguientes pasos:

Cargará la imagen en 16 bits.

Normalizará la imagen a 8 bits para segmentación.

Detectará la botella (seleccionando el contorno de mayor área).

Dividirá la botella en tres regiones horizontales (Pico y Cuello, Cuerpo y Base).

Calculará la temperatura promedio y mediana en cada región usando la ecuación:

𝑇
(
°
𝐶
)
=
0.1639
×
raw
+
14.9353
T(°C)=0.1639×raw+14.9353
Imprimirá los valores en °C y mostrará la imagen con las etiquetas.

2. Calibración mediante Regresión Lineal
Este script te permite seleccionar puntos en la imagen y asociar manualmente la temperatura real a cada uno para obtener la ecuación de calibración. Ejecuta el script:

bash
Copiar
python calibration_interactive.py
Pasos del script:

Se abre la imagen en una ventana (en escala de grises convertida a BGR para visualización).

Con cada clic en la imagen se extrae el valor crudo del píxel y se solicita que ingreses la temperatura en °C.

Los puntos seleccionados se almacenan.

Cuando termines (por ejemplo, presionando Ctrl+C o 'q', según la implementación), el script calcula la regresión lineal de la forma:

𝑇
(
°
𝐶
)
=
scale
×
raw
+
offset
T(°C)=scale×raw+offset
Se imprime la ecuación y se muestra un gráfico con los puntos y la línea de ajuste.

Notas
Calibración:
La ecuación de calibración usada en el primer script es un ejemplo predefinido. Se recomienda usar el segundo script para obtener la ecuación de calibración óptima basada en tus puntos de referencia.

Datos Radiométricos:
Es fundamental que la imagen utilizada contenga los datos crudos radiométricos (por ejemplo, en formato de 16 bits) para que la conversión a temperatura sea válida. Si la imagen ha sido procesada o colorizada, los valores extraídos no representarán las temperaturas reales.

Archivos
temperature_calculation.py: Script para procesar la imagen y calcular las temperaturas en diferentes regiones.

calibration_interactive.py: Script interactivo para seleccionar puntos de calibración y obtener la ecuación de regresión lineal.

Licencia
Este proyecto es de código abierto y se distribuye bajo la Licencia MIT.