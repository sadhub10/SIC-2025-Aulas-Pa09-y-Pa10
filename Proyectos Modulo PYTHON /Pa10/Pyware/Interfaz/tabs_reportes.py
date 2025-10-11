
import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .state import ruta_csv_actual
from analysis.stats import cargar_y_procesar_csv

# interpretación 

def etiqueta_corr(r: float) -> tuple[str, str]:
    """Devuelve (nivel, color_hex) según magnitud de correlación."""
    a = abs(r)
    if a > 0.7:  return ("muy fuerte", "#D32F2F")
    if a > 0.5:  return ("fuerte", "#F57C00")
    if a > 0.3:  return ("moderada", "#FBC02D")
    if a > 0.1:  return ("débil", "#7CB342")
    return ("muy débil / nula", "#388E3C")

def linea_explicacion_corr(variable: str, r: float) -> str:
    nivel, _ = etiqueta_corr(r)
    direccion = "positiva" if r >= 0 else "negativa"
    return f"• {variable}: r = {r:.2f} → relación {nivel} {direccion}."

def _fig_to_tk(frame_parent: tk.Frame, fig: plt.Figure, titulo: str, comentario: str | None = None):
    """Inserta una figura matplotlib dentro de un frame Tkinter con título y comentario."""
    caja = tk.Frame(frame_parent, bg="white")
    caja.pack(fill="x", padx=20, pady=15)

    if titulo:
        tk.Label(caja, text=titulo, font=("Arial", 13, "bold"), fg="#1976D2", bg="white").pack(anchor="w", pady=(0,8))

    lienzo = FigureCanvasTkAgg(fig, master=caja)
    lienzo.draw()
    widget = lienzo.get_tk_widget()
    widget.pack(fill="both", expand=True)

    if comentario:
        tk.Label(caja, text=comentario, font=("Arial", 10), bg="white", fg="#555555", wraplength=900, justify="left")\
          .pack(anchor="w", pady=(6,0))

def _top_corr(matriz: pd.DataFrame, col: str, k: int = 5) -> pd.Series:
    if col not in matriz.columns:
        return pd.Series(dtype=float)
    s = matriz[col].drop(labels=[col], errors="ignore").dropna()
    return s.reindex(s.abs().sort_values(ascending=False).head(k).index)


