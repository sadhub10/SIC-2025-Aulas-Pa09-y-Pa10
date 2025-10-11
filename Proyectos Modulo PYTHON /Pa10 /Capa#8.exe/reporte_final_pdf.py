# ======================================================
# REPORTE FINAL PDF - PROYECTO MOVILIDAD 4.0
# ======================================================
# Genera un informe profesional con logo, fecha,
# gráficos, tabla y conclusiones dinámicas.
# ======================================================

import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from datetime import datetime
import os

# ------------------------------------------------------
# 1️⃣ Cargar datos
# ------------------------------------------------------
try:
    df_hora = pd.read_csv("estadisticas_por_hora.csv")
    df_ruta = pd.read_csv("estadisticas_por_ruta.csv")
    print("✅ Archivos de estadísticas cargados correctamente.")
except FileNotFoundError:
    print("❌ Faltan archivos de estadísticas. Ejecuta primero 'reporte_estadisticas.py'.")
    exit()

# ------------------------------------------------------
# 2️⃣ Generar gráficos con matplotlib
# ------------------------------------------------------
plt.figure(figsize=(7, 4))
plt.bar(df_hora["Hora"], df_hora["Salidas"], color="#1f77b4")
plt.title("Cantidad de Salidas por Hora")
plt.xlabel("Hora del Día")
plt.ylabel("Cantidad de Salidas")
plt.tight_layout()
plt.savefig("grafico_salidas_hora.png")
plt.close()

plt.figure(figsize=(7, 4))
plt.plot(df_hora["Hora"], df_hora["Demanda_Prom"], marker="o", color="#ff7f0e")
plt.title("Demanda Promedio por Hora")
plt.xlabel("Hora del Día")
plt.ylabel("Demanda Promedio")
plt.grid(True)
plt.tight_layout()
plt.savefig("grafico_demanda_hora.png")
plt.close()

print("📊 Gráficos generados correctamente.")

# ------------------------------------------------------
# 3️⃣ Crear PDF con reportlab
# ------------------------------------------------------
fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
doc = SimpleDocTemplate("Reporte_Final_Movilidad_4.0.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# ------------------------------------------------------
# Portada
# ------------------------------------------------------
if os.path.exists("logo.png"):  # coloca tu logo como 'logo.png' en la carpeta del proyecto
    story.append(Spacer(1, 60))
    story.append(Image("logo.png", width=200, height=200))
else:
    story.append(Spacer(1, 100))
story.append(Spacer(1, 20))
story.append(Paragraph("<b><font size=18 color='#004c6d'>MOVILIDAD 4.0</font></b>", styles["Title"]))
story.append(Spacer(1, 10))
story.append(Paragraph("Sistema de Planificación de Operaciones de Transporte Público", styles["Normal"]))
story.append(Spacer(1, 20))
story.append(Paragraph(f"<i>Fecha de generación del reporte:</i> {fecha_actual}", styles["Normal"]))
story.append(Spacer(1, 100))

# ------------------------------------------------------
# Gráficos
# ------------------------------------------------------
story.append(Paragraph("<b>1. Distribución de Salidas por Hora</b>", styles["Heading2"]))
story.append(Spacer(1, 6))
story.append(Image("grafico_salidas_hora.png", width=400, height=250))
story.append(Spacer(1, 12))

story.append(Paragraph("<b>2. Demanda Promedio por Hora</b>", styles["Heading2"]))
story.append(Spacer(1, 6))
story.append(Image("grafico_demanda_hora.png", width=400, height=250))
story.append(Spacer(1, 12))

# ------------------------------------------------------
# Tabla de estadísticas
# ------------------------------------------------------
story.append(Paragraph("<b>3. Estadísticas Generales por Ruta</b>", styles["Heading2"]))
story.append(Spacer(1, 6))

tabla_ruta = [df_ruta.columns.to_list()] + df_ruta.values.tolist()
t = Table(tabla_ruta, hAlign='CENTER')
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004c6d")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 10),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f7")]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
]))
story.append(t)
story.append(Spacer(1, 20))

# ------------------------------------------------------
# 4️⃣ Conclusión dinámica
# ------------------------------------------------------
demanda_prom = float(df_ruta["Demanda_Prom"].mean())
frecuencia_prom = float(df_ruta["Frecuencia_Prom"].mean())

if demanda_prom > 0.8:
    conclusion = """
El sistema muestra una <b>alta demanda</b> sostenida a lo largo del día, lo que sugiere la necesidad de incrementar
la flota operativa o reducir los intervalos de salida. La infraestructura actual responde bien a las horas pico,
pero se recomienda aumentar la capacidad en los tramos de mayor tráfico.
"""
elif demanda_prom >= 0.6:
    conclusion = """
La demanda promedio es <b>moderada</b>, lo que indica una buena distribución de pasajeros a lo largo de las rutas.
El sistema mantiene una frecuencia estable y una cobertura adecuada, con posibilidad de ajustes menores
en horarios o asignación de unidades para mejorar la eficiencia.
"""
else:
    conclusion = """
El sistema evidencia una <b>baja demanda</b> general, lo que sugiere optimizar las frecuencias o
reasignar autobuses para evitar tiempos muertos. Se recomienda analizar las zonas con menor tráfico
para equilibrar la oferta con la demanda real.
"""

story.append(Paragraph("<b>4. Conclusiones</b>", styles["Heading2"]))
story.append(Spacer(1, 6))
story.append(Paragraph(conclusion, styles["Normal"]))
story.append(Spacer(1, 20))

story.append(Paragraph(
    "<b>Reporte generado automáticamente con Python, pandas, matplotlib y reportlab.</b>",
    ParagraphStyle('ItalicStyle', parent=styles['Normal'], fontName='Helvetica-Oblique')
))

# ------------------------------------------------------
# Exportar PDF
# ------------------------------------------------------
doc.build(story)
print("✅ Reporte PDF generado exitosamente: 'Reporte_Final_Movilidad_4.0.pdf'")
