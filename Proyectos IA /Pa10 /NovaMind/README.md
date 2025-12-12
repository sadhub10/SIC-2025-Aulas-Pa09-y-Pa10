# NovaMind - Análisis de Bienestar Laboral con IA

Sistema completo para analizar comentarios de empleados utilizando Inteligencia Artificial, Procesamiento de Lenguaje Natural y análisis emocional.

El backend está construido en FastAPI con modelos Transformer para detectar:

- Nivel de estrés laboral
- Estado emocional
- Categorías de problemas (sobrecarga, liderazgo, comunicación, etc.)
- Resumen automático del comentario
- Recomendaciones generadas por IA

El frontend está construido en Streamlit con dashboard interactivo, visualizaciones y sistema de alertas.

Incluye conexión a MySQL, carga de CSV, análisis por lotes, API REST documentada y estructura modular escalable.

---

# Características principales

Backend:
- FastAPI modular con endpoints REST completos
- IA basada en modelos Transformers (Sentiment, Emotion, Zero-shot, Summarizer)
- Limpieza de texto y análisis multi-dimensional
- Almacenamiento estructurado en MySQL
- Procesamiento individual y por lotes (CSV)
- Sistema de alertas automáticas por niveles de estrés
- Endpoints para estadísticas, tendencias y comparaciones

Frontend:
- Dos aplicaciones separadas:
  - **Página Pública**: Para que empleados dejen comentarios anónimos
  - **Panel RRHH**: Con autenticación para acceder a análisis y estadísticas
- Dashboard interactivo con Streamlit
- KPIs en tiempo real (estrés, emociones, categorías)
- Gráficos con Plotly (barras, pie, líneas, tendencias)
- WordCloud de comentarios
- Análisis por departamentos y equipos
- Sistema de alertas con detección de patrones
- Filtros avanzados y búsquedas personalizadas
- Carga masiva de CSV
- Sistema de autenticación con bcrypt  

---

#  Arquitectura del Proyecto

NovaMind/
│
├── backend/
│ ├── main.py
│ ├── requirements.txt
│ ├── init.py
│ │
│ ├── api/
│ │ ├── analizarComentario.py
│ │ ├── analizarLote.py
│ │ ├── manejarHistoricos.py
│ │ └── alertasAutomaticas.py
│ │
│ ├── core/
│ │ ├── coreModels.py
│ │ ├── coreServices.py
│ │ └── init.py
│ │
│ ├── config/
│ │ ├── settings.py
│ │ ├── database.py
│ │ └── init.py
│ │
│ ├── ia/
│ │ ├── iaCore.py
│ │ ├── configIA.py
│ │ ├── preProcesamiento.py
│ │ └── init.py
│ │
│ ├── utils/
│ │ ├── helpers.py
│ │ └── init.py
│ │
│ └── test/
│
├── frontend/
│ ├── app_publica.py (Página pública para empleados)
│ ├── app_rrhh.py (Panel RRHH con login)
│ ├── app.py (Deprecated)
│ ├── requirements.txt
│ │
│ ├── pages/
│ │ ├── ingresarComentario.py
│ │ ├── analisisCSV.py
│ │ ├── analisisIndividual.py
│ │ └── configuracion.py
│ │
│ └── utils/
│   ├── callBackend.py
│   ├── formatHelper.py
│   └── worldCloudUtils.py
├── database/
│ ├── schema.sql
│ ├── usuarios.sql
│ ├── datos_prueba.sql
│ ├── comentarios_ejemplo.csv
│ └── README.md
├── .env.example
└── .env

---

# 🔧 Tecnologías utilizadas

| Capa | Tecnologías |
|------|--------------|
| **Backend API** | FastAPI, Uvicorn |
| **IA / NLP** | Transformers, PyTorch, Zero-Shot, Summarization |
| **Base de Datos** | MySQL + SQLAlchemy ORM |
| **Procesamiento CSV** | Python CSV, Helpers personalizados |
| **Infraestructura** | Pydantic Settings, CORS Middleware |
| **Frontend** | Streamlit, Plotly, WordCloud, Pandas |

---

#  Instalación y Configuración

##  Clonar el repositorio

git clone https://github.com/tuusuario/NovaMind.git
cd NovaMind/backend


## 2 Crear y activar un entorno virtual

python -m venv .venv
.venv\Scripts\activate   # Windows

## 3 Instalar dependencias

pip install -r requirements.txt


##  Configurar archivo .env

mysql_user=root
mysql_password=TU_PASSWORD
mysql_host=127.0.0.1
mysql_port=3308
mysql_db=novamind


