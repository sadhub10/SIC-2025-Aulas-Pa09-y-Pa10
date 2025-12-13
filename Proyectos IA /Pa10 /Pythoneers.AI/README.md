Sistema de Monitoreo Ambiental — Instalación

Repositorio con pipelines para ingerir y procesar datos climáticos (IMHPA, ETESA), enriquecimiento geoespacial y utilidades relacionadas.

# Sistema de Monitoreo Ambiental — Instalación

> Repositorio con pipelines para ingerir y procesar datos climáticos (IMHPA, ETESA), enriquecimiento geoespacial y utilidades relacionadas.

## Instalación (pip / venv)

1. Crear y activar el virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias runtime:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. (Opcional) Instalar dependencias de desarrollo / notebooks:

```bash
python -m pip install -r requirements-dev.txt
```

> Nota: si usas `conda`, puedes crear un entorno desde `conda-forge` y evitar problemas con compilación de librerías geoespaciales.

## Variables de entorno
Puedes colocar variables en un fichero `.env` en la raíz. Ejemplos útiles:


## Ejecutar tests

Desde la raíz del repo (con `.venv` activado):

```bash
PYTHONPATH=. pytest -q
```

Si tus imports fallan por `ModuleNotFoundError: pipelines`, asegúrate de ejecutar con `PYTHONPATH=.`, o lanzar el runner con `python -m pipelines.pipeline_runner`.

## Ejecutar los pipelines

Menú interactivo (recomendado para desarrollo):

```bash
python -m pipelines.pipeline_runner
```

Ejecutar todo programáticamente:

```bash
python -c "import pipelines.pipeline_runner as pr; pr.run_all_pipelines()"
```

Ejecutar un pipeline concreto (ejemplo IMHPA realtime):

```bash
python -m pipelines.imhpa.realtime_temp
```

## Estructura de datos en disco

Los módulos que escriben datos se encargan de crear sus carpetas con `os.makedirs(..., exist_ok=True)`. Además, el `pipeline_runner` crea las carpetas base al iniciar la ejecución completa.

## Notas sobre problemas comunes

## Contribuir


Si quieres, puedo añadir una sección de `environment.yml` (conda) o un README en inglés.

Sistema de Monitoreo Ambiental — Instalación

Este repositorio contiene pipelines para ingerir y procesar datos climáticos (IMHPA, ETESA), enriquecimiento geoespacial y utilidades relacionadas.

## Requisitos previos
- macOS / Linux / Windows con Python 3.10+ (se probó con 3.11/3.12).
- Recomiendo usar un entorno virtual (`venv`) o `conda`/`mamba` para aislar dependencias.
- Dependencias nativas para `geopandas` / `osmnx`: GDAL, Fiona, PROJ, GEOS. En macOS puedes instalarlas con `brew` o usar conda-forge para evitar compilaciones.

Ejemplos (macOS):

```bash
# brew (si no usas conda)
brew install gdal proj

# o conda (recomendado para reproducibilidad geoespacial)
conda create -n sm_env python=3.11 -y
conda activate sm_env
conda install -c conda-forge geopandas osmnx jupyterlab -y
```

## Instalación (pip / venv)

1. Crear y activar el virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias runtime:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. (Opcional) Instalar dependencias de desarrollo / notebooks:

```bash
python -m pip install -r requirements-dev.txt
```

Nota: si usas `conda`, puedes omitir el paso `brew` y crear un `environment.yml` a partir de `requirements.txt` si lo deseas.

## Variables de entorno
Puedes colocar variables en un fichero `.env` en la raíz. Ejemplos útiles:

- `DATA_RAW_PATH` — ruta raíz para datos crudos (por defecto `data_raw`)
- `IMHPA_MAX_WORKERS` — número de hilos para procesar estaciones IMHPA (por defecto `8`)
- `TERRAIN_MAX_WORKERS` — hilos para enriquecimiento de terreno
- `OSM_TILE_KM` y `OSM_MAX_WORKERS` — controlan el tiling y concurrencia en descargas OSM

## Ejecutar tests

Desde la raíz del repo (con `.venv` activado):

```bash
PYTHONPATH=. pytest -q
```

