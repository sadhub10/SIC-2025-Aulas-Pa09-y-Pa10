# MAC – Motor de Análisis de Correlación (Artritis Reumatoide)

Aplicación de escritorio en **Python + Tkinter** para registrar **síntomas diarios** de Artritis Reumatoide (AR) y descubrir **relaciones** con factores de **estilo de vida** y **ambiente** (sueño, dieta, clima, actividad física).  
Cada usuario tiene **su perfil** y **su propio CSV** con registros. Incluye **simulación de datos** realistas para aprender el flujo desde el primer uso.

>  Esta app **no diagnostica ni receta**. Solo muestra **asociaciones** (correlación) para apoyar el autocuidado y la conversación con el equipo de salud. **Correlación ≠ causalidad.**

---

## Planteamiento 

- La AR puede aparecer a **cualquier edad** y sus síntomas (dolor, rigidez, inflamación, fatiga) **varían entre personas**.  
- Los médicos piden llevar un **diario** (qué duele, cuánto, clima, sueño, dieta, actividad), pero:
  - Es **difícil** mantenerlo a diario.
  - Casi nunca se **analiza** para encontrar **patrones personales**.
- **Necesidad:** una herramienta **simple** que permita **registrar** rápido y **visualizar** cómo los factores cotidianos se **relacionan** con los síntomas, * y con **explicaciones claras**.

---

## Objetivos

**Objetivo general**  
Facilitar el **registro diario** y la **interpretación** de los síntomas y factores personales en AR para apoyar el **autocuidado** y la **conversación** con el equipo de salud.

**Objetivos específicos**
1. Permitir un **registro simple** (0–5) de dolor, rigidez, inflamación y fatiga, junto con **sueño**, **dieta**, **clima**, **temperatura**, **actividad** y **ánimo**.
2. Guardar la **información por usuario** (perfil en `data/usuarios.json` y registros en `data/{usuario}_registros.csv`).
- **Enfoque cuantitativo + visual** con **retroalimentación personalizada** basada en tu **registro diario**, y **gráficas clínicas interpretables** para paciente y reumatólogo.

3. Calcular y mostrar **correlaciones** (Pearson), **prueba t** (clima adverso vs dolor) y un índice **ISA** (promedio de síntomas).
4. **Visualizar** resultados con gráficos y **mensajes interpretables**
5. Incluir **simulación de datos** realistas para aprender el uso desde el primer día.

---

##Herramientas utilizadas

- **Python 3**
- **Tkinter** (interfaz de escritorio)
- **Pandas** (carga, limpieza, análisis)
- **NumPy** (simulación y operaciones numéricas)
- **Matplotlib** y **Seaborn** (gráficos)
- **SciPy** (prueba t)
- **CSV/JSON** para persistencia por usuario (simple y entendible)

---
## Resultados del sistema

A partir de tus **registros diarios** (y/o del **dataset simulado**) el sistema genera:

- **Promedios e ISA (Índice de Síntomas Agregados)**  
  - Promedio de **dolor, rigidez, inflamación, fatiga** (escala 0–5).  
  - **ISA = promedio** de esos cuatro síntomas → visión rápida de tu **malestar general**.

- **Matriz de correlaciones (Pearson)**  
  - Mide la **asociación** entre variables (de –1 a +1).  
  - **+**: aumentan juntas. **–**: cuando una sube, la otra baja.  
  - **Fuerte**: |r| ≥ 0.7; **Moderada**: 0.5–0.69; **Débil**: 0.3–0.49.

- **Sueño (día anterior) → Fatiga (día siguiente)**  
  - Correlación con **desfase de 1 día**: mejor sueño ayer suele asociarse con **menos fatiga** hoy.

- **Clima adverso vs Dolor (prueba t)**  
  - Compara el **dolor** en días **lluviosos/húmedos** vs el resto.  
  - Reporta **p-valor**:  
    - **p < 0.05** → diferencia **estadísticamente significativa**.  
    - **p ≥ 0.05** → no se puede afirmar diferencia con evidencia suficiente.

- **Dieta vs Dolor**  
  - Dolor **promedio** por tipo de dieta (**Antiinflamatoria**, **Balanceada**, **Inflamatoria**).  
  - Esperable: **Antiinflamatoria ≤ Balanceada ≤ Inflamatoria**.


- **Top 5 variables más relacionadas con el dolor**  
  - Barras con las **asociaciones más fuertes** (positivas o negativas).

- **Tendencia mensual del ISA**  
  - Promedio de **ISA por mes** para ver si **mejoras** o **empeoras**.


- **Retroalimentación personalizada**  
  - Mensajes automáticos al **guardar un registro** (ej.: síntomas altos → descansa; sueño pobre → prioriza higiene del sueño; clima húmedo → abrígate y estira; dieta inflamatoria → ajusta alimentos; sin actividad y síntomas bajos → caminar suave, etc.).

**Archivos generados (persistencia por usuario)**
- `data/usuarios.json` → Guarda **perfiles** (se actualiza al registrarte/editar).  
- `data/{usuario}_registros.csv` → Guarda **tus registros diarios** (se crea al primer guardado).

**Importante:** los resultados muestran **asociaciones**, no causas. Sirven para **aprender tus patrones** y conversar con tu **reumatólogo**.
