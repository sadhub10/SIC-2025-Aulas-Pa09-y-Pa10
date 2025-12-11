# ErgoVision: Asistente de Salud Inteligente 🧘

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B.svg)](https://streamlit.io)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-00C853.svg)](https://google.github.io/mediapipe/)

## 📋 Descripción del Proyecto

**ErgoVision** es un asistente de bienestar inteligente diseñado para personas con hábitos sedentarios, como estudiantes universitarios y trabajadores de oficina o remotos. El sistema utiliza **visión por computadora en tiempo real** para detectar y corregir malas posturas corporales y condiciones de iluminación deficientes durante largas jornadas frente a la computadora.

### 🎯 Problema que Resuelve

El trabajo prolongado frente a pantallas genera:
- Dolores cervicales y lumbares por malas posturas
- Fatiga visual por iluminación inadecuada
- Riesgo de lesiones musculoesqueléticas a largo plazo
- Disminución de la productividad y bienestar general

### 💡 Solución Propuesta

ErgoVision ofrece monitoreo continuo y retroalimentación en tiempo real mediante:
- **Detección de postura**: Análisis del ángulo cervical en modo lateral y frontal
- **Monitoreo de iluminación**: Evaluación del brillo ambiental para prevenir fatiga visual
- **Alertas personalizables**: Notificaciones configurables cuando se detectan malas posturas o baja iluminación
- **Interfaz intuitiva**: Panel de control visual con métricas en tiempo real

---

## 🎯 Objetivos

### Objetivo Principal
Reducir en un **30%** el tiempo acumulado de mala postura detectada durante una jornada de 8 horas, en comparación con una sesión sin el asistente.

### Objetivos Específicos
1. **Detección precisa**: Lograr un error promedio <5° en la medición del ángulo cervical
2. **Retroalimentación inmediata**: Alertar al usuario en tiempo real sobre posturas incorrectas
3. **Monitoreo de iluminación**: Evaluar y alertar sobre condiciones de luz inadecuadas
4. **Accesibilidad**: Implementar una solución de bajo costo (solo requiere cámara web)

---

## 🛠️ Herramientas y Tecnologías

### Frameworks y Librerías Principales
- **[Streamlit](https://streamlit.io)**: Framework para la interfaz web interactiva
- **[MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose.html)**: Detección de puntos clave del cuerpo humano
- **[OpenCV](https://opencv.org)**: Procesamiento de video y análisis de imágenes
- **[streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc)**: Captura de video en tiempo real vía WebRTC

### Tecnologías Complementarias
- **NumPy**: Cálculos matemáticos y procesamiento de arrays
- **Threading**: Manejo concurrente de múltiples cámaras
- **EMA (Exponential Moving Average)**: Suavizado de mediciones para estabilidad

### Algoritmos Implementados
- **Detección de ángulos**: Cálculo geométrico entre puntos anatómicos (oreja-hombro-cadera)
- **Análisis de brillo**: Conversión a espacio de color YCbCr y promediado de luminancia
- **Sistema de alertas**: Timers acumulativos con cooldown para evitar notificaciones repetitivas

---

## 📊 Resultado del Proyecto

### Funcionalidades Implementadas

#### 1. **Dual-Mode Detection** 📷
- **Modo Lateral**: Detecta inclinación del cuello mediante el análisis del triángulo oreja-hombro-cadera
- **Modo Frontal**: Evalúa la alineación vertical del cuello desde una vista de frente
- Operación simultánea de ambos modos con cámaras independientes

#### 2. **Sistema de Clasificación Inteligente** 🟢🟡🔴
- **Buena postura**: Ángulo cervical ≥ 165° (lateral) / ≥ 163° (frontal)
- **Postura regular**: Ángulo entre 160-165° (lateral) / 159-163° (frontal)
- **Mala postura**: Ángulo < 160° (lateral) / < 159° (frontal)
- Umbrales ajustables en tiempo real desde la interfaz

#### 3. **Monitoreo de Iluminación** 💡
- Análisis continuo del brillo ambiental (escala 0-255)
- Clasificación en tres niveles: Mala (<55), Regular (55-70), Buena (>70)
- Alertas cuando la iluminación permanece baja por más de 8 segundos

#### 4. **Sistema de Alertas Configurable** ⚠️
- Alertas de mala postura tras 6 segundos sostenidos (ajustable 3-20s)
- Cooldown de 15 segundos entre alertas (ajustable 3-60s)
- Auto-limpieza de alertas tras mantener buena postura por 3 segundos
- Notificaciones separadas para postura e iluminación

#### 5. **Optimización de Rendimiento** ⚡
- Procesamiento selectivo de frames (configurable: 1-6 frames)
- Uso de EMAs para suavizado de mediciones
- Threading locks para operación concurrente estable
- Límite de hilos OpenCV para reducir carga de CPU

#### 6. **Panel de Control Interactivo** 🎛️
Sidebar con controles para:
- Umbral de brillo mínimo (10-120)
- Frecuencia de procesamiento de frames
- Umbrales de postura personalizados por modo
- Activación/desactivación de alertas
- Tiempos de espera configurables
- Overlay de puntos de detección (debug mode)

### Métricas de Éxito
- ✅ **Tiempo de respuesta**: <100ms para detección de postura
- ✅ **Precisión angular**: Error promedio de ~3-4° en condiciones óptimas
- ✅ **Estabilidad**: Sistema opera continuamente sin crashes
- ✅ **Usabilidad**: Interfaz intuitiva sin curva de aprendizaje

---

## 🚀 Instalación y Uso

### Requisitos Previos
```bash
Python 3.8 o superior
Webcam funcional
Conexión a internet (para dependencias)
```

### Instalación
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/ergovision.git
cd ergovision

# Instalar dependencias
pip install streamlit opencv-python mediapipe numpy streamlit-webrtc av
```

### Ejecución
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

### Uso Recomendado
1. **Modo Lateral**: Coloca la cámara de perfil a tu costado
2. **Modo Frontal**: Coloca la cámara frente a ti, a la altura de los ojos
3. Ajusta los umbrales en el sidebar según tu comodidad
4. Mantén las alertas activadas durante tu jornada laboral

---

## 📈 Valor Generado

### Social
- ✅ Promueve hábitos saludables en entornos laborales y educativos
- ✅ Reduce el riesgo de lesiones musculoesqueléticas a largo plazo
- ✅ Mejora la calidad de vida de usuarios sedentarios

### Económico
- 💰 Potencial reducción de ausentismo laboral
- 💰 Aumento de productividad al minimizar molestias físicas
- 💰 Bajo costo de implementación (solo requiere webcam)

### Educativo
- 📚 Concientiza sobre la importancia de la ergonomía
- 📚 Proporciona retroalimentación inmediata y personalizada
- 📚 Fomenta el autocuidado mediante datos objetivos

---

## 🔒 Privacidad y Seguridad

- ✅ **Procesamiento local**: Todo el análisis se realiza en el dispositivo del usuario
- ✅ **Sin almacenamiento**: No se guardan ni transmiten videos o imágenes
- ✅ **Sin servidores externos**: La aplicación no envía datos a servicios de terceros
- ✅ **Control total**: El usuario puede iniciar/detener la cámara en cualquier momento

---
---

## 👥 Equipo de Desarrollo

Desarrollado como proyecto de innovación en salud ocupacional.

---
