
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data.simulate import generar_dataset_simulado
from analysis.stats import procesar_dataframe

def insertar_figura(parent, figura, titulo, comentario=None):
    caja = tk.Frame(parent, bg="white"); caja.pack(fill="x", padx=20, pady=15)
    if titulo:
        tk.Label(caja, text=titulo, font=("Arial", 13, "bold"), fg="#1976D2", bg="white").pack(anchor="w", pady=(0,8))
    lienzo = FigureCanvasTkAgg(figura, master=caja)
    lienzo.draw()
    lienzo.get_tk_widget().pack(fill="both", expand=True)
    if comentario:
        tk.Label(caja, text=comentario, font=("Arial", 10), bg="white", fg="#555", wraplength=900, justify="left")\
          .pack(anchor="w", pady=(6,0))

def mejores_correlaciones(matriz, columna, k=5):
    if columna not in matriz.columns:
        return pd.Series(dtype=float)
    serie = matriz[columna].drop(labels=[columna], errors="ignore").dropna()
    orden = serie.abs().sort_values(ascending=False).head(k).index
    return serie.reindex(orden)

def renderizar_reporte_visual(marco, df, df_num, matriz, info_t, corr_sf):
    # 1) Heatmap
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    sns.heatmap(matriz, annot=True, fmt=".2f", cmap="coolwarm", ax=ax1)
    ax1.set_title("Matriz de correlación entre variables clínicas")
    insertar_figura(marco, fig1, "Matriz de correlación",
                    "Rojos = positiva; azules = negativa; más intenso = mayor fuerza. Correlación no implica causalidad.")

    # 2) Dolor vs clima adverso
    if "clima_adverso" in df.columns and "dolor_score" in df.columns:
        fig2, ax2 = plt.subplots(figsize=(6.4, 5))
        sns.boxplot(x='clima_adverso', y='dolor_score', data=df, ax=ax2)
        ax2.set_title(f"Dolor según el clima adverso (p-valor = {info_t.get('p_val', 1.0):.4f})")
        ax2.set_xlabel("Clima adverso (1 = Sí, 0 = No)"); ax2.set_ylabel("Dolor")
        insertar_figura(marco, fig2, "Dolor vs Clima Adverso",
                        "Si p < 0.05 y las cajas se separan, hay evidencia de diferencia en dolor entre días con/sin clima adverso.")

    # 3) Sueño T-1 vs Fatiga T
    if "sueno_score" in df.columns and "fatiga_score" in df.columns:
        x = df['sueno_score'].shift(1); y = df['fatiga_score']; mask = ~x.isna() & ~y.isna()
        fig3, ax3 = plt.subplots(figsize=(6.4, 5))
        ax3.scatter(x[mask], y[mask], alpha=0.7)
        ax3.set_title(f"Sueño (día anterior) vs Fatiga (hoy) · r = {corr_sf:.2f}")
        ax3.set_xlabel("Sueño (día anterior)"); ax3.set_ylabel("Fatiga (hoy)")
        insertar_figura(marco, fig3, "Sueño ↔ Fatiga (desfase 1 día)",
                        "Si los puntos descienden al mejorar el sueño, sugiere menor fatiga al día siguiente.")

    # 4) Series temporales
    if "fecha" in df.columns and "dolor_score" in df.columns and "fatiga_score" in df.columns:
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        ax4.plot(df['fecha'], df['dolor_score'], label="Dolor", linewidth=2)
        ax4.plot(df['fecha'], df['fatiga_score'], label="Fatiga", linewidth=2)
        ax4.set_title("Evolución temporal del dolor y la fatiga")
        ax4.set_xlabel("Fecha"); ax4.set_ylabel("Nivel"); ax4.legend()
        insertar_figura(marco, fig4, "Series temporales (Dolor y Fatiga)",
                        "Observa picos (brotes), tendencias y mejoras sostenidas.")

    # 5) Histograma ánimo
    if "estado_animo_score" in df.columns:
        fig5, ax5 = plt.subplots(figsize=(6.4, 4.2))
        sns.histplot(df['estado_animo_score'], bins=10, kde=True, ax=ax5)
        ax5.set_title("Distribución del estado de ánimo")
        ax5.set_xlabel("Puntaje de ánimo"); ax5.set_ylabel("Frecuencia")
        insertar_figura(marco, fig5, "Estado de Ánimo",
                        "La curva (KDE) muestra la forma de la distribución.")

    # 6) Dieta vs dolor promedio
    if "dieta_tipo" in df.columns and "dolor_score" in df.columns:
        fig6, ax6 = plt.subplots(figsize=(6.4, 4.2))
        sns.barplot(x='dieta_tipo', y='dolor_score', data=df, estimator=np.mean, ci=None, ax=ax6)
        ax6.set_title("Dolor promedio según tipo de dieta")
        ax6.set_xlabel("Tipo de dieta"); ax6.set_ylabel("Promedio de dolor")
        insertar_figura(marco, fig6, "Dieta ↔ Dolor",
                        "Si ‘Antiinflamatoria’ es más baja, puede apoyar su beneficio (no prueba causalidad).")

    # 7) Actividad física vs dolor
    if "actividad_fisica" in df.columns and "dolor_score" in df.columns:
        fig7, ax7 = plt.subplots(figsize=(6.4, 5))
        sns.scatterplot(x='actividad_fisica', y='dolor_score', data=df, ax=ax7)
        ax7.set_title("Actividad física vs nivel de dolor")
        ax7.set_xlabel("Actividad física (0 = No, 1 = Sí)"); ax7.set_ylabel("Dolor")
        insertar_figura(marco, fig7, "Actividad Física ↔ Dolor",
                        "Si los puntos con ‘1’ se ven más bajos, sugiere menos dolor en días activos.")

    # 8) Top correlaciones con dolor
    if "dolor_score" in matriz.columns:
        top = mejores_correlaciones(matriz, "dolor_score", k=5)
        fig8, ax8 = plt.subplots(figsize=(7.2, 4))
        sns.barplot(x=top.values, y=top.index, palette="mako", ax=ax8)
        ax8.set_title("Top 5 variables más correlacionadas con el dolor")
        ax8.set_xlabel("Coeficiente de correlación")
        insertar_figura(marco, fig8, "Variables más relacionadas con el dolor",
                        "Útil para priorizar hipótesis (correlación ≠ causalidad).")

