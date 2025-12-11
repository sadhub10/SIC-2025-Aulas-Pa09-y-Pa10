# ErgoVision: Asistente de Salud Inteligente 🧘
### Samsung Innovation Campus 2025

> **Desarrollado por:**  
> Equipo BugBusters: Joseph Batista · Juan Castillo · Laura Rivera · Marco Rodríguez  
> © 2025 Samsung Innovation Campus | ErgoVision

---

## 📖 Descripción General

**ErgoVision** es una aplicación web desarrollada en **Python** con **Streamlit** que permite monitorear y corregir la postura corporal y las condiciones de iluminación en tiempo real mediante visión por computadora.

El sistema está dirigido a personas con hábitos sedentarios (estudiantes universitarios, trabajadores de oficina o remotos) que pasan largas jornadas frente a la computadora, ayudándoles a prevenir lesiones musculoesqueléticas y fatiga visual.

El sistema combina tres componentes principales:
1. **Detector de Postura:** analiza el ángulo cervical en tiempo real usando MediaPipe Pose.
2. **Monitor de Iluminación:** evalúa el brillo ambiental para prevenir fatiga visual.
3. **Sistema de Alertas Inteligente:** notifica al usuario sobre posturas incorrectas o baja iluminación de forma personalizable.

La interfaz web integra todas las funcionalidades en una experiencia interactiva, con soporte para dos modos de cámara (lateral y frontal) operando simultáneamente.

---

## 🎯 Planteamiento del Problema

### Problemática Identificada
El trabajo prolongado frente a pantallas genera:
- **Dolores musculoesqueléticos:** cervicales y lumbares por malas posturas sostenidas
- **Fatiga visual:** causada por iluminación inadecuada en el espacio de trabajo
- **Riesgo de lesiones a largo plazo:** síndrome del túnel carpiano, hernias discales, etc.
- **Disminución de productividad:** por molestias físicas durante la jornada laboral

### Datos que Respaldan el Problema
- Potencial reducción de ausentismo laboral por problemas posturales
- Aumento de productividad al minimizar molestias físicas
- Mejora en la calidad de vida y bienestar de usuarios sedentarios

---

## 🎯 Objetivos del Proyecto

### Objetivo Principal
**Reducir en un 30%** el tiempo acumulado de mala postura detectada durante una jornada de 8 horas, en comparación con una sesión sin el asistente.

### Objetivos Específicos
1. **Detección Precisa:** Lograr un error promedio <5° en la medición del ángulo cervical.
2. **Monitoreo Dual:** Implementar detección simultánea en modo lateral y frontal.
3. **Retroalimentación Inmediata:** Alertar al usuario sobre posturas incorrectas en tiempo real.
4. **Análisis de Iluminación:** Evaluar y alertar sobre condiciones de luz inadecuadas.
5. **Accesibilidad:** Ofrecer una solución de bajo costo (solo requiere cámara web estándar).

### Métricas Clave (KPIs)
- Porcentaje de tiempo en "postura mala" vs. "postura buena"
- Número de alertas emitidas y tiempo de respuesta del usuario
- Precisión del sistema: error promedio <5° en detección del ángulo cervical
- Satisfacción del usuario mediante encuestas post-uso

---

## ⚙️ Herramientas Utilizadas