Si tus imports fallan por `ModuleNotFoundError: pipelines`, asegúrate de ejecutar con `PYTHONPATH=.` o de lanzar el runner con `python -m pipelines.pipeline_runner`.

## Ejecutar los pipelines

Menú interactivo (recomendado para desarrollo):

```bash
python -m pipelines.pipeline_runner
```

Ejecutar todo programáticamente:

```bash
python -c "import pipelines.pipeline_runner as pr; pr.run_all_pipelines()"
```

Algunos pipelines individuales también se pueden ejecutar directamente (por ejemplo IMHPA realtime):

```bash
python -m pipelines.imhpa.realtime_temp
```

## Estructura de datos en disco
- `data_raw/` — datos crudos y caches (ej.: `data_raw/imhpa`, `data_raw/etesa`, `data_raw/osm`)
- `data_clean/` — salidas limpias y datasets intermedios (ej.: `data_clean/imhpa`, `data_clean/master`)

Los módulos que escriben datos se encargan de crear sus carpetas con `os.makedirs(..., exist_ok=True)`. Además, el `pipeline_runner` crea las carpetas base al iniciar la ejecución completa.

## Notas sobre problemas comunes
- Geopandas/osmnx: si la instalación falla por dependencias nativas, usa conda-forge o instala `gdal`/`proj` vía `brew`.
- Overpass / OSM: el downloader tiene mecanimos de cache en `data_raw/osm` y descarga por tiles para evitar consultas demasiado grandes.
- Si tienes problemas con permisos al crear carpetas, revisa permisos del directorio de trabajo o ejecuta con un usuario con permisos adecuados.

## Contribuir
- Abrir issues para bugs o mejoras.
- Para cambios grandes, crear una rama y enviar un pull request.

---

## 🧪 Ejecución de Notebooks (Flujo de trabajo)

Esta sección describe el orden recomendado para ejecutar los notebooks del proyecto, una vez que los pipelines ya han sido ejecutados correctamente.

⚠️ Importante: Todos los notebooks dependen de los datasets generados en la carpeta data_clean/.
Primero deben ejecutarse los pipelines.

## 🔹 Paso 1: Ejecutar el pipeline principal

Ejecuta el pipeline que contiene toda la ingesta y procesamiento de datos climáticos (IMHPA / ETESA):

python -m pipelines.pipeline_runner


Selecciona la opción para ejecutar todos los pipelines

Espera a que el proceso termine completamente

Este paso genera los datasets limpios en data_clean/

## 🔹 Paso 2: Limpieza y validación de datos

Luego de que el pipeline finaliza, abre el notebook encargado de la limpieza y validación:

📓 Notebook:

data_clean.ipynb (o equivalente)

En este notebook:

Se revisa la data generada

Se limpian valores nulos o inconsistentes

Se consolida el dataset final que usarán los análisis posteriores

## 🔹 Paso 3: Análisis y visualización IMHPA

Después, ejecuta el notebook de análisis exploratorio:

📓 Notebook:

analisis_imhpa.ipynb

Aquí se realiza:

Visualización de datos climáticos

Análisis por estación

Exploración de tendencias históricas

## 🔹 Paso 4: Series de tiempo y mapas climáticos

Ejecuta el notebook de series de tiempo y mapas:

📓 Notebook:

serie_de_tiempo.ipynb

Este notebook:

Carga automáticamente el dataset limpio desde data_clean/

Muestra mapas climáticos para el año 2025

Incluye la simulación climática para 2026

Genera mapas interactivos con Folium

## 🔹 Paso 5: Entrenamiento y visualización de modelos

Finalmente, ejecuta el notebook donde se entrenan y visualizan los modelos de Machine Learning:

📓 Notebook:

train_and_visualise.ipynb

En este notebook:

Se entrenan los modelos de sequías y inundaciones

Se usan algoritmos de Machine Learning

Se visualizan resultados y métricas

Se generan los modelos finales utilizados por el sistema

## para resumir el flujo de ejecuciones 
Ejecutar pipelines 1

Ejecutar análisis IMHPA

Ejecutar notebook de limpieza (data_clean)

Ejecutar series de tiempo y mapas (2025 / 2026)

Ejecutar entrenamiento de modelos (sequías e inundaciones)
