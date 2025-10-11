import pandas as pd
import matplotlib.pyplot as mp
import numpy as np
from sklearn.linear_model import LinearRegression
import io
import base64

# Datos ficticios de ejemplo
data = {
    "Número de Autos": [200, 0, 100, 300, 50, 400, 120, 500, 80, 150, 220, 600, 90, 700, 40, 450, 110, 800, 70, 900],
    "Uso Transporte Público (%)": [20, 80, 60, 10, 70, 5, 65, 15, 55, 75, 40, 8, 85, 3, 90, 25, 50, 2, 95, 1],
    "Nivel Contaminación (µg/m³)": [70, 20, 40, 85, 35, 95, 50, 110, 45, 30, 65, 120, 25, 130, 22, 100, 55, 140, 20, 150]
}

df = pd.DataFrame(data)

# Variables independientes (X) y dependiente (Y)
x = df[["Número de Autos", "Uso Transporte Público (%)"]]
y = df[["Nivel Contaminación (µg/m³)"]]

x1 = df["Número de Autos"]
x2 = df["Uso Transporte Público (%)"]

# Crear y entrenar el modelo
model = LinearRegression()
model.fit(x, y)

# Función para predecir nivel de contaminación
def PredecirContaminacion(autos, uso_transporte):
    result = model.predict([[autos, uso_transporte]])[0]
    return result

# Función para graficar
def PlotGraph():
    img = io.BytesIO()
    
    # Crear figura 3D
    fig = mp.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Puntos de datos reales
    ax.scatter(x1, x2, y, c='blue', marker='o', label='Datos reales')
    
    # Crear malla para el plano de regresión
    x1_surf, x2_surf = np.meshgrid(x1, x2)
    y_predict = model.predict(np.c_[x1_surf.ravel(), x2_surf.ravel()])
    y_predict = y_predict.reshape(x1_surf.shape)
    
    # Plano de regresión
    ax.plot_surface(x1_surf, x2_surf, y_predict, color='red', alpha=0.5)
    
    # Etiquetas
    ax.set_title('Regresión Lineal Múltiple: Contaminación')
    ax.set_xlabel('Número de Autos')
    ax.set_ylabel('Uso Transporte Público (%)')
    ax.set_zlabel('Nivel Contaminación (µg/m³)')
    
    mp.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url
