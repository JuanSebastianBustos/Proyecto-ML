"""
Modelo ML para predecir calidad de cerveza artesanal de cacao (CHOCOBREW)
Adaptado para dataset beers.csv de Kaggle
Autor: Juan Sebastián Bustos Ruiz
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os

# ==============================
# CONFIGURACIÓN INICIAL
# ==============================
os.makedirs('model', exist_ok=True)
print("=" * 70)
print("ENTRENAMIENTO MODELO ML - CHOCOBREW (Adaptado a beers.csv)")
print("=" * 70)

# ==============================
# 1️⃣ CARGA DE DATOS
# ==============================
# Ruta actualizada según tu estructura de carpetas
file_path = "Datasets/beers.csv"
df = pd.read_csv(file_path)

# Limpieza de nombres de columnas por si hay caracteres ocultos
df.columns = df.columns.str.strip().str.lower()

print(f"\n📊 Dataset cargado desde: {file_path}")
print(f"📋 Total filas: {df.shape[0]} | Columnas: {list(df.columns)}")

# ==============================
# 2️⃣ LIMPIEZA Y VARIABLES ÚTILES
# ==============================
# Eliminamos filas sin datos críticos
df = df.dropna(subset=['abv', 'ibu'])
df = df[df['ibu'] > 0]

# ==============================
# 3️⃣ CREACIÓN DE VARIABLES SINTÉTICAS
# ==============================
np.random.seed(42)

# SRM (color) — simulación basada en estilos de cerveza
df["SRM"] = np.clip(np.random.normal(22, 4, len(df)), 10, 35)

# OG y FG — densidades
df["OG"] = np.round(np.random.uniform(1.050, 1.075, len(df)), 3)
df["FG"] = np.round(df["OG"] - np.random.uniform(0.010, 0.020, len(df)), 3)

# Porcentaje de Cacao — variable sintética clave
df["Porcentaje_Cacao"] = np.clip(np.random.beta(5, 2, len(df)) * 13 + 2, 2, 15)

# Fermentación y maduración
df["Dias_Fermentacion"] = np.random.randint(5, 12, len(df))
df["Dias_Maduracion"] = np.random.randint(8, 18, len(df))

# ==============================
# 4️⃣ VARIABLE OBJETIVO (PUNTUACIÓN)
# ==============================
df["Puntuacion"] = (
    2.2 +
    (df["Porcentaje_Cacao"] - 5) * 0.20 +
    (df["abv"] * 100 - 6) * 0.10 +
    -abs(df["ibu"] - 35) * 0.012 +
    (df["Dias_Maduracion"] - 8) * 0.08 +
    (df["Dias_Fermentacion"] - 5) * 0.05 +
    -abs(df["SRM"] - 22) * 0.03 +
    np.random.normal(0, 0.35, len(df))
)
df["Puntuacion"] = np.clip(df["Puntuacion"], 0, 5)

# ==============================
# 5️⃣ SELECCIÓN DE VARIABLES
# ==============================
feature_columns = [
    "abv", "ibu", "SRM", "OG", "FG",
    "Porcentaje_Cacao", "Dias_Fermentacion", "Dias_Maduracion"
]
X = df[feature_columns]
y = df["Puntuacion"]

# ==============================
# 6️⃣ DIVISIÓN DE DATOS
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Normalización
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==============================
# 7️⃣ ENTRENAMIENTO DEL MODELO
# ==============================
print("\n🧠 Entrenando modelo Random Forest...")
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=14,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_scaled, y_train)
print("✓ Modelo entrenado con éxito")

# ==============================
# 8️⃣ EVALUACIÓN
# ==============================
y_pred = model.predict(X_test_scaled)

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n📊 RESULTADOS DE EVALUACIÓN:")
print(f"  R² Score: {r2:.3f}")
print(f"  MAE: {mae:.3f}")
print(f"  RMSE: {rmse:.3f}")

# Validación cruzada
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2', n_jobs=-1)
print(f"\n🔄 Validación cruzada (5-fold): R² promedio = {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

# ==============================
# 9️⃣ IMPORTANCIA DE VARIABLES
# ==============================
feature_importance = pd.DataFrame({
    'Feature': feature_columns,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)
print("\n⭐ IMPORTANCIA DE VARIABLES:")
print(feature_importance)

# ==============================
# 🔟 GUARDAR MODELO
# ==============================
joblib.dump(model, 'model/beer_model.pkl')
joblib.dump(scaler, 'model/scaler.pkl')
print("\n💾 Modelo y scaler guardados correctamente en la carpeta 'model/'")

# ==============================
# 🔍 OPCIONAL: VISUALIZAR RESULTADOS
# ==============================
import matplotlib.pyplot as plt

plt.scatter(y_test, y_pred, alpha=0.6)
plt.xlabel("Puntuación Real")
plt.ylabel("Puntuación Predicha")
plt.title("Comparación Real vs Predicho - CHOCOBREW Adaptado")
plt.grid(True)
plt.show()
