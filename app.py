from flask import Flask, render_template, request, flash, redirect, url_for, session
import os
import logging
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import numpy as np
from datetime import timedelta, datetime
import io
import base64
import socket

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import Error
    # psycopg2-binary ES psycopg2, solo el nombre del paquete es diferente
    POSTGRES_AVAILABLE = True
    print("✅ PostgreSQL disponible")
except ImportError as e:
    POSTGRES_AVAILABLE = False
    print(f"⚠️ PostgreSQL no disponible: {e}")

def get_db_connection():
    if not POSTGRES_AVAILABLE:
        print("🔄 Modo desarrollo - Sin base de datos")
        return None
    
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            connection = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            print("✅ Conectado a PostgreSQL")
            return connection
        else:
            print("❌ DATABASE_URL no configurado")
            return None
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return None

# Función para obtener IP local automáticamente
def obtener_ip_local():
    """Obtiene la IP local de la máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception:
        return "localhost"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar QR Code
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    logger.warning("qrcode no disponible. Instala: pip install qrcode[pil]")

# Configuración PostgreSQL para Neon.tech
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import Error
    POSTGRES_AVAILABLE = True
    print("🎯 psycopg2-binary instalado correctamente")
except ImportError as e:
    POSTGRES_AVAILABLE = False
    print(f"❌ Error importando psycopg2: {e}")

def get_db_connection():
    if not POSTGRES_AVAILABLE:
        print("🔧 Modo desarrollo - PostgreSQL no disponible")
        return None
    
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            print(f"🎯 Intentando conectar a: {database_url[:50]}...")
            connection = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            print("✅ ¡CONEXIÓN EXITOSA a PostgreSQL!")
            return connection
        else:
            print("❌ DATABASE_URL no configurado")
            return None
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return None

# Decorador login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Información del proyecto (SIMPLIFICADA)
PROJECT_INFO = {
    'nombre': 'CHOCOBREW Predictor',
    'version': '2.0',
    'producto': 'Cerveza Artesanal de Cacao',
    'emprendimiento': 'CHOCOBREW',
    'ubicacion': 'Loja, Ecuador',
    'vida_util_dias': 120,
}

# Cargar modelo
model = None
scaler = None
try:
    import joblib
    model = joblib.load('model/beer_model.pkl')
    scaler = joblib.load('model/scaler.pkl')
    logger.info("Modelo cargado exitosamente")
except Exception as e:
    logger.warning(f"Modelo no encontrado: {e}. Usando predicción simulada")
    
# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def calcular_tabla_nutricional(abv, porcentaje_cacao, og):
    """Calcula valores nutricionales aproximados por 100ml"""
    calorias = (og - 1) * 1000 * 4 + (abv * 7)
    carbohidratos = (og - 1) * 1000 * 0.8
    proteinas = 0.3 + (porcentaje_cacao * 0.1)
    grasas = porcentaje_cacao * 0.15
    azucares = carbohidratos * 0.6
    
    return {
        'calorias': round(calorias),
        'carbohidratos': round(carbohidratos, 1),
        'proteinas': round(proteinas, 1),
        'grasas': round(grasas, 1),
        'azucares': round(azucares, 1),
        'alcohol': round(abv, 1)
    }

def generar_codigo_qr(lote_id):
    """Genera código QR con URL accesible desde red local"""
    if not QR_AVAILABLE:
        return None
    
    # En producción, usar la URL real de Render
    if os.environ.get('RENDER'):
        # En Render, usar la URL del deploy
        base_url = os.environ.get('RENDER_EXTERNAL_URL', f"http://{obtener_ip_local()}:5000")
    else:
        # En desarrollo local
        base_url = f"http://{obtener_ip_local()}:5000"
    
    url_lote = f"{base_url}/lote-publico/{lote_id}"
    
    logger.info(f"Generando QR con URL: {url_lote}")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(url_lote)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64

def guardar_lote_en_bd(datos_lote, user_id):
    """Guarda el lote completo en PostgreSQL"""
    connection = get_db_connection()
    if not connection:
        logger.warning("No se pudo conectar a la base de datos")
        return None
    
    try:
        cursor = connection.cursor()
        
        query = """
        INSERT INTO lotes_chocobrew (
            user_id, codigo_lote, fecha_elaboracion, fecha_vencimiento,
            abv, ibu, srm, og, fg, porcentaje_cacao,
            dias_fermentacion, dias_maduracion, puntuacion, categoria,
            calorias, carbohidratos, proteinas, grasas, azucares,
            qr_code_base64
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        valores = (
            int(user_id),
            str(datos_lote['codigo_lote']),
            str(datos_lote['fecha_elaboracion']),
            str(datos_lote['fecha_vencimiento']),
            float(datos_lote['abv']),
            int(datos_lote['ibu']),
            int(datos_lote['srm']),
            float(datos_lote['og']),
            float(datos_lote['fg']),
            float(datos_lote['porcentaje_cacao']),
            int(datos_lote['dias_fermentacion']),
            int(datos_lote['dias_maduracion']),
            float(datos_lote['puntuacion']),
            str(datos_lote['categoria']),
            int(datos_lote['nutricional']['calorias']),
            float(datos_lote['nutricional']['carbohidratos']),
            float(datos_lote['nutricional']['proteinas']),
            float(datos_lote['nutricional']['grasas']),
            float(datos_lote['nutricional']['azucares']),
            datos_lote.get('qr_code')
        )
        
        cursor.execute(query, valores)
        connection.commit()
        
        lote_id = cursor.fetchone()['id']
        logger.info(f"Lote guardado en BD con ID: {lote_id}")
        
        return lote_id
        
    except Error as e:
        logger.error(f"Error guardando lote en BD: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()

# =====================================================
# MANEJADORES DE ERRORES
# =====================================================

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
                         error_title="Error interno",
                         error_message="Error inesperado.",
                         error_code=500), 500

# =====================================================
# RUTAS DE AUTENTICACIÓN
# =====================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Completa todos los campos', 'danger')
            return render_template('login.html')
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
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
                logger.error(f"Error login: {e}")
                flash('Error al iniciar sesión', 'danger')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Error de conexión a la base de datos', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([nombre, email, password, confirm_password]):
            flash('Completa todos los campos', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener mínimo 6 caracteres', 'danger')
            return render_template('register.html')
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Este correo ya está registrado', 'warning')
                    return render_template('register.html')
                
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s) RETURNING id",
                    (nombre, email, hashed_password)
                )
                connection.commit()
                flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
                return redirect(url_for('login'))
            except Error as e:
                logger.error(f"Error en registro: {e}")
                flash('Error al registrar usuario', 'danger')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Error de conexión a la base de datos', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    nombre = session.get('user_name', 'Usuario')
    session.clear()
    flash(f'Hasta pronto {nombre}!', 'info')
    return redirect(url_for('login'))

