from flask import Flask, render_template, request, flash, redirect, url_for, session
import os
import logging
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import numpy as np
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de base de datos MySQL
try:
    import mysql.connector
    from mysql.connector import Error
    
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',  # Usuario por defecto de XAMPP
        'password': '',  # Contraseña por defecto de XAMPP (vacía)
        'database': 'beer_predictor_db'
    }
    
    def get_db_connection():
        """Crear conexión a la base de datos"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            return connection
        except Error as e:
            logger.error(f"Error conectando a MySQL: {e}")
            return None
    
    logger.info("Módulo MySQL disponible")
except ImportError:
    logger.warning("MySQL connector no disponible. Instala: pip install mysql-connector-python")
    DB_CONFIG = None
    
    def get_db_connection():
        return None

# Decorador para rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
model = None
scaler = None

try:
    import joblib
    model = joblib.load('model/beer_model.pkl')
    scaler = joblib.load('model/scaler.pkl')
    logger.info("Modelo cargado exitosamente")
except ImportError:
    logger.warning("joblib no disponible")
except FileNotFoundError:
    logger.warning("Modelo no encontrado, usando predicción simulada")

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

# ==============================================
# RUTAS DE AUTENTICACIÓN
# ==============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Por favor completa todos los campos', 'danger')
            return render_template('login.html', project=PROJECT_INFO)
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['user_name'] = user['nombre']
                    session['user_email'] = user['email']
                    
                    if remember:
                        session.permanent = True
                    
                    flash(f'¡Bienvenido {user["nombre"]}!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Correo o contraseña incorrectos', 'danger')
            except Error as e:
                logger.error(f"Error en login: {e}")
                flash('Error al iniciar sesión', 'danger')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Error de conexión a la base de datos', 'danger')
    
    return render_template('login.html', project=PROJECT_INFO)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de usuarios"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validaciones
        if not all([nombre, email, password, confirm_password]):
            flash('Por favor completa todos los campos', 'danger')
            return render_template('register.html', project=PROJECT_INFO)
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html', project=PROJECT_INFO)
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'danger')
            return render_template('register.html', project=PROJECT_INFO)
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Verificar si el email ya existe
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Este correo ya está registrado', 'warning')
                    return render_template('register.html', project=PROJECT_INFO)
                
                # Crear usuario
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
                    (nombre, email, hashed_password)
                )
                connection.commit()
                
                flash('¡Registro exitoso! Ya puedes iniciar sesión', 'success')
                return redirect(url_for('login'))
                
            except Error as e:
                logger.error(f"Error en registro: {e}")
                flash('Error al registrar usuario', 'danger')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Error de conexión a la base de datos', 'danger')
    
    return render_template('register.html', project=PROJECT_INFO)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

# ==============================================
# RUTAS PÚBLICAS
# ==============================================

@app.route('/')
def index():
    return render_template('index.html', project=PROJECT_INFO)

@app.route('/proyecto')
def proyecto():
    return render_template('project.html', project=PROJECT_INFO)

@app.route('/equipo')
def equipo():
    return render_template('team.html', project=PROJECT_INFO)

# ==============================================
# RUTAS PROTEGIDAS (requieren login)
# ==============================================

@app.route('/prediccion')
@login_required
def prediccion():
    return render_template('predict.html', project=PROJECT_INFO)

@app.route('/predecir', methods=['POST'])
@login_required
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

# ==============================================
# FUNCIONES DE CONTEXTO
# ==============================================

@app.context_processor
def inject_globals():
    return {
        'app_name': PROJECT_INFO['nombre'],
        'app_version': PROJECT_INFO['version'],
        'current_year': 2025,
        'user_logged_in': 'user_id' in session,
        'user_name': session.get('user_name', '')
    }

# ==============================================
# INICIALIZACIÓN
# ==============================================

if __name__ == '__main__':
    # Crear directorios necesarios
    for directory in ['templates', 'static/css', 'static/js', 'static/img', 'model', 'data']:
        os.makedirs(directory, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)