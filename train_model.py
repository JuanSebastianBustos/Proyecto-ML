"""
Script para entrenar el modelo de predicción de cervezas Hazy IPA
Este script crea un modelo de ejemplo. Debes reemplazarlo con tu dataset real.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os

# Crear directorio para el modelo si no existe
os.makedirs('model', exist_ok=True)

# ====================================
# 1. GENERAR DATASET DE EJEMPLO
# ====================================
# NOTA: Reemplaza esto con tu dataset real de cervezas

def generate_sample_data(n_samples=500):
    """
    Genera datos sintéticos para demostración.
    En producción, carga tu dataset real desde CSV o base de datos.
    """
    np.random.seed(42)
    
    # Características típicas de Hazy IPA
    data = {
        'ABV': np.random.uniform(5.5, 8.5, n_samples),
        'IBU': np.random.uniform(25, 70, n_samples),
        'SRM': np.random.uniform(4, 10, n_samples),
        'OG': np.random.uniform(1.050, 1.075, n_samples),
        'FG': np.random.uniform(1.010, 1.018, n_samples),
        'Aroma': np.random.uniform(5, 10, n_samples),
        'Turbidez': np.random.uniform(6, 10, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Crear puntuación basada en características
    # Esta fórmula simula preferencias: más aroma y turbidez = mejor puntuación
    df['Puntuacion'] = (
        2.0 +  # Base
        (df['Aroma'] - 5) * 0.2 +  # Aroma fuerte mejora
        (df['Turbidez'] - 5) * 0.15 +  # Turbidez alta mejora
        (df['ABV'] - 6) * 0.1 +  # ABV moderado-alto es mejor
        -abs(df['IBU'] - 45) * 0.01 +  # IBU óptimo alrededor de 45
        np.random.normal(0, 0.3, n_samples)  # Ruido aleatorio
    )
    
    # Limitar puntuación entre 0 y 5
    df['Puntuacion'] = df['Puntuacion'].clip(0, 5)
    
    return df

# ====================================
# 2. CARGAR O GENERAR DATOS
# ====================================
print("=" * 50)
print("ENTRENAMIENTO DE MODELO - BEER HAZY PREDICTOR")
print("=" * 50)

# Intenta cargar dataset real, si no existe, genera uno de ejemplo
try:
    df = pd.read_csv('data/beers_dataset.csv')
    print(f"\n✓ Dataset cargado: {len(df)} registros")
except FileNotFoundError:
    print("\n⚠ Dataset no encontrado. Generando datos de ejemplo...")
    df = generate_sample_data(500)
    print(f"✓ Dataset generado: {len(df)} registros")

print(f"\nColumnas: {list(df.columns)}")
print(f"\nPrimeras filas:")
print(df.head())

# ====================================
# 3. PREPROCESAMIENTO
# ====================================
print("\n" + "=" * 50)
print("PREPROCESAMIENTO DE DATOS")
print("=" * 50)

# Separar características y objetivo
feature_columns = ['ABV', 'IBU', 'SRM', 'OG', 'FG', 'Aroma', 'Turbidez']
X = df[feature_columns]
y = df['Puntuacion']

print(f"\nCaracterísticas (X): {X.shape}")
print(f"Objetivo (y): {y.shape}")

# Estadísticas descriptivas
print(f"\nEstadísticas del objetivo:")
print(f"  Media: {y.mean():.2f}")
print(f"  Desv. Est: {y.std():.2f}")
print(f"  Min: {y.min():.2f}")
print(f"  Max: {y.max():.2f}")

# ====================================
# 4. DIVISIÓN TRAIN/TEST
# ====================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nConjunto de entrenamiento: {X_train.shape[0]} muestras")
print(f"Conjunto de prueba: {X_test.shape[0]} muestras")

# ====================================
# 5. NORMALIZACIÓN
# ====================================
print("\n" + "=" * 50)
print("NORMALIZACIÓN")
print("=" * 50)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("✓ Datos normalizados con StandardScaler")

# ====================================
# 6. ENTRENAMIENTO DEL MODELO
# ====================================
print("\n" + "=" * 50)
print("ENTRENAMIENTO DEL MODELO")
print("=" * 50)

# Random Forest Regressor (mejor desempeño según proyecto)
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

print("\nEntrenando Random Forest Regressor...")
model.fit(X_train_scaled, y_train)
print("✓ Modelo entrenado")

# ====================================
# 7. EVALUACIÓN
# ====================================
print("\n" + "=" * 50)
print("EVALUACIÓN DEL MODELO")
print("=" * 50)

# Predicciones
y_train_pred = model.predict(X_train_scaled)
y_test_pred = model.predict(X_test_scaled)

# Métricas en conjunto de entrenamiento
train_r2 = r2_score(y_train, y_train_pred)
train_mae = mean_absolute_error(y_train, y_train_pred)
train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))

# Métricas en conjunto de prueba
test_r2 = r2_score(y_test, y_test_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

print("\nMétricas en ENTRENAMIENTO:")
print(f"  R² Score: {train_r2:.4f}")
print(f"  MAE: {train_mae:.4f}")
print(f"  RMSE: {train_rmse:.4f}")

print("\nMétricas en PRUEBA:")
print(f"  R² Score: {test_r2:.4f}")
print(f"  MAE: {test_mae:.4f}")
print(f"  RMSE: {test_rmse:.4f}")

# Validación cruzada
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, 
                            scoring='r2', n_jobs=-1)
print(f"\nValidación Cruzada (5-fold):")
print(f"  R² promedio: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

# Importancia de características
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nImportancia de Características:")
for idx, row in feature_importance.iterrows():
    print(f"  {row['feature']}: {row['importance']:.4f}")

# ====================================
# 8. GUARDAR MODELO
# ====================================
print("\n" + "=" * 50)
print("GUARDANDO MODELO")
print("=" * 50)

joblib.dump(model, 'model/beer_model.pkl')
joblib.dump(scaler, 'model/scaler.pkl')

print("✓ Modelo guardado en: model/beer_model.pkl")
print("✓ Scaler guardado en: model/scaler.pkl")

# ====================================
# 9. PRUEBA DE PREDICCIÓN
# ====================================
print("\n" + "=" * 50)
print("PRUEBA DE PREDICCIÓN")
print("=" * 50)

# Ejemplo de cerveza Hazy IPA típica
sample_beer = np.array([[6.5, 40, 6, 1.060, 1.012, 7.5, 8.5]])
sample_scaled = scaler.transform(sample_beer)
prediction = model.predict(sample_scaled)[0]

print("\nEjemplo de Hazy IPA:")
print(f"  ABV: 6.5%")
print(f"  IBU: 40")
print(f"  SRM: 6")
print(f"  OG: 1.060")
print(f"  FG: 1.012")
print(f"  Aroma: 7.5/10")
print(f"  Turbidez: 8.5/10")
print(f"\n  → Predicción: {prediction:.2f}/5.0 estrellas")

print("\n" + "=" * 50)
print("ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
print("=" * 50)