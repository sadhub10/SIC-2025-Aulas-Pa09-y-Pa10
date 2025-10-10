# Asistente Digital para Agricultores Panameños

**Equipo:** Pandas con Flow  
**Autores:** Kelvin He, Jean Gómez, Jorge Rodríguez, Oriel Pinilla

## Planteamiento del Problema

Los pequeños productores agrícolas de Panamá enfrentan desafíos significativos para optimizar sus cultivos debido a:

-   **Falta de acceso** a información técnica actualizada
-   **Dificultad para interpretar** datos climáticos complejos
-   **Ausencia de herramientas** para planificación de siembra
-   **Limitado conocimiento** sobre períodos óptimos de cultivo
-   **Riesgos climáticos** no identificados oportunamente

**Impacto:** Reducción de rendimientos, pérdidas económicas y uso ineficiente de recursos naturales.

## Objetivos del Proyecto

### Objetivo General

Desarrollar un sistema modular de asistencia técnica que proporcione a los agricultores panameños herramientas digitales para tomar decisiones informadas sobre cultivos, basándose en datos científicos y climáticos.

### Objetivos Específicos

-   **Integrar datos climáticos** en tiempo real mediante API especializada
-   **Analizar y visualizar** información técnica de 25 cultivos panameños
-   **Generar recomendaciones** personalizadas según condiciones actuales
-   **Proporcionar interfaz intuitiva** para usuarios sin experiencia técnica
-   **Facilitar exportación** de reportes y análisis en múltiples formatos

## Herramientas y Tecnologías Utilizadas

### Stack Tecnológico Principal

-   **Lenguaje:** Python 3.11+
-   **Framework GUI:** Tkinter (Interfaz gráfica nativa)
-   **Análisis de Datos:** Pandas (Manipulación de datasets)
-   **Visualización:** Matplotlib (Gráficos científicos)
-   **Integración API:** Requests (Datos climáticos)
-   **Configuración:** python-dotenv (Variables de entorno)

### APIs y Servicios Externos

-   **OpenWeatherMap API:** Datos climáticos en tiempo real
-   **Dataset personalizado:** 25 cultivos panameños con información técnica

### Arquitectura Modular

```
Asistente_Agricultor/
├── asistente_agricola_modular.py  # Aplicación principal
├── dataset_cultivos_panama.csv    # Base de datos de cultivos
├── requirements.txt               # Dependencias del proyecto
├── .env                          # Variables de entorno
├── README.md                     # Documentación
└── modulos/                      # Módulos del sistema
    ├── __init__.py               # Inicializador de módulos
    ├── datos.py                  # Gestión de dataset
    ├── graficos.py               # Visualizaciones
    ├── clima.py                  # Integración API climática
    └── interfaz.py               # Interfaz de usuario
```

## Estructura del Proyecto

### Archivo Principal

-   **`asistente_agricola_modular.py`:** Clase principal que coordina todos los módulos y gestiona la aplicación completa.

### Módulos del Sistema

#### `modulos/datos.py` - DatosManager

**Función:** Gestión completa del dataset de cultivos panameños

-   Carga y limpieza de datos del CSV
-   Búsqueda inteligente con sugerencias automáticas
-   Análisis estadístico y comparativo entre cultivos
-   Exportación de reportes en CSV y PDF
-   Validación y normalización de datos

#### `modulos/graficos.py` - GraficosManager

**Función:** Creación de visualizaciones científicas personalizadas

-   Gráficos de barras para rendimientos por cultivo
-   Gráficos de líneas para temporadas de siembra
-   Gráficos circulares para distribución de lluvias
-   Gráficos de dispersión para análisis de correlaciones
-   Exportación de imágenes en alta calidad

#### `modulos/clima.py` - ClimaManager

**Función:** Integración con servicios climáticos externos

-   Conexión con OpenWeatherMap API
-   Obtención de datos climáticos actualizados
-   Verificación de compatibilidad cultivo-clima
-   Generación de alertas climáticas personalizadas
-   Manejo de errores de conectividad

#### `modulos/interfaz.py` - InterfazManager

**Función:** Diseño de experiencia de usuario intuitiva

-   Interfaz gráfica amigable para agricultores
-   Navegación simplificada y accesible
-   Formularios de búsqueda con validación
-   Presentación clara de resultados
-   Sistema de ayuda y guías integradas