### Frameworks y Librerías Principales
- **[Streamlit](https://streamlit.io) 1.0+:** Framework para la interfaz web interactiva
- **[MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose.html):** Detección de 33 puntos clave del cuerpo humano en tiempo real
- **[OpenCV (cv2)](https://opencv.org):** Procesamiento de video, análisis de imágenes y cálculo de brillo
- **[streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc):** Captura de video en tiempo real vía WebRTC

### Tecnologías Complementarias
- **NumPy:** Cálculos matemáticos, geometría vectorial y procesamiento de arrays
- **Threading:** Manejo concurrente de múltiples cámaras y estados compartidos
- **av (PyAV):** Codificación/decodificación de frames de video

### Algoritmos Implementados

| Algoritmo | Descripción | Uso |
|-----------|-------------|-----|
| **EMA (Exponential Moving Average)** | Suavizado exponencial de mediciones | Estabilizar ángulos y brillo detectados |
| **Detección de ángulos geométricos** | Cálculo trigonométrico entre 3 puntos | Medir inclinación cervical (oreja-hombro-cadera) |
| **Análisis de brillo YCbCr** | Conversión de color y promediado de luminancia | Evaluar iluminación ambiental (0-255) |
| **Sistema de timers acumulativos** | Contadores con cooldown | Evitar notificaciones repetitivas |

---

## 🖥️ Funcionamiento de la Aplicación

La aplicación se ejecuta con el comando:

```bash
streamlit run app.py
```

Una vez iniciada, el programa mostrará la **interfaz web principal**, estructurada de la siguiente manera:

---

### 🧱 1. Encabezado Principal
- Muestra el título del sistema (**Coach de Bienestar – Postura e Iluminación**)
- Descripción: "Dos modos de detección: **Lateral** y **Frontal**"
- Color institucional azul (#1E88E5)
- Visible en todas las secciones del programa

---

### ⚙️ 2. Sidebar (Panel de Configuración)

El panel lateral permite ajustar todos los parámetros del sistema en tiempo real:

#### **Configuración de Iluminación**
| Parámetro | Rango | Valor por defecto | Descripción |
|-----------|-------|-------------------|-------------|
| Umbral de brillo mínimo | 10-120 | 55 | Brillo mínimo recomendado (0-255) |

#### **Configuración de Rendimiento**
| Parámetro | Rango | Valor por defecto | Descripción |
|-----------|-------|-------------------|-------------|
| Procesar cada N cuadros | 1-6 | 1 | Saltar frames para ahorrar CPU |
| Debug overlay | On/Off | On | Mostrar puntos y textos sobre video |

#### **Umbrales de Postura Ajustables**
Define los ángulos del cuello para clasificar **Buena / Regular / Mala**:

**Modo Frontal:**
- Buena postura: ≥ 163.0° (ajustable 150-180°)
- Postura regular: ≥ 159.0° (ajustable 140-179.9°)
- Mala postura: < 159.0°

**Modo Lateral:**
- Buena postura: ≥ 165.0° (ajustable 150-180°)
- Postura regular: ≥ 160.0° (ajustable 140-179.9°)
- Mala postura: < 160.0°

#### **Configuración de Alertas**
| Parámetro | Rango | Valor por defecto | Descripción |
|-----------|-------|-------------------|-------------|
| Activar alertas de postura | On/Off | On | Notificar malas posturas |
| Segundos para alertar (postura) | 3-20s | 6s | Tiempo sostenido antes de alertar |
| Activar alertas de iluminación | On/Off | On | Notificar baja luz |
| Segundos para alertar (luz) | 3-20s | 8s | Tiempo sostenido antes de alertar |
| Cool-down entre alertas | 3-60s | 15s | Tiempo de espera entre notificaciones |

---

### 📷 3. Pestañas de Cámara (Dual-Mode)

La aplicación ofrece **dos modos de detección simultáneos** mediante pestañas:

#### **🔹 Cámara Lateral**
Para detectar la inclinación del cuello de perfil:
- **Posicionamiento:** Coloca la cámara a tu costado (izquierdo o derecho)
- **Detección:** Analiza el triángulo oreja-hombro-cadera
- **Puntos clave:** LEFT_EAR, LEFT_SHOULDER, LEFT_HIP (o RIGHT_*)

#### **🔹 Cámara Frontal**
Para detectar la alineación vertical del cuello:
- **Posicionamiento:** Coloca la cámara frente a ti, a la altura de los ojos
- **Detección:** Analiza el ángulo oreja-hombro respecto a la vertical
- **Puntos clave:** LEFT_EAR, LEFT_SHOULDER, RIGHT_EAR, RIGHT_SHOULDER

---

### 📊 4. Panel de Estado (Tiempo Real)

Cada modo de cámara cuenta con un panel lateral que muestra:

#### **Métricas de Postura**
- **Estado actual:** 🟢 Buena / 🟡 Regular / 🔴 Mala / ⚪ Sin datos
- **Ángulo del cuello:** Valor numérico en grados (ej: 162.4°)
- **Visualización:** Color-coded según clasificación

#### **Métricas de Iluminación**
- **Nivel de brillo:** Valor numérico (0-255)
- **Estado:** 🟢 Buena (≥70) / 🟡 Regular (55-70) / 🔴 Mala (<55)
- **Umbral mínimo:** Recordatorio del valor configurado

#### **Sistema de Alertas Activas**
- ⚠️ **Alerta de postura:** "Mala postura mantenida. Endereza cuello y espalda."
- 💡 **Alerta de iluminación:** "Iluminación insuficiente. Aumenta el nivel de luz."
- **Auto-limpieza:** Las alertas desaparecen tras mantener buena postura/luz por 3 segundos

---

## 🚀 Resultado del Proyecto

### Funcionalidades Implementadas

#### ✅ **1. Detección Dual de Postura**
- **Modo Lateral:** Detecta inclinación mediante ángulo oreja-hombro-cadera
- **Modo Frontal:** Evalúa alineación vertical oreja-hombro
- **Operación simultánea:** Ambos modos funcionan independientemente con estados separados
- **Precisión:** Error promedio de ~3-4° en condiciones óptimas

#### ✅ **2. Sistema de Clasificación Inteligente**
Tres niveles de postura por modo:
- **🟢 Buena:** Ángulo cervical dentro del rango óptimo (≥165° lateral / ≥163° frontal)
- **🟡 Regular:** Ángulo intermedio (160-165° lateral / 159-163° frontal)
- **🔴 Mala:** Ángulo crítico que requiere corrección (<160° lateral / <159° frontal)
- **Umbrales ajustables:** Personalizables desde el sidebar en tiempo real

#### ✅ **3. Monitor de Iluminación Continuo**
- **Análisis de brillo:** Conversión a espacio YCbCr y cálculo de luminancia promedio
- **Escala 0-255:** Medición estándar de brillo digital
- **Clasificación:** Mala (<55), Regular (55-70), Buena (>70)
- **Alertas automáticas:** Cuando la iluminación permanece baja por >8 segundos

#### ✅ **4. Sistema de Alertas Configurable**
- **Timers acumulativos:** Contadores que aumentan/disminuyen según el estado
- **Cool-down inteligente:** Previene spam de notificaciones (15s por defecto)
- **Auto-limpieza:** Alertas se limpian tras mantener buen estado por 3 segundos
- **Notificaciones separadas:** Postura e iluminación independientes

#### ✅ **5. Optimización de Rendimiento**
- **Procesamiento selectivo:** Analiza 1 de cada N frames (configurable 1-6)
- **EMA filtering:** Suavizado exponencial para estabilizar mediciones
- **Threading locks:** Operación concurrente estable sin race conditions
- **Límite de hilos OpenCV:** Reduce carga de CPU (`cv2.setNumThreads(2)`)

#### ✅ **6. Interfaz Web Moderna**
- **Streamlit responsivo:** Layout adaptable a diferentes tamaños de pantalla
- **WebRTC integrado:** Captura de video sin plugins adicionales
- **Debug mode:** Overlay opcional con puntos de detección MediaPipe
- **Configuración en vivo:** Todos los parámetros ajustables sin reiniciar

---

### 📈 Valor Generado

#### **Valor Social**
- ✅ Promueve hábitos saludables en entornos laborales y educativos
- ✅ Reduce el riesgo de lesiones musculoesqueléticas a largo plazo
- ✅ Mejora la calidad de vida y el bienestar de usuarios sedentarios
- ✅ Concientiza sobre la importancia de la ergonomía

#### **Valor Económico**
- 💰 Potencial reducción de ausentismo laboral por problemas posturales
- 💰 Aumento de productividad al minimizar molestias físicas durante la jornada
- 💰 Bajo costo de implementación (solo requiere cámara web estándar)
- 💰 Sin costos recurrentes de suscripción o servidores

#### **Valor Educativo**
- 📚 Proporciona retroalimentación inmediata y personalizada
- 📚 Fomenta el autocuidado mediante datos objetivos en tiempo real
- 📚 Enseña sobre ángulos ergonómicos óptimos de forma práctica

---

## 🔧 Instalación y Uso

### Requisitos del Sistema

- **Python 3.8 o superior**
- **Webcam funcional** (resolución mínima recomendada: 640x480)
- **Conexión a internet** (solo para instalación de dependencias)
- **Sistema operativo:** Windows, macOS o Linux

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/ergovision.git
cd ergovision

# 2. Instalar dependencias
pip install streamlit opencv-python mediapipe numpy streamlit-webrtc av

# O usando requirements.txt
pip install -r requirements.txt
```

### Ejecución

```bash
# Iniciar la aplicación
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

---

### 💡 Guía de Uso Rápido

#### **Para Modo Lateral:**
1. Coloca la cámara **de perfil** (a tu costado izquierdo o derecho)
2. Asegúrate de que tu oreja, hombro y cadera sean visibles
3. Abre la pestaña **"📷 Cámara lateral"**
4. Presiona "Start" en el componente de video
5. Ajusta los umbrales en el sidebar si es necesario

#### **Para Modo Frontal:**
1. Coloca la cámara **frente a ti**, a la altura de los ojos
2. Asegúrate de que tu rostro y hombros sean visibles
3. Abre la pestaña **"🧑‍💻 Cámara frontal"**
4. Presiona "Start" en el componente de video
5. Ajusta los umbrales en el sidebar si es necesario

#### **Recomendaciones Generales:**
- Mantén las alertas activadas durante tu jornada laboral
- Ajusta el umbral de iluminación según la luz natural de tu habitación
- Si recibes muchas alertas falsas, aumenta los segundos requeridos para alertar
- Usa el cool-down para evitar interrupciones constantes

---

## 🔒 Privacidad y Seguridad

ErgoVision está diseñado con **privacidad por defecto**:

- ✅ **Procesamiento 100% local:** Todo el análisis se realiza en tu dispositivo
- ✅ **Sin almacenamiento:** No se guardan videos, imágenes ni capturas
- ✅ **Sin transmisión de datos:** La aplicación no envía información a servidores externos
- ✅ **Sin registro de usuarios:** No requiere cuenta ni inicio de sesión
- ✅ **Control total:** Puedes iniciar/detener la cámara en cualquier momento
- ✅ **Código abierto:** El código fuente es auditable y transparente

---

## 🧠 Arquitectura Técnica

### Flujo de Procesamiento

```
1. Captura de Video (WebRTC)
   ↓
2. Conversión de Frame (BGR → RGB)
   ↓
3. Detección MediaPipe Pose (33 landmarks)
   ↓
4. Cálculo de Ángulos (geometría trigonométrica)
   ↓
5. Suavizado EMA (alpha=0.35)
   ↓
6. Clasificación de Postura (buena/regular/mala)
   ↓
7. Análisis de Brillo (YCbCr + promediado)
   ↓
8. Sistema de Timers (acumulación + cooldown)
   ↓
9. Actualización de UI (Streamlit)
```

---

## 👥 Créditos del Equipo

> **Desarrollado por:**  
> Joseph Batista · Juan Castillo · Laura Rivera · Marco Rodríguez  
> © 2025 Samsung Innovation Campus | ErgoVision

---
