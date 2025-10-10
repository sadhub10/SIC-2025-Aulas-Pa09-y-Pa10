# 🚌 BusPredict – Sistema Inteligente de Predicción de Transporte Público  
### Samsung Innovation Campus 2025 | Universidad Tecnológica de Panamá

> **Desarrollado por:**  
> Juan Castillo · Joseph Batista · Marco Rodríguez · Laura Rivera  
> © 2025 Samsung Innovation Campus | BusPredict UTP

---

## 📖 Descripción general

**BusPredict** es una aplicación desarrollada en **Python** con interfaz gráfica basada en **Tkinter** que permite analizar, visualizar y predecir el comportamiento de rutas de transporte público a partir de datos históricos.  

El sistema combina tres componentes principales:
1. **Analizador Descriptivo:** procesa la información del dataset y genera reportes estadísticos.  
2. **Modelo Predictivo (Headway):** predice intervalos promedio de llegada entre buses.  
3. **Buscador de Rutas:** permite al usuario consultar rutas posibles entre un origen y un destino específico.  

La interfaz gráfica integra todas las funcionalidades en una experiencia interactiva, intuitiva y visualmente agradable.

---

## ⚙️ Requisitos del sistema

- **Python 3.10 o superior**  
- Librerías necesarias:
  ```bash
  pip install pandas matplotlib numpy scikit-learn
  ```
- Archivos de datos:
  - `data/transformed-data/eventos_buses.csv`
  - `data/transformed-data/resumen_eventos.csv`

> 💡 Si los archivos no existen, deben generarse previamente mediante los scripts:
> ```bash
> python scripts/generate_events.py
> python scripts/analyze_dataset.py
> ```

---

## 🧩 Estructura del proyecto

```
BusPredict_SIC2025/
│
├── buspredict/
│   ├── __init__.py
│   ├── analizador.py
│   ├── predictor.py
│   ├── buscador.py
│
├── interfaz/
│   └── ventana_principal.py
│
├── data/
│   └── transformed-data/
│       ├── eventos_buses.csv
│       └── resumen_eventos.csv
│
├── main.py
└── README.md
```

---

## 🖥️ Funcionamiento de la Interfaz Gráfica

La interfaz se ejecuta con el comando:

```bash
python main.py
```

Una vez iniciada, el programa mostrará la **ventana principal**, estructurada de la siguiente manera:

---

