from flask import Flask, render_template, request, flash, redirect, url_for
import os
import logging
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Información del proyecto Aulas Espejo
PROJECT_INFO = {
    'nombre': 'Proyecto Aulas Espejo',
    'subtitulo': 'Colaboración Internacional en Educación Superior',
    'version': '1.0',
    'descripcion': 'Iniciativa de colaboración académica internacional que conecta estudiantes y docentes de diferentes universidades para compartir conocimientos, experiencias culturales y metodologías de enseñanza innovadoras.',
    'objetivos': [
        {
            'titulo': 'Intercambio Cultural',
            'descripcion': 'Fomentar el entendimiento intercultural y la colaboración entre estudiantes de diferentes países',
            'icono': 'fas fa-globe-americas'
        },
        {
            'titulo': 'Innovación Pedagógica',
            'descripcion': 'Implementar metodologías de enseñanza colaborativas y tecnologías educativas avanzadas',
            'icono': 'fas fa-lightbulb'
        },
        {
            'titulo': 'Desarrollo de Competencias',
            'descripcion': 'Fortalecer habilidades de comunicación, trabajo en equipo y pensamiento crítico',
            'icono': 'fas fa-users-cog'
        }
    ],
    'universidades': [
        {
            'nombre': 'Universidad Principal',
            'pais': 'Colombia',
            'ciudad': 'Bogotá',
            'estudiantes': 45,
            'facultad': 'Ingeniería de Sistemas'
        },
        {
            'nombre': 'Universidad Colaboradora',
            'pais': 'País Colaborador',
            'ciudad': 'Ciudad',
            'estudiantes': 38,
            'facultad': 'Ciencias de la Computación'
        }
    ],
    'equipo': [
        {
            'nombre': 'Dr. Nombre Apellido',
            'rol': 'Director del Proyecto',
            'universidad': 'Universidad Principal',
            'email': 'director@universidad.edu'
        },
        {
            'nombre': 'Dra. Nombre Apellido',
            'rol': 'Co-directora',
            'universidad': 'Universidad Colaboradora',
            'email': 'codirectora@universidad.edu'
        },
        {
            'nombre': 'Nombre Apellido',
            'rol': 'Coordinador Técnico',
            'universidad': 'Universidad Principal',
            'email': 'coordinador@universidad.edu'
        }
    ],
    'duracion': 'Agosto 2025 - Diciembre 2025',
    'modalidad': 'Virtual Sincrónico',
    'participantes': '83 estudiantes',
    'institucion': 'Universidad Principal',
    'fecha_inicio': 'Agosto 2025'
}

# Manejadores de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('pagina_error.html', 
                         error_title="Página no encontrada",
                         error_message="La página que buscas no existe.",
                         error_code=404), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Server Error: {error}')
    return render_template('pagina_error.html',
                         error_title="Error interno del servidor",
                         error_message="Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo.",
                         error_code=500), 500

@app.errorhandler(RequestEntityTooLarge)
def too_large(error):
    return render_template('pagina_error.html',
                         error_title="Archivo demasiado grande",
                         error_message="El archivo enviado supera el límite de tamaño permitido.",
                         error_code=413), 413

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html', project=PROJECT_INFO)

# Funciones de contexto para templates
@app.context_processor
def inject_globals():
    """Inyecta variables globales a todos los templates."""
    return {
        'app_name': PROJECT_INFO['nombre'],
        'app_version': PROJECT_INFO['version'],
        'current_year': 2025
    }

if __name__ == '__main__':
    # Verificar que existe el template
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        logger.warning("Directorio 'templates' creado. Asegúrate de colocar index.html allí.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)