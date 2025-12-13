# Guía de Inicio Rápido - NovaMind

## Requisitos Previos

- Python 3.8+
- MySQL Server 5.7+
- pip

## Paso 1: Configurar Base de Datos

### Opción A: Automático (Recomendado)
El backend crea las tablas automáticamente al ejecutarse. Solo crea la base de datos:

```sql
CREATE DATABASE IF NOT EXISTS novamind
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### Opción B: Manual con datos de prueba
Usa los scripts SQL incluidos:

```bash
cd database
mysql -u root -p < schema.sql
mysql -u root -p novamind < usuarios.sql
mysql -u root -p novamind < datos_prueba.sql
```

Esto crea las tablas, usuarios de RRHH e inserta 20 comentarios pre-analizados para testing.

## Paso 2: Configurar Variables de Entorno

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales de MySQL:

```
mysql_user=root
mysql_password=tu_password
mysql_host=127.0.0.1
mysql_port=3306
mysql_db=novamind
```

## Paso 3: Instalar Dependencias del Backend

```bash
cd backend
pip install -r requirements.txt
```

## Paso 4: Ejecutar el Backend

```bash
uvicorn main:app --reload --port 8000
 --reload --port 8000
```

Verifica que esté funcionando en: http://127.0.0.1:8000/docs

## Paso 5: Instalar Dependencias del Frontend

En otra terminal:

```bash
cd frontend

```

## Paso 6: Ejecutar el Frontend

### Opción A: Página Pública (Empleados)
Para que los empleados dejen comentarios anónimos:

```bash
streamlit run app_publica.py
```
 
Acceso: http://localhost:8501

### Opción B: Panel de RRHH (Con Login)
Para que RRHH acceda al dashboard y análisis:

```bash
streamlit run app_rrhh.py --server.port 8502
```

Acceso: http://localhost:8502

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

## Estructura de Uso

1. **Ingresar Comentarios**: Usa la página "Ingresar Comentario" para probar el análisis individual
2. **Carga Masiva**: Prepara un CSV con columnas: comentario, departamento, equipo, fecha
3. **Ver Dashboard**: Accede al Dashboard para visualizar estadísticas y gráficos
4. **Alertas**: Revisa patrones críticos en la página de Alertas

## Arquitectura Modular

```
Backend:
- config/: Configuración y conexión DB
- core/: Modelos y servicios CRUD
- ia/: Análisis NLP con Transformers
- api/: Endpoints REST
- utils/: Helpers

Frontend:
- pages/: Páginas Streamlit
- utils/: Helpers para API y visualización
```