def mostrar_reportes(panel_contenedor: tk.Frame):
    for w in panel_contenedor.winfo_children():
        w.destroy()

    nombre_archivo = ruta_csv_actual()
    if not os.path.exists(nombre_archivo):
        tk.Label(panel_contenedor, text="No hay datos del usuario.\nRegistra tus síntomas o usa la pestaña de simulación.",
                 font=("Arial", 14), fg="gray", bg="white", justify="center").pack(expand=True, pady=50)
        return

    res = cargar_y_procesar_csv(nombre_archivo)
    if res is None:
        tk.Label(panel_contenedor, text="Error al procesar datos. Verifica el CSV.", font=("Arial", 14),
                 fg="red", bg="white").pack(expand=True, pady=50)
        return

    df, df_num, matriz, t_clima, corr_sf = res

    
    canvas = tk.Canvas(panel_contenedor, bg="white")
    scrollbar = ttk.Scrollbar(panel_contenedor, orient="vertical", command=canvas.yview)
    marco = tk.Frame(canvas, bg="white")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=marco, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    marco.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    tk.Label(marco, text="Reporte Visual e Interpretativo",
             font=("Arial", 16, "bold"), fg="#4B0082", bg="white").pack(pady=18, padx=20, anchor="w")

    # 1) Heatmap correlaciones
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    sns.heatmap(matriz, annot=True, fmt=".2f", cmap="coolwarm", ax=ax1)
    ax1.set_title("Matriz de correlación entre variables clínicas")
    _fig_to_tk(marco, fig1, "Matriz de correlación",
               "Colores rojos = relación positiva; azules = negativa; más intenso = mayor fuerza. "
               "Recuerda: correlación no implica causalidad.")

    # 2) Dolor según clima adverso (boxplot)
    if "clima_adverso" in df.columns and "dolor_score" in df.columns:
        fig2, ax2 = plt.subplots(figsize=(6.4, 5))
        sns.boxplot(x='clima_adverso', y='dolor_score', data=df, ax=ax2)
        ax2.set_title(f"Dolor según el clima adverso (p-valor t-test = {t_clima.get('p_val', 1.0):.4f})")
        ax2.set_xlabel("Clima adverso (1 = Sí, 0 = No)")
        ax2.set_ylabel("Dolor")
        comentario = "Si la separación entre cajas es clara y el p-valor es < 0.05, hay evidencia de diferencia en el dolor entre días con y sin clima adverso."
        _fig_to_tk(marco, fig2, "Dolor vs Clima Adverso", comentario)

    # 3) Sueño (día anterior) vs Fatiga (dispersión)
    if "sueno_score" in df.columns and "fatiga_score" in df.columns:
        x = df['sueno_score'].shift(1)
        y = df['fatiga_score']
        mask = ~x.isna() & ~y.isna()
        fig3, ax3 = plt.subplots(figsize=(6.4, 5))
        ax3.scatter(x[mask], y[mask], alpha=0.7)
        ax3.set_title(f"Sueño (día anterior) vs Fatiga (hoy) · r = {corr_sf:.2f}")
        ax3.set_xlabel("Sueño (día anterior)")
        ax3.set_ylabel("Fatiga (hoy)")
        nivel, color = etiqueta_corr(corr_sf)
        comentario = f"Correlación {nivel}. Valores negativos sugieren que un mejor sueño ayer se asocia con menor fatiga hoy."
        _fig_to_tk(marco, fig3, "Sueño ↔ Fatiga (desfase 1 día)", comentario)

    # 4) Evolución temporal dolor y fatiga
    if "fecha" in df.columns and "dolor_score" in df.columns and "fatiga_score" in df.columns:
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        ax4.plot(df['fecha'], df['dolor_score'], label="Dolor", linewidth=2)
        ax4.plot(df['fecha'], df['fatiga_score'], label="Fatiga", linewidth=2)
        ax4.set_title("Evolución temporal del dolor y la fatiga")
        ax4.set_xlabel("Fecha"); ax4.set_ylabel("Nivel")
        ax4.legend()
        _fig_to_tk(marco, fig4, "Series temporales (Dolor y Fatiga)",
                   "Útil para detectar brotes (picos), tendencias o mejoras sostenidas.")

    # 5) Distribución del estado de ánimo
    if "estado_animo_score" in df.columns:
        fig5, ax5 = plt.subplots(figsize=(6.4, 4.2))
        sns.histplot(df['estado_animo_score'], bins=10, kde=True, ax=ax5)
        ax5.set_title("Distribución del estado de ánimo")
        ax5.set_xlabel("Puntaje de ánimo"); ax5.set_ylabel("Frecuencia")
        _fig_to_tk(marco, fig5, "Estado de Ánimo",
                   "Curva KDE (línea) muestra la forma de la distribución. Sesgos hacia valores bajos pueden indicar periodos difíciles.")

    # 6) Dolor promedio por tipo de dieta
    if "dieta_tipo" in df.columns and "dolor_score" in df.columns:
        fig6, ax6 = plt.subplots(figsize=(6.4, 4.2))
        sns.barplot(x='dieta_tipo', y='dolor_score', data=df, estimator=np.mean, ci=None, ax=ax6)
        ax6.set_title("Dolor promedio según tipo de dieta")
        ax6.set_xlabel("Tipo de dieta"); ax6.set_ylabel("Promedio de dolor")
        _fig_to_tk(marco, fig6, "Dieta ↔ Dolor",
                   "Barras más bajas en ‘Antiinflamatoria’ apoyan el beneficio potencial de ese patrón alimentario.")

    # 7) Actividad física vs dolor
    if "actividad_fisica" in df.columns and "dolor_score" in df.columns:
        fig7, ax7 = plt.subplots(figsize=(6.4, 5))
        sns.scatterplot(x='actividad_fisica', y='dolor_score', data=df, ax=ax7)
        ax7.set_title("Actividad física vs nivel de dolor")
        ax7.set_xlabel("Actividad física (0 = No, 1 = Sí)"); ax7.set_ylabel("Dolor")
        _fig_to_tk(marco, fig7, "Actividad Física ↔ Dolor",
                   "Si los puntos con ‘1’ tienden a estar más bajos, sugiere que moverse se asocia a menos dolor (no prueba causalidad).")

    # 8) Top 5 correlaciones con el dolor (barras)
    if "dolor_score" in matriz.columns:
        top_corr = _top_corr(matriz, "dolor_score", k=5)
        fig8, ax8 = plt.subplots(figsize=(7.2, 4))
        pal = sns.color_palette("mako", n_colors=len(top_corr))
        sns.barplot(x=top_corr.values, y=top_corr.index, palette=pal, ax=ax8)
        ax8.set_title("Top 5 variables más correlacionadas con el dolor")
        ax8.set_xlabel("Coeficiente de correlación")
        _fig_to_tk(marco, fig8, "Variables más relacionadas con el dolor",
                   "Estas son las señales lineales más fuertes en tus datos. Úsalas como punto de partida para hipótesis.")

    # 9) Bloque de explicaciones breve (dolor, fatiga, ánimo, ISA)
    explicaciones = tk.Frame(marco, bg="#F7F9FC")
    explicaciones.pack(fill="x", padx=20, pady=15)
    tk.Label(explicaciones, text="💡 Cómo leer las correlaciones",
             font=("Arial", 13, "bold"), bg="#F7F9FC").pack(anchor="w", pady=(10,6))
    tk.Label(explicaciones, text=(
        "• r va de -1 a 1. Positivo: cuando sube A, tiende a subir B. Negativo: cuando sube A, tiende a bajar B.\n"
        "• Magnitud: |r| ≤ 0.10 muy débil; ≤ 0.30 débil; ≤ 0.50 moderada; ≤ 0.70 fuerte; > 0.70 muy fuerte.\n"
        "• Correlación ≠ causalidad. Úsalo para generar hipótesis, no como prueba definitiva."
    ), font=("Arial", 10), bg="#F7F9FC", justify="left").pack(anchor="w", pady=(0,12))
