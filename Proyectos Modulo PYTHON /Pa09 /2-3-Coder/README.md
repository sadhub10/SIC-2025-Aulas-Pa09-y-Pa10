# 🛡️ Vulnescan: Escáner de Seguridad Web

Este proyecto fue desarrollado como una herramienta de **análisis de seguridad web**, que permite visualizar los resultados del escaneo de vulnerabilidades a través de gráficos y tablas.

Su objetivo es brindar la **capacidad** al usuario de **determinar** si una web tiene **vulnerabilidades** y transformar reportes técnicos en **insights visuales**, ayudando a los usuarios a **identificar si sus datos estan seguros** de manera efectiva.

---

## 👥 Integrantes del Proyecto

* **Aula:** PA09
* **Nombre del equipo:** 2/3 Coder

### **Integrantes:**

1. Miguel Eduarte
2. Diego Delgado
3. Gino Portacio
4. Ronald Gordon
5. Jean Rodríguez

---

## 🚀 Introducción

El **Vulnescan** es una herramienta desarrollada en **Python y Streamlit** que permite analizar webs y generar reportes de seguridad de forma visual.
El sistema carga muestra detalles de los reportes generados como:

* Total de hallazgos detectados
* Distribución por nivel de severidad (Alta, Media, Baja, Informativa)
* Historial de reportes y tendencias
* Exportación de resultados a CSV

---

## 🧠 Objetivos

* Analizar vulnerabilidades web.
* Mostrar métricas.
* Permitir la exportación de reportes.
* Proveer una herramienta amigable para usuarios no técnicos.

---

## 🧰 Herramientas y Librerías

### **Librerías principales:**

* **Streamlit** 🧩 – Framework de código abierto en Python diseñado para crear aplicaciones web interactivas de análisis de datos.
* **Pandas** 📊 – Librería fundamental para la manipulación y el análisis de datos estructurados.
* **Altair** 📈 – Librería declarativa para la visualización estadística de datos en Python.
* **Requests** 🌐 – Permite enviar solicitudes a servidores web (como GET, POST, PUT, DELETE) y recibir sus respuestas de forma sencilla y legible.

---

## 📁 Estructura del Proyecto

```text
Vulnescan/
├── Reportes/                     # Almacenamiento de reportes de escaneos
│   ├── reportes.csv              # Archivos de reportes en formato CSV
├── diccionario.py            # Diccionario de vulnerabilidades
├── csv_generador.py               # generador de archivos CSV
├── scanner.py                 # Funciones principales de escaneo web
├── dashboard.py              # Interfaz visual con Streamlit
├── requirements.txt              # Dependencias del proyecto
└── README.md                     # Documentación principal
```

---

## ⚙️ Instalación y Uso

### 1️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Ejecutar la aplicación

```bash
streamlit run dashboard.py
```

## 🔒 Futuras mejoras

* Implementación de autenticación de usuarios.
* Integración con APIs de escaneo automático.
* Alertas por correo ante detección de vulnerabilidades críticas.
* Exportación avanzada en formato PDF.

---
