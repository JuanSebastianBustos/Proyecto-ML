# 🍺 CHOCOBREW - Sistema de Análisis ML para Cerveza Artesanal de Cacao

Sistema inteligente de predicción de calidad y gestión de lotes para cerveza artesanal con cacao fino de aroma ecuatoriano.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Características

- ✅ **Predicción de Calidad ML**: Random Forest para predecir calificación 0-5 estrellas
- ✅ **Generación de QR Codes**: Códigos únicos por lote con información completa
- ✅ **Tabla Nutricional**: Cálculo automático de valores por 100ml
- ✅ **Gestión de Lotes**: Registro y seguimiento de producción
- ✅ **Autenticación**: Sistema de usuarios con MySQL
- ✅ **Dashboard**: Visualización de estadísticas por usuario

---

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **ML**: Scikit-learn, NumPy, Pandas
- **Base de Datos**: MySQL 8.0+
- **Frontend**: Bootstrap 5, JavaScript
- **QR Generation**: qrcode + PIL

---

## 📦 Requisitos Previos

### 1. Instalar Python 3.8+
```bash
python --version  # Verificar versión
```

### 2. Instalar MySQL 8.0+
- **Windows**: [Descargar MySQL Installer](https://dev.mysql.com/downloads/installer/)
- **Linux**: 
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```
- **macOS**: 
```bash
brew install mysql
brew services start mysql
```

### 3. Verificar MySQL
```bash
mysql --version
mysql -u root -p  # Probar conexión
```

---

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar o Descargar el Proyecto
```bash
# Si tienes git
git clone <url-repositorio>
cd Proyecto-ML

# O simplemente descargar y extraer el ZIP
```

### Paso 2: Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install --upgrade pip
pip install flask
pip install mysql-connector-python
pip install scikit-learn
pip install numpy
pip install pandas
pip install joblib
pip install qrcode[pil]
pip install werkzeug
```

O usar requirements.txt:
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar MySQL

#### 4.1 Crear Base de Datos
```bash
# Abrir MySQL
mysql -u root -p

# En el prompt de MySQL:
```

```sql
CREATE DATABASE beer_predictor_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### 4.2 Ejecutar Script SQL
```bash
mysql -u root -p beer_predictor_db < database.sql
```

O copiar y pegar el contenido del archivo `database.sql` en MySQL Workbench.

#### 4.3 Verificar Tablas Creadas
```sql
USE beer_predictor_db;
SHOW TABLES;
-- Deberías ver: usuarios, lotes_chocobrew, predicciones

DESCRIBE usuarios;
DESCRIBE lotes_chocobrew;
```

### Paso 5: Configurar Credenciales MySQL

Editar `app.py` líneas 30-36:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',              # Tu usuario MySQL
    'password': '',              # Tu contraseña MySQL (si la tienes)
    'database': 'beer_predictor_db'
}
```

### Paso 6: Entrenar Modelo ML
```bash
python train_chocobrew_model.py
```

**Salida esperada:**
```
✓ Dataset generado: 600 lotes simulados
✓ Modelo entrenado exitosamente
✓ R² Score: 0.87 (87%)
✓ Modelo guardado en: model/beer_model.pkl
```

### Paso 7: Ejecutar Aplicación
```bash
python app.py
```

**Salida esperada:**
```
INFO:root:Módulo MySQL disponible
INFO:root:Modelo cargado exitosamente
INFO:root:✓ Conexión a MySQL exitosa
INFO:root:Iniciando aplicación CHOCOBREW v2.0
 * Running on http://0.0.0.0:5000
```

### Paso 8: Abrir en Navegador
```
http://localhost:5000
```

---

## 👤 Crear Primera Cuenta

1. Ir a **Iniciar Sesión** → **Crear Cuenta**
2. Llenar formulario:
   - Nombre: Tu nombre
   - Email: tu@email.com
   - Contraseña: mínimo 6 caracteres
3. Click en **Crear Cuenta**
4. Iniciar sesión con tus credenciales

---

## 📊 Usar el Sistema

### 1. Crear Nuevo Lote
- Click en **Nuevo Lote** (navbar)
- Llenar formulario:
  - **Código de Lote**: Ej: `CHOCO-2025-001`
  - **Fecha de Elaboración**: Hoy o fecha anterior
  - **ABV**: 4.0% - 10.0% (slider)
  - **IBU**: 15 - 70 (slider)
  - **SRM**: 10 - 40 (slider)
  - **Porcentaje Cacao**: 2% - 15% ⭐ IMPORTANTE
  - **OG**: 1.045 - 1.080
  - **FG**: 1.008 - 1.020 (debe ser < OG)
  - **Días Fermentación**: 5 - 14
  - **Días Maduración**: 7 - 21
- Click **Generar Análisis y Código QR**

### 2. Ver Resultado
El sistema generará:
- ✅ Código QR único
- ✅ Predicción de calidad (0-5 estrellas)
- ✅ Categoría (Premium/Excelente/Muy Buena/Buena/Regular)
- ✅ Tabla nutricional por 100ml
- ✅ Fecha de vencimiento (120 días)

### 3. Ver Mis Lotes
- Click en **Mis Lotes** (navbar)
- Ver historial completo
- Estadísticas: total lotes, promedio calidad, etc.
- Click en cualquier lote para ver detalles

### 4. Descargar/Imprimir
- **Descargar QR**: Para etiquetas
- **Imprimir Etiqueta**: Vista previa para impresión
- **Imprimir Todo**: Reporte completo del lote

---

## 🗄️ Estructura de Base de Datos

### Tabla: `usuarios`
```sql
- id (PK)
- nombre
- email (UNIQUE)
- password (hash)
- fecha_registro
- ultimo_acceso
```

### Tabla: `lotes_chocobrew`
```sql
- id (PK)
- user_id (FK → usuarios)
- codigo_lote (UNIQUE)
- fecha_elaboracion
- fecha_vencimiento
- abv, ibu, srm, og, fg
- porcentaje_cacao ⭐
- dias_fermentacion
- dias_maduracion
- puntuacion (predicción ML)
- categoria
- calorias, carbohidratos, proteinas, grasas, azucares
- qr_code_base64
- fecha_creacion
```

### Tabla: `predicciones` (legacy)
```sql
- id (PK)
- user_id (FK)
- abv, ibu, srm, og, fg, aroma, turbidez
- puntuacion
- categoria
- confianza
- fecha_prediccion
```

---

## 🔍 Consultas SQL Útiles

### Ver todos mis lotes
```sql
USE beer_predictor_db;
SELECT codigo_lote, fecha_elaboracion, puntuacion, categoria 
FROM lotes_chocobrew 
WHERE user_id = 1 
ORDER BY fecha_elaboracion DESC;
```

### Estadísticas de usuario
```sql
SELECT * FROM resumen_lotes_usuario WHERE user_id = 1;
```

### Top 10 mejores lotes
```sql
SELECT u.nombre, l.codigo_lote, l.puntuacion, l.categoria
FROM lotes_chocobrew l
JOIN usuarios u ON l.user_id = u.id
ORDER BY l.puntuacion DESC 
LIMIT 10;
```

### Lotes próximos a vencer (30 días)
```sql
SELECT codigo_lote, fecha_vencimiento, 
       DATEDIFF(fecha_vencimiento, CURDATE()) as dias_restantes
FROM lotes_chocobrew 
WHERE fecha_vencimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
ORDER BY fecha_vencimiento;
```

---

## 🛠️ Solución de Problemas

### Error: "Could not build url for endpoint 'prediccion'"
**Solución**: Usa el `app.py` corregido. La ruta `/prediccion` ahora redirige a `/analisis`.

### Error: MySQL Connection Failed
```bash
# Verificar que MySQL esté corriendo
# Windows
services.msc  # Buscar MySQL80

# Linux
sudo systemctl status mysql
sudo systemctl start mysql

# Verificar credenciales en app.py
```

### Error: "qrcode module not found"
```bash
pip install qrcode[pil]
```

### Error: "Model not found"
```bash
# Entrenar el modelo
python train_chocobrew_model.py

# Verificar que existan:
model/beer_model.pkl
model/scaler.pkl
```

### Error: "Duplicate entry for key 'codigo_lote'"
**Solución**: El código de lote debe ser único. Usa otro código (ej: `CHOCO-2025-002`).

### Error: FG >= OG
**Solución**: La densidad final DEBE ser menor que la inicial. Ajusta los valores.

---

## 📊 Modelo Machine Learning

### Algoritmo
- **Random Forest Regressor**
- **Features**: 8 variables (ABV, IBU, SRM, OG, FG, Cacao%, Días Fermentación, Días Maduración)
- **Target**: Puntuación 0-5 estrellas

### Métricas del Modelo
- **R² Score**: 0.87 (87% de varianza explicada)
- **MAE**: 0.32 estrellas
- **RMSE**: 0.45

### Importancia de Features
1. 🍫 **Porcentaje Cacao** (más importante)
2. 🍺 **ABV**
3. ⏱️ **Días Maduración**
4. 🌿 **IBU**
5. 🎨 **SRM**
6. ⚗️ **OG/FG**
7. ⏰ **Días Fermentación**

---

## 📁 Estructura del Proyecto

```
Proyecto-ML/
├── app.py                          # Aplicación Flask principal
├── train_chocobrew_model.py        # Script entrenamiento ML
├── database.sql                    # Script creación base de datos
├── requirements.txt                # Dependencias Python
├── README.md                       # Este archivo
│
├── model/
│   ├── beer_model.pkl             # Modelo entrenado
│   └── scaler.pkl                 # Normalizador
│
├── templates/
│   ├── base.html                  # Template base
│   ├── index.html                 # Página inicio
│   ├── login.html                 # Inicio sesión
│   ├── register.html              # Registro
│   ├── analisis.html              # Formulario nuevo lote
│   ├── resultado_lote.html        # Resultados + QR
│   ├── mis_lotes.html             # Lista de lotes
│   ├── project.html               # Sobre el proyecto
│   ├── team.html                  # Equipo
│   └── error.html                 # Página error
│
└── static/
    ├── css/
    ├── js/
    └── img/
```

---

## 🤝 Equipo

### Universidad de Cundinamarca (Colombia)
- Estudiante 1 - Backend & ML
- Estudiante 2 - Frontend

### Universidad de Ecuador
- Estudiante 3 - Ciencia de Datos
- Estudiante 4 - Análisis

---

## 📝 Licencia

MIT License - Proyecto Aulas Espejo 2025

---

## 🆘 Soporte

Para problemas o consultas:
1. Revisar esta documentación
2. Verificar logs en consola
3. Revisar credenciales MySQL
4. Consultar con el equipo

---

## ✅ Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] MySQL 8.0+ instalado y corriendo
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos `beer_predictor_db` creada
- [ ] Script `database.sql` ejecutado
- [ ] Credenciales MySQL configuradas en `app.py`
- [ ] Modelo entrenado (`python train_chocobrew_model.py`)
- [ ] Aplicación corriendo (`python app.py`)
- [ ] Navegador abierto en `http://localhost:5000`
- [ ] Usuario registrado y sesión iniciada
- [ ] Primer lote creado exitosamente

---

**¡Listo! Ahora tienes CHOCOBREW funcionando completamente con MySQL** 🎉🍺🍫