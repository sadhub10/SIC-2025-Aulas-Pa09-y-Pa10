
import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
from .state import ruta_csv_actual
from analysis.stats import cargar_y_procesar_csv

def _bloque_promedios(df, parent):
    """Bloque de barras simples con los promedios de síntomas."""
    tk.Label(parent, text=" Promedios de Síntomas (General)",
             font=("Arial", 14, "bold"), fg="#1976D2", bg="white").pack(pady=(10, 10))
    cont = tk.Frame(parent, bg="white"); cont.pack(pady=5)

    sintomas = ['dolor_score', 'rigidez_score', 'inflamacion_score', 'fatiga_score']
    nombres  = ['Dolor', 'Rigidez', 'Inflamación', 'Fatiga']
    colores  = ['#E53935', '#FB8C00', '#FDD835', '#5E35B1']
    alto     = 150  

    for s, n, c in zip(sintomas, nombres, colores):
        promedio = df[s].mean() if s in df.columns else float('nan')
        base = tk.Frame(cont, bg="white"); base.pack(side="left", padx=18, anchor='s')
        tk.Label(base, text=n, font=("Arial", 11, "bold"), bg="white").pack()
        barra_cont = tk.Frame(base, bg="#E0E0E0", width=60, height=alto)
        barra_cont.pack(pady=5); barra_cont.pack_propagate(False)
        h = int((promedio / 5.0) * alto) if pd.notna(promedio) else 0
        tk.Frame(barra_cont, bg=c, width=60, height=h).pack(side="bottom")
        valor = 0 if pd.isna(promedio) else promedio
        tk.Label(base, text=f"{valor:.2f}/5", font=("Arial", 10), bg="white").pack()

def mostrar_analisis_estadistico(panel_contenedor: tk.Frame):
    for w in panel_contenedor.winfo_children():
        w.destroy()
    canvas = tk.Canvas(panel_contenedor, bg="white")
    scrollbar = ttk.Scrollbar(panel_contenedor, orient="vertical", command=canvas.yview)
    marco = tk.Frame(canvas, bg="white")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=marco, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    marco.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Título 
    tk.Label(marco, text=" Análisis Estadístico de Correlaciones",
             font=("Arial", 16, "bold"), fg="#4B0082", bg="white").pack(pady=20)

    # Ruta del CSV del usuario activo
    nombre_archivo = ruta_csv_actual()
    if not os.path.exists(nombre_archivo):
        tk.Label(marco,
                 text="No hay datos registrados aún.\nComienza registrando tus síntomas diarios.",
                 font=("Arial", 14), fg="gray", bg="white", justify="center").pack(expand=True, pady=50)
        return

    # Procesamiento y métricas
    res = cargar_y_procesar_csv(nombre_archivo)
    if res is None:
        tk.Label(marco,
                 text="Error al procesar los datos.\nVerifica que el archivo contenga información válida.",
                 font=("Arial", 14), fg="red", bg="white", justify="center").pack(expand=True, pady=50)
        return

    df, _, matriz, resultado_t_clima, corr_sueno_fatiga = res

    # Tarjeta de resumen (total y periodo)
    info = tk.Frame(marco, bg="#F0F0F0", padx=20, pady=15)
    info.pack(fill="x", padx=20, pady=10)
    tk.Label(info, text=f" Total de registros: {len(df)}", font=("Arial", 12, "bold"), bg="#F0F0F0").pack(anchor="w")
    if 'fecha' in df.columns:
        tk.Label(info, text=f" Período: {df['fecha'].min().strftime('%d/%m/%Y')} - {df['fecha'].max().strftime('%d/%m/%Y')}",
                 font=("Arial", 12), bg="#F0F0F0").pack(anchor="w")

    
    _bloque_promedios(df, marco)

    # Correlaciones con el dolor
    tk.Label(marco, text="🔗 Correlaciones con el Dolor",
             font=("Arial", 14, "bold"), fg="#1976D2", bg="white").pack(pady=(20, 10))
    cont = tk.Frame(marco, bg="white", padx=20); cont.pack(fill="x", padx=20)

    if 'dolor_score' in matriz.columns:
        correlaciones = matriz['dolor_score'].sort_values(ascending=False)
        nombres = {
            'rigidez_score': 'Rigidez Matutina', 'inflamacion_score': 'Inflamación',
            'fatiga_score': 'Fatiga', 'clima_adverso': 'Clima Adverso (Lluvia/Humedad)',
            'sueno_score': 'Calidad del Sueño', 'dieta_score': 'Dieta Antiinflamatoria',
            'actividad_fisica': 'Actividad Física', 'temperatura_C': 'Temperatura',
            'ISA': 'Índice General de Síntomas', 'estado_animo_score': 'Estado de Ánimo'
        }
        variables = ['rigidez_score','inflamacion_score','fatiga_score','clima_adverso',
                     'sueno_score','dieta_score','actividad_fisica','temperatura_C',
                     'estado_animo_score','ISA']

        for var in variables:
            if var in correlaciones.index:
                val = correlaciones[var]
               
                color = "#388E3C"  
                if pd.notna(val):
                    if abs(val) > 0.7: color = "#D32F2F"   
                    elif abs(val) > 0.5: color = "#F57C00" 
                    elif abs(val) > 0.3: color = "#FBC02D" 
                fila = tk.Frame(cont, bg="white"); fila.pack(fill="x", pady=3)
                tk.Label(fila, text=f"• {nombres.get(var,var)}:", font=("Arial", 11),
                         bg="white", width=35, anchor="w").pack(side="left")
                tk.Label(fila, text=f"{0 if pd.isna(val) else val:.3f}",
                         font=("Arial", 11, "bold"), fg=color, bg="white").pack(side="left")

    # Notas
    tk.Label(marco, text="", bg="white").pack(pady=10)
    pval = resultado_t_clima.get('p_val', 1.0)
    signif = "significativa (p < 0.05)" if pval < 0.05 else "NO significativa (p ≥ 0.05)"
    tk.Label(marco, text=f" Clima vs Dolor: diferencia {signif}.",
             font=("Arial", 12), bg="white").pack(pady=5)
    tk.Label(marco, text=f"🛌 Sueño (día anterior) vs Fatiga (hoy): r = {corr_sueno_fatiga:.3f}.",
             font=("Arial", 12), bg="white").pack(pady=5)