## Crear la base de datos en MySQL

**Opción A: Automático**

Solo crea la base de datos. Las tablas se crean automáticamente al ejecutar el backend:

```sql
CREATE DATABASE IF NOT EXISTS novamind
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

**Opción B: Manual con datos de prueba**

Usa los scripts SQL incluidos:

```bash
cd database
mysql -u root -p < schema.sql
mysql -u root -p novamind < datos_prueba.sql
```

Esto crea las tablas e inserta 20 comentarios analizados para testing inmediato.

##  Ejecutar el backend

uvicorn backend.main:app --reload --port 8000

##  Instalar dependencias del frontend

cd frontend
pip install -r requirements.txt

##  Ejecutar el frontend

**Página Pública (Empleados):**

```bash
streamlit run app_publica.py
```

**Panel RRHH (Con Login):**

```bash
streamlit run app_rrhh.py --server.port 8502
```

Credenciales: `admin` / `admin123`


# Documentación de la API

Ir a:http://127.0.0.1:8000/docs
---

#  Endpoints principales

## POST /login/

Autenticación de usuarios RRHH.

```json
{
  "usuario": "admin",
  "password": "admin123"
}
```

##  POST /analizar-comentario/

Analiza un comentario individual y lo guarda en MySQL.

Ejemplo Payload:
{
  "comentario": "Me siento agotado y con mucha presión laboral.",
  "meta": {
    "departamento": "Operaciones",
    "equipo": "Turno A",
    "fecha": "2025-02-01"
  }
}


Resultado incluye:
emotion
stress
categories
summary
suggestion
meta

##POST /analizar-lote/

Analiza un CSV completo y guarda cada fila como un registro.

{
  "ruta_csv": "../data/raw/comentarios_sinteticos.csv"
}

## GET /historicos/

Devuelve registros recientes guardados en MySQL.

GET /historicos/?limit=50

## GET /alertas/

Devuelve comentarios con estrés en nivel alto/medio/bajo.

GET /alertas/?nivel=alto&limite=20

## GET /estadisticas/

Obtiene estadísticas generales con filtros opcionales.

GET /estadisticas/?departamento=Operaciones

##  GET /estadisticas/departamentos/

Devuelve estadísticas agregadas por departamento.

##  GET /estadisticas/tendencias/

Obtiene tendencias temporales de estrés.

GET /estadisticas/tendencias/?dias=30

## GET /alertas/patrones/

Detecta patrones críticos automáticamente.

---

#  IA — Detalles del análisis

Cada comentario pasa por:

##  Limpieza Básica

minúsculas, espacios, normalización ligera

##  Modelo de Emoción

detecta emoción principal + score

##  Sentiment → Estrés

Convierte sentiment a nivel de estrés + refuerzo por palabras clave

##  Zero-Shot Classification

Determina categorías del comentario (liderazgo, carga laboral, etc.)

## Resumen Automático

usa modelo distilBART

##  Generación de sugerencias

Recomendaciones basadas en reglas + IA

---


#  Base de Datos

Tabla principal: analisis_comentarios

Campos:

| Campo                       | Descripción         |
| --------------------------- | ------------------- |
| comentario                  | Texto original      |
| emotion_label               | Emoción detectada   |
| emotion_score               | Intensidad          |
| stress_level                | alto / medio / bajo |
| sent_pos/neu/neg            | distribución        |
| categories                  | lista JSON          |
| summary                     | resumen automático  |
| suggestion                  | recomendación IA    |
| departamento, equipo, fecha | metadatos           |
| created_at                  | timestamp           |


---

# Uso del Frontend

## Página Pública (Empleados)

**Acceso:** http://localhost:8501

Interfaz simple y anónima donde los empleados pueden:
- Dejar comentarios sobre el ambiente laboral
- Opcional: Especificar departamento y equipo
- Envío confidencial y anónimo
- Sin necesidad de login

## Panel RRHH (Recursos Humanos)

**Acceso:** http://localhost:8502
**Login requerido:** admin / admin123

Páginas disponibles:

1. **Dashboard**: Vista general con KPIs, gráficos de estrés, emociones, tendencias y WordCloud
2. **Análisis Individual**: Búsqueda y filtrado avanzado de comentarios
3. **Análisis CSV**: Carga masiva de comentarios desde archivo CSV
4. **Alertas**: Sistema de detección de patrones críticos y alertas por departamento
5. **Configuración**: Ajustes del sistema y verificación de conexión

---
