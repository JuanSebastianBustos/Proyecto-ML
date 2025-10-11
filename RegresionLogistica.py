import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import base64
from io import BytesIO

# Cargar el conjunto de datos
data = pd.read_csv('Datasets/data.csv')

# Explorar los datos
print(data.head())
print(data.info())
print(data.describe())

# Separar la variable dependiente y las independientes
x = data.drop('Aprueba', axis=1)  
y = data['Aprueba']  

# Dividir el dataset en conjunto de entrenamiento y prueba
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

# Estandarizar los datos 
scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)

# Crear el modelo de Regresión Logística
logistic_model = LogisticRegression()

# Entrenar el modelo
logistic_model.fit(x_train_scaled, y_train)

# Realizar predicciones al conjunto de prueba
y_pred = logistic_model.predict(x_test_scaled)

def evaluate():
    """Evalúa el modelo y retorna métricas"""
    # Calcular exactitud
    accuracy = accuracy_score(y_test, y_pred)
    
    # Generar reporte de clasificación
    report = classification_report(y_test, y_pred, output_dict=True)
    
    # Crear matriz de confusión
    plt.figure(figsize=(8,6))
    conf_matrix = confusion_matrix(y_test, y_pred)
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.xlabel('Predicción')
    plt.ylabel('Actual')
    plt.title('Matriz de Confusión')

    # Convertir matriz de confusión a imagen base64
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    matriz_url = base64.b64encode(img_buffer.getvalue()).decode('utf8')
    
    return accuracy, report, matriz_url

def predict_label(features, threshold=0.5):
    """Predice la etiqueta para nuevas características"""
    # Estandarizar las características
    features_scaled = scaler.transform([features])
    
    # Predecir probabilidades
    probabilities = logistic_model.predict_proba(features_scaled)[0]
    
    # Determinar predicción basada en el threshold
    prediction = "Sí" if probabilities[1] >= threshold else "No"
    
    return prediction, probabilities[1]