# =====================================================
# RUTAS PÚBLICAS
# =====================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lote-publico/<int:lote_id>')
def lote_publico(lote_id):
    """Página pública para ver información del lote al escanear QR"""
    connection = get_db_connection()
    
    if not connection:
        return render_template('error.html',
                             error_title="Error de conexión",
                             error_message="No se pudo conectar a la base de datos",
                             error_code=500), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM lotes_chocobrew 
            WHERE id = %s
        """, (lote_id,))
        lote = cursor.fetchone()
        
        if not lote:
            return render_template('error.html',
                                 error_title="Lote no encontrado",
                                 error_message="Este código QR no es válido o el lote no existe",
                                 error_code=404), 404
        
        datos_lote = {
            'id': lote['id'],
            'codigo_lote': lote['codigo_lote'],
            'fecha_elaboracion': lote['fecha_elaboracion'].strftime('%d/%m/%Y'),
            'fecha_vencimiento': lote['fecha_vencimiento'].strftime('%d/%m/%Y'),
            'abv': float(lote['abv']),
            'ibu': lote['ibu'],
            'srm': lote['srm'],
            'porcentaje_cacao': float(lote['porcentaje_cacao']),
            'puntuacion': float(lote['puntuacion']),
            'categoria': lote['categoria'],
            'nutricional': {
                'calorias': lote['calorias'],
                'carbohidratos': float(lote['carbohidratos']),
                'proteinas': float(lote['proteinas']),
                'grasas': float(lote['grasas']),
                'azucares': float(lote['azucares']),
                'alcohol': float(lote['abv'])
            }
        }
        
        return render_template('lote_publico.html', lote=datos_lote)
        
    except Error as e:
        logger.error(f"Error obteniendo lote público: {e}")
        return render_template('error.html',
                             error_title="Error del servidor",
                             error_message="No se pudo cargar la información del lote",
                             error_code=500), 500
    finally:
        cursor.close()
        connection.close()

# =====================================================
# RUTAS PROTEGIDAS - ANÁLISIS DE LOTES
# =====================================================

@app.route('/analisis')
@login_required
def analisis():
    return render_template('analisis.html', current_year=2025)

@app.route('/procesar_lote', methods=['POST'])
@login_required
def procesar_lote():
    try:
        # Obtener datos del formulario
        codigo_lote = request.form.get('codigo_lote', '').strip()
        fecha_elaboracion = request.form.get('fecha_elaboracion', '')
        abv = float(request.form.get('abv', 0))
        ibu = float(request.form.get('ibu', 0))
        srm = float(request.form.get('srm', 0))
        og = float(request.form.get('og', 0))
        fg = float(request.form.get('fg', 0))
        porcentaje_cacao = float(request.form.get('porcentaje_cacao', 0))
        dias_fermentacion = int(request.form.get('dias_fermentacion', 0))
        dias_maduracion = int(request.form.get('dias_maduracion', 0))
        
        # Validaciones
        if not codigo_lote or not fecha_elaboracion:
            flash('Código de lote y fecha son obligatorios', 'danger')
            return redirect(url_for('analisis'))
        
        if fg >= og:
            flash('Error: La densidad final (FG) debe ser menor que la inicial (OG)', 'danger')
            return redirect(url_for('analisis'))
        
        # Verificar código duplicado
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT id FROM lotes_chocobrew WHERE codigo_lote = %s",
                    (codigo_lote,)
                )
                if cursor.fetchone():
                    flash(f'El código de lote "{codigo_lote}" ya existe. Usa otro código.', 'warning')
                    cursor.close()
                    connection.close()
                    return redirect(url_for('analisis'))
                cursor.close()
                connection.close()
            except Error as e:
                logger.error(f"Error verificando código: {e}")
        
        # Calcular fecha de vencimiento
        fecha_elab = datetime.strptime(fecha_elaboracion, '%Y-%m-%d')
        fecha_venc = fecha_elab + timedelta(days=PROJECT_INFO['vida_util_dias'])
        
        # Predicción de calidad
        features = np.array([[abv, ibu, srm, og, fg, porcentaje_cacao, dias_fermentacion, dias_maduracion]])
        
        if model and scaler:
            try:
                features_scaled = scaler.transform(features)
                prediccion = float(model.predict(features_scaled)[0])
                logger.info(f"Predicción ML: {prediccion}")
            except Exception as e:
                logger.error(f"Error en predicción ML: {e}")
                prediccion = 2.5 + (abv * 0.08) + (porcentaje_cacao * 0.15) - (ibu * 0.008) + (dias_maduracion * 0.02)
                prediccion = float(np.clip(prediccion, 0, 5))
        else:
            logger.warning("Modelo no disponible, usando fórmula basada en cacao")
            prediccion = 2.5 + (abv * 0.08) + (porcentaje_cacao * 0.15) - (ibu * 0.008) + (dias_maduracion * 0.02)
            prediccion = float(np.clip(prediccion, 0, 5))
        
        # Clasificar calidad
        if prediccion >= 4.5:
            categoria = "Premium"
        elif prediccion >= 4.0:
            categoria = "Excelente"
        elif prediccion >= 3.5:
            categoria = "Muy Buena"
        elif prediccion >= 3.0:
            categoria = "Buena"
        else:
            categoria = "Regular"
        
        # Calcular tabla nutricional
        nutricional = calcular_tabla_nutricional(abv, porcentaje_cacao, og)
        
        # Datos del lote (SIN QR todavía)
        datos_lote = {
            'codigo_lote': codigo_lote,
            'fecha_elaboracion': fecha_elaboracion,
            'fecha_vencimiento': fecha_venc.strftime('%Y-%m-%d'),
            'abv': float(abv),
            'ibu': int(ibu),
            'srm': int(srm),
            'og': float(og),
            'fg': float(fg),
            'porcentaje_cacao': float(porcentaje_cacao),
            'dias_fermentacion': int(dias_fermentacion),
            'dias_maduracion': int(dias_maduracion),
            'puntuacion': float(round(prediccion, 2)),
            'categoria': categoria,
            'nutricional': nutricional,
            'qr_code': None
        }
        
        # Guardar primero para obtener el ID
        lote_id = guardar_lote_en_bd(datos_lote, session['user_id'])
        
        if lote_id:
            # Generar el QR con el ID
            qr_code = generar_codigo_qr(lote_id)
            datos_lote['qr_code'] = qr_code
            
            # Actualizar el registro con el QR
            connection = get_db_connection()
            if connection and qr_code:
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "UPDATE lotes_chocobrew SET qr_code_base64 = %s WHERE id = %s",
                        (qr_code, lote_id)
                    )
                    connection.commit()
                    logger.info(f"QR actualizado para lote ID: {lote_id}")
                except Error as e:
                    logger.error(f"Error actualizando QR: {e}")
                finally:
                    cursor.close()
                    connection.close()
            
            flash('¡Lote guardado exitosamente!', 'success')
        else:
            flash('Advertencia: No se pudo guardar en la base de datos', 'warning')
        
        return render_template('resultado_lote.html', lote=datos_lote)
    
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        flash(f"Error en los datos ingresados: {str(e)}", "danger")
        return redirect(url_for('analisis'))
    except Exception as e:
        logger.error(f"Error procesando lote: {e}")
        flash(f"Error al procesar el lote: {str(e)}", "danger")
        return redirect(url_for('analisis'))

@app.route('/mis-lotes')
@login_required
def mis_lotes():
    """Muestra todos los lotes del usuario actual"""
    connection = get_db_connection()
    lotes = []
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM lotes_chocobrew 
                WHERE user_id = %s 
                ORDER BY fecha_elaboracion DESC
            """, (session['user_id'],))
            lotes_raw = cursor.fetchall()
            
            for lote in lotes_raw:
                lote['puntuacion'] = float(lote['puntuacion'])
                lote['abv'] = float(lote['abv'])
                lote['og'] = float(lote['og'])
                lote['fg'] = float(lote['fg'])
                lote['porcentaje_cacao'] = float(lote['porcentaje_cacao'])
                lote['carbohidratos'] = float(lote['carbohidratos'])
                lote['proteinas'] = float(lote['proteinas'])
                lote['grasas'] = float(lote['grasas'])
                lote['azucares'] = float(lote['azucares'])
                lotes.append(lote)
                
        except Error as e:
            logger.error(f"Error obteniendo lotes: {e}")
            flash('Error al cargar los lotes', 'danger')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('mis_lotes.html', lotes=lotes)