## Configuración e Instalación

### 1. Requisitos del Sistema

```
Python 3.8 o superior
Sistema Operativo: Windows, Linux, macOS
Conexión a Internet (para datos climáticos)
```

### 2. Crear Entorno Virtual (Recomendado)

#### Crear el entorno virtual:

```bash
python -m venv .venv
```

#### Activar el entorno virtual:

**Windows (Command Prompt):**

```cmd
.venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows/Linux/macOS (Bash/Terminal):**

```bash
source .venv/bin/activate
```

**Git Bash (Windows):**

```bash
source .venv/Scripts/activate
```

### 3. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configuración de API Climática

Crear archivo `.env` en la raíz del proyecto:

```bash
# Configuración del Asistente Agrícola
OPENWEATHER_API_KEY=tu_api_key_aqui
```

**Obtener API Key:**

1. Registrarse en [OpenWeatherMap](https://openweathermap.org/api)
2. Obtener API key gratuita
3. Reemplazar `tu_api_key_aqui` con tu clave personal

### 5. Ejecución del Sistema

```bash
python asistente_agricola_modular.py
```

## Resultados del Proyecto

### Funcionalidades Implementadas

-   **Sistema completamente funcional** con arquitectura modular
-   **Base de datos integrada** con 25 cultivos panameños
-   **Interfaz gráfica intuitiva** desarrollada con Tkinter
-   **Integración API climática** con datos en tiempo real
-   **Visualizaciones dinámicas** con 4 tipos de gráficos por cultivo
-   **Exportación de reportes** en múltiples formatos
-   **Sistema de búsqueda inteligente** con sugerencias automáticas

### Cultivos Disponibles en el Sistema

El sistema incluye información técnica completa de **25 cultivos** organizados por categorías:

**Granos Básicos:** Arroz, Maíz, Frijol, Sorgo  
**Tubérculos:** Yuca, Ñame, Ñampí, Papa  
**Plátanos:** Plátano, Banano  
**Frutas:** Naranja, Limón, Mango, Papaya, Piña, Aguacate, Coco  
**Hortalizas:** Tomate, Cebolla, Pimiento, Lechuga, Repollo  
**Cultivos Especiales:** Café, Cacao, Caña de Azúcar

### Impacto Esperado

-   **Valor Social:** Democratización del acceso a información técnica agrícola
-   **Mejora de Rendimientos:** 15-20% de optimización en producción
-   **Reducción de Pérdidas:** Minimización de riesgos por decisiones incorrectas
-   **Inclusión Tecnológica:** Capacitación digital para comunidades rurales
-   **Sostenibilidad:** Uso más eficiente de recursos naturales

## Equipo de Desarrollo

| Integrante          | Rol Principal                    | Responsabilidades                          |
| ------------------- | -------------------------------- | ------------------------------------------ |
| **Kelvin He**       | Líder de Desarrollo Backend      | Módulo de datos, algoritmos de búsqueda    |
| **Jean Gómez**      | Especialista en Visualización    | Módulo de gráficos, reportes científicos   |
| **Jorge Rodríguez** | Desarrollador de Integración API | Módulo climático, servicios externos       |
| **Oriel Pinilla**   | Diseñador de Interfaz UX/UI      | Módulo de interfaz, experiencia de usuario |

## Proyección y Escalabilidad

### Próximas Funcionalidades

-   **Versión móvil** para mayor accesibilidad
-   **Integración con Machine Learning** para predicciones avanzadas
-   **Versión web** con acceso desde cualquier navegador
-   **Integración IoT** para sensores de campo
-   **Expansión geográfica** a Centroamérica

### Colaboraciones Futuras

-   **MIDA (Ministerio de Desarrollo Agropecuario)**
-   **Universidades panameñas**
-   **Cooperativas agrícolas**
-   **Organizaciones internacionales**

## Licencia y Contribuciones

Este proyecto está desarrollado con fines educativos y de impacto social. Las contribuciones y mejoras son bienvenidas para fortalecer el apoyo a la agricultura panameña.

---

**Contacto del Equipo:** Pandas con Flow  
**Fecha de Desarrollo:** 2025  
**Institución:** Samsung Innovation Campus
