# Arquitectura del Proyecto 
## Descripción General

El proyecto **Panama Safe - Análisis de Datos Geográficos de Delitos** está diseñado para recopilar, procesar, analizar y visualizar datos geográficos relacionados con delitos en Panamá. La arquitectura se compone de varios módulos que interactúan para ofrecer una solucion democratizada de datos.

## Componentes Principales

### 1. Ingesta de Datos

- **Fuentes:** Archivos CSV, APIs públicas, bases de datos gubernamentales.
- **Herramientas:** Python (pandas, princialmente).
- **Proceso:** Extracción, limpieza y normalización de datos.

### 2. Almacenamiento

- **Base de Datos:** Los datos se encuentran cargados localmente en la aplicacion.

### 3. Procesamiento y Análisis

- **Librerías:** pandas, streamlit, plotly, folium, streamlit-folium, openpyxl, scipy
- **Funcionalidades:** Estadísticas descriptivas, agrupación geográfica, detección de patrones y tendencias.

### 4. Visualización

- **Herramientas:** Matplotlib, Plotly.
- **Salidas:** Mapas interactivos, gráficos de barras, líneas de tiempo.

### 5. Interfaz de Usuario

- **Tipo:** Aplicación web o dashboard interactivo.
- **Características:** Consulta de datos, filtros geográficos y temporales, exportación de resultados.

## Flujo de Datos

1. **Ingesta:** Los datos se obtienen y se almacenan
2. **Procesamiento:** Se realizan análisis y transformaciones sobre los datos.
3. **Visualización:** Los resultados se presentan en mapas y gráficos accesibles desde la interfaz.
4. **Exportación:** Los usuarios pueden descargar reportes y mapas.

## Diagrama de Arquitectura

```mermaid
    A[Ingesta de Datos] --> B[Base de Datos]
    B --> C[Procesamiento y Análisis]
    C --> D[Visualización]
    D --> E[Interfaz de Usuario]
```

## Consideraciones Finales

La arquitectura está diseñada para ser sencilla, flexible y escalable en un futuro. Actualmente consiste en un prototipo pequeño que cumple la funcion de metodo de aprendizaje para el grupo de desarrollo que participo en su desarrollo.