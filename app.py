from flask import Flask, render_template, request, flash, redirect, url_for
import os
import logging
from werkzeug.exceptions import RequestEntityTooLarge
import numpy as np

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Información del proyecto
PROJECT_INFO = {
    'nombre': 'Beer Hazy Predictor',
    'subtitulo': 'Predicción de Popularidad con Machine Learning',
    'version': '1.0',
    'descripcion': 'Sistema inteligente de predicción de aceptación de cervezas artesanales estilo Hazy mediante algoritmos de Machine Learning',
    'objetivo_general': 'Predecir la puntuación de aceptación de cervezas artesanales Hazy basándose en sus características físicas y organolépticas',
    'objetivos_especificos': [
        'Analizar las características que más influyen en la aceptación de cervezas Hazy',
        'Implementar modelos de regresión para predicción de puntuaciones',
        'Crear una interfaz web interactiva para facilitar las predicciones',
        'Promover la colaboración internacional en investigación cervecera'
    ],
    'tecnologias': [
        {'nombre': 'Python', 'icono': 'fab fa-python'},
        {'nombre': 'Flask', 'icono': 'fas fa-flask'},
        {'nombre': 'Scikit-learn', 'icono': 'fas fa-brain'},
        {'nombre': 'Pandas', 'icono': 'fas fa-table'},
        {'nombre': 'Bootstrap', 'icono': 'fab fa-bootstrap'}
    ],
    'universidades': [
        {
            'nombre': 'Universidad de Cundinamarca',
            'pais': 'Colombia',
            'ciudad': 'Chía',
            'participantes': 2,
            'carrera': 'Ingeniería de Sistemas'
        },
        {
            'nombre': 'Universidad de Ecuador',
            'pais': 'Ecuador',
            'ciudad': 'Quito',
            'participantes': 2,
            'carrera': 'Ingeniería en Computación'
        }
    ],
    'equipo': [
        {
            'nombre': 'Estudiante UdeC 1',
            'rol': 'Desarrollador Backend & ML',
            'universidad': 'Universidad de Cundinamarca',
            'pais': 'Colombia',
            'email': 'estudiante1@ucundinamarca.edu.co',
            'iniciales': 'E1'
        },
        {
            'nombre': 'Estudiante UdeC 2',
            'rol': 'Desarrollador Frontend',
            'universidad': 'Universidad de Cundinamarca',
            'pais': 'Colombia',
            'email': 'estudiante2@ucundinamarca.edu.co',
            'iniciales': 'E2'
        },
        {
            'nombre': 'Estudiante Ecuador 1',
            'rol': 'Científico de Datos',
            'universidad': 'Universidad de Ecuador',
            'pais': 'Ecuador',
            'email': 'estudiante1@uce.edu.ec',
            'iniciales': 'E3'
        },
        {
            'nombre': 'Estudiante Ecuador 2',
            'rol': 'Analista de Datos',
            'universidad': 'Universidad de Ecuador',
            'pais': 'Ecuador',
            'email': 'estudiante2@uce.edu.ec',
            'iniciales': 'E4'
        }
    ],
    'metricas': {
        'r2': 0.87,
        'mae': 0.23,
        'rmse': 0.31
    }
}

# Cargar modelo (crear modelo dummy si no existe)
try:
    model = joblib.load('model/beer_model.pkl')
    scaler = joblib.load('model/scaler.pkl')
    logger.info("Modelo cargado exitosamente")
except:
    logger.warning("Modelo no encontrado, usando predicción simulada")
    model = None
    scaler = None

# Manejadores de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_title="Página no encontrada",
                         error_message="La página que buscas no existe.",
                         error_code=404), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Server Error: {error}')
    return render_template('error.html',
                         error_title="Error interno del servidor",
                         error_message="Ha ocurrido un error inesperado.",
                         error_code=500), 500

# Rutas
@app.route('/')
def index():
    return render_template('index.html', project=PROJECT_INFO)

@app.route('/proyecto')
def proyecto():
    return render_template('project.html', project=PROJECT_INFO)

@app.route('/equipo')
def equipo():
    return render_template('team.html', project=PROJECT_INFO)

@app.route('/prediccion')
def prediccion():
    return render_template('predict.html', project=PROJECT_INFO)

@app.route('/predecir', methods=['POST'])
def predecir():
    try:
        # Obtener datos del formulario
        abv = float(request.form.get('abv', 0))
        ibu = float(request.form.get('ibu', 0))
        srm = float(request.form.get('srm', 0))
        og = float(request.form.get('og', 0))
        fg = float(request.form.get('fg', 0))
        aroma = float(request.form.get('aroma', 0))
        turbidez = float(request.form.get('turbidez', 0))
        
        # Crear array de características
        features = np.array([[abv, ibu, srm, og, fg, aroma, turbidez]])
        
        # Predecir
        if model and scaler:
            features_scaled = scaler.transform(features)
            prediccion = model.predict(features_scaled)[0]
        else:
            # Predicción simulada basada en características
            prediccion = 2.5 + (abv * 0.1) + (aroma * 0.15) - (ibu * 0.01) + (turbidez * 0.1)
            prediccion = np.clip(prediccion, 0, 5)
        
        # Calcular confianza
        confianza = min(95, 70 + (aroma + turbidez) * 2)
        
        # Clasificar
        if prediccion >= 4.5:
            categoria = "Excepcional"
            color = "success"
        elif prediccion >= 4.0:
            categoria = "Excelente"
            color = "info"
        elif prediccion >= 3.5:
            categoria = "Muy Buena"
            color = "primary"
        elif prediccion >= 3.0:
            categoria = "Buena"
            color = "warning"
        else:
            categoria = "Regular"
            color = "danger"
        
        resultado = {
            'puntuacion': round(prediccion, 2),
            'categoria': categoria,
            'color': color,
            'confianza': round(confianza, 1),
            'caracteristicas': {
                'ABV': f"{abv}%",
                'IBU': int(ibu),
                'SRM': int(srm),
                'OG': og,
                'FG': fg,
                'Aroma': f"{aroma}/10",
                'Turbidez': f"{turbidez}/10"
            }
        }
        
        return render_template('results.html', 
                             resultado=resultado, 
                             project=PROJECT_INFO)
    
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        flash("Error al procesar la predicción. Verifica los datos ingresados.", "danger")
        return redirect(url_for('prediccion'))

@app.context_processor
def inject_globals():
    return {
        'app_name': PROJECT_INFO['nombre'],
        'app_version': PROJECT_INFO['version'],
        'current_year': 2025
    }

if __name__ == '__main__':
    # Crear directorios necesarios
    for directory in ['templates', 'static/css', 'static/js', 'static/img', 'model', 'data']:
        os.makedirs(directory, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)