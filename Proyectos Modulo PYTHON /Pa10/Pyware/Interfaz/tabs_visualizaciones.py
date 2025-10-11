
import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
from .state import ruta_csv_actual

def mostrar_visualizaciones(panel_contenedor: tk.Frame):
    for w in panel_contenedor.winfo_children():
        w.destroy()

    tk.Label(panel_contenedor, text="📊 Visualizaciones",
             font=("Arial", 16, "bold"), fg="#4B0082", bg="white").pack(pady=20)

    nombre_archivo = ruta_csv_actual()
    if not os.path.exists(nombre_archivo):
        tk.Label(panel_contenedor,
                 text="No hay datos para visualizar.\nComienza registrando tus síntomas diarios.",
                 font=("Arial", 14), fg="gray", bg="white", justify="center").pack(expand=True, pady=50)
        return

    try:
        df = pd.read_csv(nombre_archivo)
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])

        canvas = tk.Canvas(panel_contenedor, bg="white")
        scrollbar = ttk.Scrollbar(panel_contenedor, orient="vertical", command=canvas.yview)
        marco = tk.Frame(canvas, bg="white")
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=marco, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        marco.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tk.Label(marco, text="📈 Promedios de Síntomas (General)",
                 font=("Arial", 14, "bold"), fg="#1976D2", bg="white").pack(pady=20)
        cont = tk.Frame(marco, bg="white"); cont.pack(pady=10)

        sintomas = ['dolor_score', 'rigidez_score', 'inflamacion_score', 'fatiga_score']
        nombres = ['Dolor', 'Rigidez', 'Inflamación', 'Fatiga']
        colores = ['#E53935', '#FB8C00', '#FDD835', '#5E35B1']
        alto = 150

        for s, n, c in zip(sintomas, nombres, colores):
            promedio = df[s].mean() if s in df.columns else float('nan')
            base = tk.Frame(cont, bg="white"); base.pack(side="left", padx=15, anchor='s')
            tk.Label(base, text=n, font=("Arial", 11, "bold"), bg="white").pack()
            barra_cont = tk.Frame(base, bg="#E0E0E0", width=60, height=alto)
            barra_cont.pack(pady=5); barra_cont.pack_propagate(False)
            h = int((promedio / 5.0) * alto) if pd.notna(promedio) else 0
            tk.Frame(barra_cont, bg=c, width=60, height=h).pack(side="bottom")
            tk.Label(base, text=f"{(promedio if pd.notna(promedio) else 0):.2f}/5",
                     font=("Arial", 10), bg="white").pack()
    except Exception as e:
        tk.Label(panel_contenedor,
                 text=f"Error al cargar visualizaciones:\n{str(e)}",
                 font=("Arial", 12), fg="red", bg="white").pack(expand=True)
