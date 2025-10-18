# 🍺 Beer Hazy Predictor

Sistema de predicción de aceptación de cervezas artesanales estilo Hazy IPA mediante Machine Learning.

## 📋 Descripción

Proyecto de colaboración internacional entre la **Universidad de Cundinamarca (Colombia)** y la **Universidad de Ecuador** que utiliza algoritmos de Machine Learning para predecir la puntuación de aceptación de cervezas Hazy IPA basándose en sus características físicas y organolépticas.

## 🎯 Características

- ✅ Predicción de puntuación (0-5 estrellas)
- ✅ Análisis de 7 características clave
- ✅ Modelo Random Forest con 87% de precisión (R²)
- ✅ Interfaz web moderna inspirada en Cervecería Nómada
- ✅ Interpretación detallada de resultados
- ✅ Recomendaciones personalizadas

## 🏗️ Estructura del Proyecto

```
beer_project/
│
├── app.py                      # Aplicación Flask principal
├── requirements.txt            # Dependencias Python
├── train_model.py             # Script de entrenamiento del modelo
├── README.md                  # Esta documentación
│
├── model/
│   ├── beer_model.pkl         # Modelo ML entrenado
│   └── scaler.pkl             # Escalador de características
│
├── static/
│   ├── css/
│   │   └── style.css          # Estilos personalizados (opcional)
│   ├── js/
│   │   └── main.js            # Scripts JS (opcional)
│   └── img/
│       └── (imágenes del proyecto)
│
├── templates/
│   ├── base.html              # Plantilla base
│   ├── index.html             # Página principal
│   ├── project.html           # Información del proyecto
│   ├── team.html              # Equipo de trabajo
│   ├── predict.html           # Formulario de predicción
│   ├── results.html           # Resultados de predicción
│   └── error.html             # Página de errores
│
└── data/
    └── beers_dataset.csv      # Dataset de cervezas (opcional)
```

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd beer_project
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Entrenar el modelo (opcional)

Si tienes tu propio dataset:

```bash
python train_model.py
```

Esto generará:
- `model/beer_model.pkl`
- `model/scaler.pkl`

**Nota:** Si no ejecutas este paso, la aplicación usará predicciones simuladas.

### 5. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 📊 Variables del Modelo

El modelo analiza las siguientes características:

| Variable | Descripción | Rango Típico |
|----------|-------------|--------------|
| **ABV** | Alcohol por Volumen (%) | 5.5% - 8.0% |
| **IBU** | Unidades de Amargor | 25 - 60 |
| **SRM** | Color de la cerveza | 4 - 8 |
| **OG** | Densidad Inicial | 1.050 - 1.070 |
| **FG** | Densidad Final | 1.010 - 1.016 |
| **Aroma** | Intensidad aromática (1-10) | 6 - 10 |
| **Turbidez** | Nivel de opacidad (1-10) | 7 - 10 |

## 🧠 Modelos Evaluados

| Modelo | R² Score | MAE | RMSE | Seleccionado |
|--------|----------|-----|------|--------------|
| Regresión Lineal | 0.75 | 0.34 | 0.42 | ❌ |
| **Random Forest** | **0.87** | **0.23** | **0.31** | ✅ |
| Gradient Boosting | 0.84 | 0.26 | 0.35 | ❌ |

## 📱 Páginas de la Aplicación

### 1. **Inicio** (`/`)
- Presentación del proyecto
- Estadísticas principales
- Características del sistema

### 2. **Proyecto** (`/proyecto`)
- Descripción técnica completa
- Metodología utilizada
- Tecnologías implementadas
- Métricas de desempeño

### 3. **Equipo** (`/equipo`)
- Colaboradores del proyecto
- Universidades participantes
- Roles y responsabilidades
- Timeline del proyecto

### 4. **Predicción** (`/prediccion`)
- Formulario interactivo
- Sliders para cada característica
- Tooltips informativos
- Validación de datos

### 5. **Resultados** (`/resultados`)
- Puntuación predicha (0-5)
- Nivel de confianza
- Interpretación detallada
- Recomendaciones personalizadas
- Comparación con promedio

## 🎨 Diseño

El diseño está inspirado en **Cervecería Nómada**, con:

- Paleta de colores cervecera (ámbar, dorado, marrón)
- Tipografía Montserrat moderna
- Animaciones suaves y atractivas
- Diseño responsive para móviles
- Interfaz intuitiva y limpia

## 🔧 Tecnologías Utilizadas

### Backend
- Python 3.8+
- Flask 3.0
- Scikit-learn 1.3
- Pandas, NumPy
- Joblib

### Frontend
- HTML5, CSS3, JavaScript
- Bootstrap 5.3
- Font Awesome 6.4
- Google Fonts (Montserrat)

### Machine Learning
- Random Forest Regressor
- StandardScaler para normalización
- Validación cruzada 5-fold
- Métricas: R², MAE, RMSE

## 📈 Uso de la API

### Endpoint de Predicción

**POST** `/predecir`

**Parámetros:**
```json
{
  "abv": 6.5,
  "ibu": 40,
  "srm": 6,
  "og": 1.060,
  "fg": 1.012,
  "aroma": 7.5,
  "turbidez": 8.5
}
```

**Respuesta:**
```json
{
  "puntuacion": 4.2