def mostrar_simulacion_dataset(panel_contenedor):
    for w in panel_contenedor.winfo_children(): w.destroy()

    cabecera = tk.Frame(panel_contenedor, bg="white"); cabecera.pack(pady=20, padx=40, fill="x")
    tk.Label(cabecera, text="🧪 Simulación de Dataset Clínico",
             font=("Arial", 16, "bold"), fg="#4B0082", bg="white").pack()

    tk.Label(cabecera, text="Genera datos simulados y visualiza todo aquí mismo.",
             font=("Arial", 11), fg="gray", bg="white", justify="center").pack(pady=10)

    caja_config = tk.Frame(cabecera, bg="white"); caja_config.pack(pady=10)
    tk.Label(caja_config, text="Número de días a simular:", font=("Arial", 11), bg="white")\
      .grid(row=0, column=0, sticky="w")
    dias_var = tk.StringVar(value="180")
    tk.Entry(caja_config, textvariable=dias_var, width=15).grid(row=0, column=1, padx=10)

    area_resultados = tk.Frame(panel_contenedor, bg="white")
    area_resultados.pack(fill="both", expand=True)

    def generar_y_mostrar():
        for w in area_resultados.winfo_children(): w.destroy()
        try:
            dias = int(dias_var.get())
            if not (30 <= dias <= 3650):
                messagebox.showerror("Error", "El número de días debe estar entre 30 y 3650.", parent=panel_contenedor)
                return

            df_sim = generar_dataset_simulado(dias)
            res = procesar_dataframe(df_sim)
            if res is None:
                messagebox.showerror("Error", "No se pudieron procesar los datos simulados.", parent=panel_contenedor)
                return

            df, df_num, matriz, info_t, corr_sf = res

            # Scroll para ver todos los gráficos
            canvas = tk.Canvas(area_resultados, bg="white")
            barra = ttk.Scrollbar(area_resultados, orient="vertical", command=canvas.yview)
            marco = tk.Frame(canvas, bg="white")
            barra.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            canvas.create_window((0, 0), window=marco, anchor="nw")
            canvas.configure(yscrollcommand=barra.set)
            marco.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            tk.Label(marco, text="Resultados del Dataset Simulado",
                     font=("Arial", 16, "bold"), fg="#4B0082", bg="white").pack(pady=18, padx=20, anchor="w")

            info = tk.Frame(marco, bg="#F0F0F0", padx=20, pady=15); info.pack(fill="x", padx=20, pady=10)
            tk.Label(info, text=f"📅 Total de registros: {len(df)}", font=("Arial", 12, "bold"), bg="#F0F0F0").pack(anchor="w")
            if 'fecha' in df.columns:
                tk.Label(info, text=f"📆 Período: {df['fecha'].min().strftime('%d/%m/%Y')} - {df['fecha'].max().strftime('%d/%m/%Y')}",
                         font=("Arial", 12), bg="#F0F0F0").pack(anchor="w")

            renderizar_reporte_visual(marco, df, df_num, matriz, info_t, corr_sf)

        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un número válido de días.", parent=panel_contenedor)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar y mostrar el reporte: {e}", parent=panel_contenedor)

    tk.Button(cabecera, text="🎲 Generar y Analizar Dataset",
              bg="#4B0082", fg="white", font=("Arial", 12, "bold"), width=30,
              command=generar_y_mostrar).pack(pady=20)
