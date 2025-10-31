"""
Script de verificación de instalación - CHOCOBREW
Verifica que todos los componentes estén correctamente instalados
"""

import sys
import os

print("=" * 70)
print("VERIFICACIÓN DE INSTALACIÓN - CHOCOBREW")
print("Sistema de Análisis ML para Cerveza Artesanal de Cacao")
print("=" * 70)

# Colores para terminal (opcional)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check(condition, message):
    """Verifica una condición y muestra resultado"""
    if condition:
        print(f"{GREEN}✓{RESET} {message}")
        return True
    else:
        print(f"{RED}✗{RESET} {message}")
        return False

# =====================================================
# 1. VERIFICAR PYTHON
# =====================================================
print("\n[1] VERIFICANDO PYTHON")
python_version = sys.version_info
python_ok = check(
    python_version >= (3, 8),
    f"Python {python_version.major}.{python_version.minor}.{python_version.micro} (Requerido: 3.8+)"
)

if not python_ok:
    print(f"{RED}ERROR: Actualiza Python a versión 3.8 o superior{RESET}")
    sys.exit(1)

# =====================================================
# 2. VERIFICAR MÓDULOS PYTHON
# =====================================================
print("\n[2] VERIFICANDO MÓDULOS PYTHON")

modulos_requeridos = {
    'flask': 'Flask',
    'mysql.connector': 'MySQL Connector',
    'sklearn': 'Scikit-learn',
    'numpy': 'NumPy',
    'pandas': 'Pandas',
    'joblib': 'Joblib',
    'qrcode': 'QR Code Generator',
    'PIL': 'Pillow (PIL)',
}

modulos_ok = True
for modulo, nombre in modulos_requeridos.items():
    try:
        __import__(modulo)
        check(True, f"{nombre}")
    except ImportError:
        check(False, f"{nombre} - FALTA")
        modulos_ok = False

if not modulos_ok:
    print(f"\n{YELLOW}Instala los módulos faltantes:{RESET}")
    print("pip install -r requirements.txt")

# =====================================================
# 3. VERIFICAR MYSQL
# =====================================================
print("\n[3] VERIFICANDO CONEXIÓN MYSQL")

try:
    import mysql.connector
    from mysql.connector import Error
    
    # Intentar conexión básica
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Ajusta si tienes contraseña
        )
        
        check(True, "Conexión a MySQL servidor")
        
        # Verificar base de datos
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES LIKE 'beer_predictor_db'")
        db_exists = cursor.fetchone() is not None
        
        check(db_exists, "Base de datos 'beer_predictor_db'")
        
        if db_exists:
            # Verificar tablas
            cursor.execute("USE beer_predictor_db")
            cursor.execute("SHOW TABLES")
            tablas = [t[0] for t in cursor.fetchall()]
            
            check('usuarios' in tablas, "Tabla 'usuarios'")
            check('lotes_chocobrew' in tablas, "Tabla 'lotes_chocobrew'")
            check('predicciones' in tablas, "Tabla 'predicciones'")
        else:
            print(f"{YELLOW}Ejecuta: mysql -u root -p < database.sql{RESET}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        check(False, f"Conexión MySQL: {e}")
        print(f"{YELLOW}Verifica que MySQL esté corriendo y las credenciales sean correctas{RESET}")
        
except ImportError:
    check(False, "MySQL Connector - Instala: pip install mysql-connector-python")

# =====================================================
# 4. VERIFICAR ESTRUCTURA DE ARCHIVOS
# =====================================================
print("\n[4] VERIFICANDO ESTRUCTURA DE ARCHIVOS")

archivos_requeridos = [
    'app.py',
    'train_chocobrew_model.py',
    'database.sql',
    'requirements.txt',
    'templates/base.html',
    'templates/index.html',
    'templates/login.html',
    'templates/register.html',
    'templates/analisis.html',
    'templates/resultado_lote.html',
    'templates/mis_lotes.html',
    'templates/project.html',
    'templates/team.html',
    'templates/error.html',
]

archivos_ok = True
for archivo in archivos_requeridos:
    existe = os.path.exists(archivo)
    check(existe, archivo)
    if not existe:
        archivos_ok = False

# =====================================================
# 5. VERIFICAR MODELO ML
# =====================================================
print("\n[5] VERIFICANDO MODELO ML")

modelo_existe = os.path.exists('model/beer_model.pkl')
scaler_existe = os.path.exists('model/scaler.pkl')

check(modelo_existe, "model/beer_model.pkl")
check(scaler_existe, "model/scaler.pkl")

if not (modelo_existe and scaler_existe):
    print(f"{YELLOW}Entrena el modelo: python train_chocobrew_model.py{RESET}")
else:
    # Intentar cargar modelo
    try:
        import joblib
        model = joblib.load('model/beer_model.pkl')
        scaler = joblib.load('model/scaler.pkl')
        check(True, "Modelo cargado correctamente")
    except Exception as e:
        check(False, f"Error cargando modelo: {e}")

# =====================================================
# 6. VERIFICAR DIRECTORIOS
# =====================================================
print("\n[6] VERIFICANDO DIRECTORIOS")

directorios = ['templates', 'static', 'static/css', 'static/js', 'static/img', 'model', 'data']
for directorio in directorios:
    check(os.path.exists(directorio), directorio)

# =====================================================
# RESUMEN FINAL
# =====================================================
print("\n" + "=" * 70)
print("RESUMEN DE VERIFICACIÓN")
print("=" * 70)

todo_ok = python_ok and modulos_ok and archivos_ok

if todo_ok:
    print(f"\n{GREEN}✓ ¡INSTALACIÓN COMPLETA!{RESET}")
    print("\nPasos siguientes:")
    print("1. python train_chocobrew_model.py  (si no has entrenado el modelo)")
    print("2. python app.py")
    print("3. Abrir http://localhost:5000")
else:
    print(f"\n{YELLOW}⚠ HAY COMPONENTES FALTANTES{RESET}")
    print("\nRevisa los errores marcados con ✗ arriba")
    print("Consulta el README.md para instrucciones detalladas")

print("\n" + "=" * 70)