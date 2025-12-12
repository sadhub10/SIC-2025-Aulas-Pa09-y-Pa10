# Clasificador de Desechos del Hogar
Aplicación web desarrollada con **Python**, **Streamlit** y **YOLO** para la **clasificación automática de residuos domésticos**, con registro histórico y estadísticas dinámicas.

---

## Descripción del Proyecto
Este proyecto tiene como propósito apoyar iniciativas de gestión de residuos, brindando a los usuarios una herramienta sencilla para:

- Clasificar desechos mediante una imagen o usando la webcam.
- Obtener información relevante sobre cada tipo de desecho.
- Registrar cada clasificación realizada.
- Visualizar estadísticas en tiempo real sobre los desechos detectados.

Está pensado para comunidades, municipios o usuarios individuales que deseen mejorar sus prácticas de separación de basura.

---

## Integrantes del Proyecto

* **Aula:** PA09
* **Nombre del equipo:** 2/3 Coder

### **Integrantes:**

1. Miguel Eduarte
2. Diego Delgado
3. Gino Portacio
4. Ronald Gordon

---

## Características
- Clasificación automática mediante un modelo YOLO entrenado.
- Entrada por:
  - Carga de imagen.
  - Captura desde cámara web.
- Registro de cada clasificación en `records.csv`.
- Gráficos interactivos generados con **Altair**.
- Base de datos local en formato CSV.
- Interfaz amigable desarrollada en **Streamlit**.
- Información ampliada de cada categoría de desecho.

---

## Tecnologías utilizadas
- streamlit
- ultralytics
- Pillow
- numpy
- pandas
- altair
- google-genai
- python-dotenv


---

## Estructura del Proyecto

```
waste-classifier/
│
├── app.py
├── README.md
├── requirements.txt
│
├── models/
│   └── best-classify.pt
│
├── data/
│   ├── categories.json
│   └── records.csv
│
└── utils/
    └── helpers.py
```
---

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/Onigp/waste-detection-system/tree/feature/gemini-analysis
cd waste-classifier
````

### 2. Crear entorno virtual (opcional)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

---

## Archivo de registro: **records.csv**

Cada clasificación se guarda con los siguientes campos:

| Campo      | Descripción                           |
| ---------- | ------------------------------------- |
| timestamp  | Fecha y hora                          |
| source     | Origen de la imagen (upload / webcam) |
| filename   | Nombre o referencia del archivo       |
| class      | Categoría clasificada                 |
| confidence | Nivel de confianza del modelo         |

---

## Archivo **categories.json**

Contiene la información de cada categoría disponible:

```json
{
  "names": ["BIODEGRADABLE", "CARDBOARD", "GLASS", "METAL", "PAPER", "PLASTIC"],
  "info": {
    "BIODEGRADABLE": {
      "description": "Residuos orgánicos que pueden descomponerse naturalmente.",
      "handling": "Recolectar por separado para compostaje.",
      "recyclable": false
    },
    "CARDBOARD": {
      "description": "Cajas y empaques rígidos de cartón.",
      "handling": "Aplanar y mantener seco.",
      "recyclable": true
    }
  }
}
```
