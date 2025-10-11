# ======================================================
# INTERFAZ GRÁFICA DEL SISTEMA MOVILIDAD 4.0
# ======================================================
# Permite seleccionar una ruta y visualizar reportes
# dinámicos con gráficos y estadísticas.
# ======================================================

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ------------------------------------------------------
# 1️⃣ Cargar datos base
# ------------------------------------------------------
try:
    df_hora = pd.read_csv("estadisticas_por_hora.csv")
    df_ruta = pd.read_csv("estadisticas_por_ruta.csv")
except FileNotFoundError:
    messagebox.showerror("Error", "No se encontraron los archivos de estadísticas.\nEjecuta primero reporte_estadisticas.py.")
    exit()

# Obtener lista de rutas disponibles
rutas_disponibles = df_ruta["Ruta"].unique().tolist()

# ------------------------------------------------------
# 2️⃣ Crear ventana principal
# ------------------------------------------------------
root = tk.Tk()
root.title("Movilidad 4.0 - Reportes de Transporte Público")
root.geometry("950x650")
root.configure(bg="#f5f6fa")

# ------------------------------------------------------
# 3️⃣ Encabezado
# ------------------------------------------------------
titulo = tk.Label(root, text="MOVILIDAD 4.0", font=("Helvetica", 20, "bold"), fg="#004c6d", bg="#f5f6fa")
titulo.pack(pady=10)

subtitulo = tk.Label(root, text="Sistema de Planificación de Operaciones de Transporte", font=("Arial", 12), bg="#f5f6fa")
subtitulo.pack()

# ------------------------------------------------------
# 4️⃣ Menú desplegable (Dropdown)
# ------------------------------------------------------
frame_seleccion = tk.Frame(root, bg="#f5f6fa")
frame_seleccion.pack(pady=10)

tk.Label(frame_seleccion, text="Seleccionar Ruta:", bg="#f5f6fa", font=("Arial", 11)).grid(row=0, column=0, padx=5)

ruta_seleccionada = tk.StringVar(value=rutas_disponibles[0])
dropdown = ttk.Combobox(frame_seleccion, textvariable=ruta_seleccionada, values=rutas_disponibles, state="readonly", width=15)
dropdown.grid(row=0, column=1, padx=5)

# ------------------------------------------------------
# 5️⃣ Contenedor para gráficos y datos
# ------------------------------------------------------
frame_contenido = tk.Frame(root, bg="#f5f6fa")
frame_contenido.pack(pady=10, fill="both", expand=True)

frame_grafico = tk.Frame(frame_contenido, bg="#f5f6fa")
frame_grafico.pack(side="left", fill="both", expand=True)

frame_info = tk.Frame(frame_contenido, bg="#f5f6fa")
frame_info.pack(side="right", fill="y", padx=20)

# ------------------------------------------------------
# 6️⃣ Función para generar reportes dinámicos
# ------------------------------------------------------
def generar_reporte():
    ruta = ruta_seleccionada.get()
    datos_ruta = df_ruta[df_ruta["Ruta"] == ruta].iloc[0]
    
    # --- Limpiar gráficos previos ---
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    # --- Datos de la ruta ---
    duracion_prom = datos_ruta["Duracion_Prom"]
    demanda_prom = datos_ruta["Demanda_Prom"]
    freq_prom = datos_ruta["Frecuencia_Prom"]

    # --- Subset de horas ---
    datos_hora = df_hora.copy()

    # --- Gráfico 1: Salidas por hora ---
    fig, ax = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
    ax[0].bar(datos_hora["Hora"], datos_hora["Salidas"], color="#1f77b4")
    ax[0].set_title("Salidas por Hora")
    ax[0].set_xlabel("Hora")
    ax[0].set_ylabel("Cantidad")

    # --- Gráfico 2: Demanda promedio ---
    ax[1].plot(datos_hora["Hora"], datos_hora["Demanda_Prom"], marker="o", color="#ff7f0e")
    ax[1].set_title("Demanda Promedio por Hora")
    ax[1].set_xlabel("Hora")
    ax[1].set_ylabel("Demanda Prom.")

    plt.tight_layout()

    # Integrar gráfico en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # --- Mostrar resumen ---
    for widget in frame_info.winfo_children():
        widget.destroy()

    tk.Label(frame_info, text=f"📍 Ruta: {ruta}", bg="#f5f6fa", font=("Arial", 12, "bold"), fg="#004c6d").pack(anchor="w", pady=5)
    tk.Label(frame_info, text=f"🚌 Salidas Totales: {int(datos_ruta['Total_Salidas'])}", bg="#f5f6fa").pack(anchor="w")
    tk.Label(frame_info, text=f"📈 Demanda Promedio: {demanda_prom:.2f}", bg="#f5f6fa").pack(anchor="w")
    tk.Label(frame_info, text=f"⏱️ Duración Promedio: {duracion_prom:.2f} min", bg="#f5f6fa").pack(anchor="w")
    tk.Label(frame_info, text=f"⏳ Frecuencia Promedio: {freq_prom:.2f} min", bg="#f5f6fa").pack(anchor="w")
    
    # Conclusión dinámica
    if demanda_prom > 0.8:
        conclusion = "Demanda alta detectada. Se recomienda aumentar la frecuencia o la flota en horas pico."
    elif demanda_prom >= 0.6:
        conclusion = "Demanda estable. El sistema mantiene un flujo equilibrado durante el día."
    else:
        conclusion = "Demanda baja. Se sugiere optimizar frecuencias y reasignar recursos."
    
    tk.Label(frame_info, text="\n📊 Conclusión:", bg="#f5f6fa", font=("Arial", 11, "bold")).pack(anchor="w")
    tk.Label(frame_info, text=conclusion, bg="#f5f6fa", wraplength=250, justify="left").pack(anchor="w", pady=5)

# ------------------------------------------------------
# 7️⃣ Botón principal
# ------------------------------------------------------
boton = tk.Button(root, text="Generar Reporte", command=generar_reporte, bg="#004c6d", fg="white", font=("Arial", 11, "bold"))
boton.pack(pady=10)

# Cargar datos iniciales al abrir
generar_reporte()

# ------------------------------------------------------
# 8️⃣ Ejecutar interfaz
# ------------------------------------------------------
root.mainloop()