### 🧱 1. Encabezado superior
- Muestra el título del sistema (**BusPredict**) y la descripción general.
- Color institucional azul (#283593).
- Visible en todas las secciones del programa.

---

### 📋 2. Menú lateral (navegación principal)

| Botón | Descripción |
|-------|--------------|
| 🏠 **Inicio** | Pantalla de bienvenida e información general. |
| 🔍 **Buscar Ruta** | Permite ingresar origen y destino para encontrar rutas disponibles. |
| 📊 **Análisis del Día** | Despliega métricas y gráficos de comportamiento del sistema en el día actual. |
| ❌ **Salir** | Cierra la aplicación. |

---

### 🔍 3. Buscar Ruta (Origen → Destino)

En esta sección el usuario puede:
1. Introducir un **origen** y **destino**.
2. Pulsar “Buscar Rutas Posibles”.
3. Seleccionar una de las rutas disponibles (se muestran como botones).  

Al seleccionar una ruta:
- El modelo predictivo se entrena automáticamente con los datos de esa ruta.  
- Se muestran los siguientes resultados:
  - **Promedio de intervalos del día.**
  - **Mejor hora** (mínimo tiempo de espera).
  - **Peor hora** (mayor congestión).
  - **Gráfico del intervalo promedio por hora** (línea continua).

El usuario puede volver al menú anterior mediante el botón **⬅ Volver a la búsqueda**.

---

### 📊 4. Análisis del Día

Permite visualizar métricas descriptivas globales del día en curso.  
El usuario elige entre distintas opciones representadas como botones:

| Métrica | Descripción |
|----------|--------------|
| 🏆 **Top 10 rutas más transitadas** | Muestra las rutas con mayor número de pasajeros. |
| ⏱️ **Promedio de intervalos por ruta** | Compara los intervalos medios entre buses en las principales rutas. |
| 🕓 **Distribución de eventos por hora** | Analiza la frecuencia de eventos a lo largo del día. |
| ⚖️ **Rutas con mayor variabilidad** | Identifica las rutas con tiempos de espera más irregulares. |

Cada opción genera una **gráfica individual** en pantalla, acompañada de un botón para volver al menú de métricas.

---

## 🎨 Diseño de la Interfaz

- Basada en **Tkinter**, sin librerías externas de UI.  
- Paleta de colores institucional:  
  - Azul primario `#283593`  
  - Azul secundario `#5C6BC0`  
  - Blanco `#F5F6FA`  
  - Gris claro `#E8EAF6`  
- Estilo tipográfico: *Segoe UI*, con énfasis en legibilidad.  
- Layout adaptable con `pack()` jerárquico y limpieza dinámica mediante `_limpiar_contenido()`.

---

## 🚀 Ejecución del modelo predictivo

El modelo de predicción de intervalos (Headway) se entrena automáticamente cada vez que el usuario selecciona una ruta específica.

El flujo es el siguiente:
1. El usuario selecciona una ruta.  
2. El modelo se entrena usando datos de `eventos_buses.csv`.  
3. Se calculan los intervalos predichos por hora.  
4. Se genera una visualización del comportamiento horario.  

---

## 🧠 Arquitectura modular

| Módulo | Descripción |
|---------|--------------|
| `analizador.py` | Limpieza de datos, agrupaciones, reportes estadísticos y generación de métricas. |
| `predictor.py` | Entrenamiento y evaluación del modelo de predicción de intervalos. |
| `buscador.py` | Filtrado y búsqueda de rutas posibles según origen/destino. |
| `ventana_principal.py` | Control completo de la interfaz gráfica. |
| `main.py` | Punto de entrada del programa, inicializa los módulos y lanza la GUI. |

---

## 🧹 Limpieza dinámica de vistas

Cada sección de la interfaz se actualiza sin abrir nuevas ventanas.  
El método:

```python
def _limpiar_contenido(self):
    for widget in self.content_frame.winfo_children():
        widget.destroy()
```

garantiza que las vistas se actualicen en el mismo contenedor, manteniendo una navegación fluida.

---# 🚌 BusPredict – Sistema Inteligente de Predicción de Transporte Público  
### Samsung Innovation Campus 2025 | Universidad Tecnológica de Panamá

> **Desarrollado por:**  
> Juan Castillo · Joseph Batista · Marco Rodríguez · Laura Rivera  
> © 2025 Samsung Innovation Campus | BusPredict UTP

---

## 📖 Descripción general

**BusPredict** es una aplicación desarrollada en **Python** con interfaz gráfica basada en **Tkinter** que permite analizar, visualizar y predecir el comportamiento de rutas de transporte público a partir de datos históricos.  

El sistema combina tres componentes principales:
1. **Analizador Descriptivo:** procesa la información del dataset y genera reportes estadísticos.  
2. **Modelo Predictivo (Headway):** predice intervalos promedio de llegada entre buses.  
3. **Buscador de Rutas:** permite al usuario consultar rutas posibles entre un origen y un destino específico.  

La interfaz gráfica integra todas las funcionalidades en una experiencia interactiva, intuitiva y visualmente agradable.

---

## ⚙️ Requisitos del sistema

- **Python 3.10 o superior**  
- Librerías necesarias:
  ```bash
  pip install pandas matplotlib numpy scikit-learn
  ```
- Archivos de datos:
  - `data/transformed-data/eventos_buses.csv`
  - `data/transformed-data/resumen_eventos.csv`

> 💡 Si los archivos no existen, deben generarse previamente mediante los scripts:
> ```bash
> python scripts/generate_events.py
> python scripts/analyze_dataset.py
> ```

---

## 🧩 Estructura del proyecto

```
BusPredict_SIC2025/
│
├── buspredict/
│   ├── __init__.py
│   ├── analizador.py
│   ├── predictor.py
│   ├── buscador.py
│
├── interfaz/
│   └── ventana_principal.py
│
├── data/
│   └── transformed-data/
│       ├── eventos_buses.csv
│       └── resumen_eventos.csv
│
├── main.py
└── README.md
```

---

## 🖥️ Funcionamiento de la Interfaz Gráfica

La interfaz se ejecuta con el comando:

```bash
python main.py
```

Una vez iniciada, el programa mostrará la **ventana principal**, estructurada de la siguiente manera:

---

### 🧱 1. Encabezado superior
- Muestra el título del sistema (**BusPredict**) y la descripción general.
- Color institucional azul (#283593).
- Visible en todas las secciones del programa.

---

### 📋 2. Menú lateral (navegación principal)

| Botón | Descripción |
|-------|--------------|
| 🏠 **Inicio** | Pantalla de bienvenida e información general. |
| 🔍 **Buscar Ruta** | Permite ingresar origen y destino para encontrar rutas disponibles. |
| 📊 **Análisis del Día** | Despliega métricas y gráficos de comportamiento del sistema en el día actual. |
| ❌ **Salir** | Cierra la aplicación. |

---

### 🔍 3. Buscar Ruta (Origen → Destino)

En esta sección el usuario puede:
1. Introducir un **origen** y **destino**.
2. Pulsar “Buscar Rutas Posibles”.
3. Seleccionar una de las rutas disponibles (se muestran como botones).  

Al seleccionar una ruta:
- El modelo predictivo se entrena automáticamente con los datos de esa ruta.  
- Se muestran los siguientes resultados:
  - **Promedio de intervalos del día.**
  - **Mejor hora** (mínimo tiempo de espera).
  - **Peor hora** (mayor congestión).
  - **Gráfico del intervalo promedio por hora** (línea continua).

El usuario puede volver al menú anterior mediante el botón **⬅ Volver a la búsqueda**.

---

### 📊 4. Análisis del Día

Permite visualizar métricas descriptivas globales del día en curso.  
El usuario elige entre distintas opciones representadas como botones:

| Métrica | Descripción |
|----------|--------------|
| 🏆 **Top 10 rutas más transitadas** | Muestra las rutas con mayor número de pasajeros. |
| ⏱️ **Promedio de intervalos por ruta** | Compara los intervalos medios entre buses en las principales rutas. |
| 🕓 **Distribución de eventos por hora** | Analiza la frecuencia de eventos a lo largo del día. |
| ⚖️ **Rutas con mayor variabilidad** | Identifica las rutas con tiempos de espera más irregulares. |

Cada opción genera una **gráfica individual** en pantalla, acompañada de un botón para volver al menú de métricas.

---

### 👥 5. Créditos del equipo

> **Desarrollado por:**  
> Juan Castillo · Joseph Batista · Marco Rodríguez · Laura Rivera  
> © 2025 Samsung Innovation Campus | BusPredict UTP

---

## 🎨 Diseño de la Interfaz

- Basada en **Tkinter**, sin librerías externas de UI.  
- Paleta de colores institucional:  
  - Azul primario `#283593`  
  - Azul secundario `#5C6BC0`  
  - Blanco `#F5F6FA`  
  - Gris claro `#E8EAF6`  
- Estilo tipográfico: *Segoe UI*, con énfasis en legibilidad.  
- Layout adaptable con `pack()` jerárquico y limpieza dinámica mediante `_limpiar_contenido()`.

---

## 🚀 Ejecución del modelo predictivo

El modelo de predicción de intervalos (Headway) se entrena automáticamente cada vez que el usuario selecciona una ruta específica.

El flujo es el siguiente:
1. El usuario selecciona una ruta.  
2. El modelo se entrena usando datos de `eventos_buses.csv`.  
3. Se calculan los intervalos predichos por hora.  
4. Se genera una visualización del comportamiento horario.  

---

## 🧠 Arquitectura modular

| Módulo | Descripción |
|---------|--------------|
| `analizador.py` | Limpieza de datos, agrupaciones, reportes estadísticos y generación de métricas. |
| `predictor.py` | Entrenamiento y evaluación del modelo de predicción de intervalos. |
| `buscador.py` | Filtrado y búsqueda de rutas posibles según origen/destino. |
| `ventana_principal.py` | Control completo de la interfaz gráfica. |
| `main.py` | Punto de entrada del programa, inicializa los módulos y lanza la GUI. |

---

## 🧹 Limpieza dinámica de vistas

Cada sección de la interfaz se actualiza sin abrir nuevas ventanas.  
El método:

```python
def _limpiar_contenido(self):
    for widget in self.content_frame.winfo_children():
        widget.destroy()
```

garantiza que las vistas se actualicen en el mismo contenedor, manteniendo una navegación fluida.

---