@app.route('/ver-lote/<int:lote_id>')
@login_required
def ver_lote(lote_id):
    """Ver detalles de un lote específico"""
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM lotes_chocobrew 
                WHERE id = %s AND user_id = %s
            """, (lote_id, session['user_id']))
            lote = cursor.fetchone()
            
            if lote:
                datos_lote = {
                    'codigo_lote': lote['codigo_lote'],
                    'fecha_elaboracion': lote['fecha_elaboracion'].strftime('%Y-%m-%d'),
                    'fecha_vencimiento': lote['fecha_vencimiento'].strftime('%Y-%m-%d'),
                    'abv': float(lote['abv']),
                    'ibu': lote['ibu'],
                    'srm': lote['srm'],
                    'og': float(lote['og']),
                    'fg': float(lote['fg']),
                    'porcentaje_cacao': float(lote['porcentaje_cacao']),
                    'dias_fermentacion': lote['dias_fermentacion'],
                    'dias_maduracion': lote['dias_maduracion'],
                    'puntuacion': float(lote['puntuacion']),
                    'categoria': lote['categoria'],
                    'nutricional': {
                        'calorias': lote['calorias'],
                        'carbohidratos': float(lote['carbohidratos']),
                        'proteinas': float(lote['proteinas']),
                        'grasas': float(lote['grasas']),
                        'azucares': float(lote['azucares']),
                        'alcohol': float(lote['abv'])
                    },
                    'qr_code': lote['qr_code_base64']
                }
                
                return render_template('resultado_lote.html', lote=datos_lote)
            else:
                flash('Lote no encontrado', 'warning')
                return redirect(url_for('mis_lotes'))
                
        except Error as e:
            logger.error(f"Error obteniendo lote: {e}")
            flash('Error al cargar el lote', 'danger')
        finally:
            cursor.close()
            connection.close()
    
    return redirect(url_for('mis_lotes'))

# =====================================================
# CONTEXT PROCESSOR (ESENCIAL PARA LOS BOTONES)
# =====================================================

@app.context_processor
def inject_globals():
    user_logged_in = 'user_id' in session
    user_name = session.get('user_name', '')
    
    # Debug en consola
    print(f"🎯 Context Processor - Usuario logueado: {user_logged_in}")
    print(f"🎯 Context Processor - Nombre: {user_name}")
    
    return {
        'current_year': 2025,
        'user_logged_in': user_logged_in,
        'user_name': user_name
    }

# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    for directory in ['templates', 'static/css', 'static/js', 'static/img', 'model', 'data']:
        os.makedirs(directory, exist_ok=True)
    
    connection = get_db_connection()
    if connection:
        logger.info("✓ Conexión a PostgreSQL exitosa")
        connection.close()
    else:
        logger.warning("⚠ No se pudo conectar a PostgreSQL. Verifica la configuración.")
    
    # Configuración para Render
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    ip_local = obtener_ip_local()
    logger.info(f"Iniciando aplicación CHOCOBREW v{PROJECT_INFO['version']}")
    
    if os.environ.get('RENDER'):
        logger.info(f"🚀 Aplicación desplegada en Render - Puerto: {port}")
        app.run(debug=debug_mode, host='0.0.0.0', port=port)
    else:
        logger.info(f"🌐 Accede desde tu PC: http://localhost:5000")
        logger.info(f"📱 Accede desde tu celular: http://{ip_local}:5000")
        logger.info(f"⚠️  Asegúrate de que tu celular esté en la misma red WiFi")
        app.run(debug=True, host='0.0.0.0', port=5000)