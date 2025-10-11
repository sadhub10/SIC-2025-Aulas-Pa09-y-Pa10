# ======================================================
# 🚍 MOVILIDAD 4.0 - SISTEMA DE GESTIÓN OPERATIVA (v5)
# ======================================================

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4

from modulo1 import RUTAS
from modulo6 import PlanificadorOperacional

# ======================================================
# 🎨 ESTILO VISUAL
# ======================================================
BG = "#1C1C1C"
PANEL = "#2C2C2C"
TEXT = "#EAEAEA"
ACCENT = "#E66B1F"
AZUL = "#00BFFF"
VERDE = "#00D084"

plt.rcParams.update({
    "axes.facecolor": BG,
    "figure.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.edgecolor": "#E0E0E0",
    "xtick.color": "#E0E0E0",
    "ytick.color": "#E0E0E0",
    "text.color": "#E0E0E0",
    "axes.labelcolor": "#E0E0E0",
    "axes.titlecolor": "#E0E0E0",
    "grid.color": "#3A3A3A"
})

# ======================================================
# 🧠 DATOS BASE
# ======================================================
rutas_disponibles = list(RUTAS.keys())
planificador = PlanificadorOperacional()

# ======================================================
# 🖥️ INTERFAZ PRINCIPAL
# ======================================================
root = tk.Tk()
root.title("MOVILIDAD 4.0 - Sistema de Gestión Operativa")
root.geometry("1300x750")
root.configure(bg=BG)

# ======================================================
# 🧭 ESTRUCTURA
# ======================================================
side_menu = tk.Frame(root, bg=PANEL, width=220)
side_menu.pack(side="left", fill="y")

content_frame = tk.Frame(root, bg=BG)
content_frame.pack(side="right", fill="both", expand=True)

# ======================================================
# 🔧 UTILIDADES
# ======================================================
def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def exportar_pdf(ruta, fig):
    try:
        nombre_archivo = f"Reporte_{ruta}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = canvas.Canvas(nombre_archivo, pagesize=landscape(A4))
        pdf.setFont("Helvetica-Bold", 18)
        pdf.setFillColorRGB(0.9, 0.4, 0.1)
        pdf.drawString(50, 550, f"Reporte Operativo: {ruta}")
        pdf.setFont("Helvetica", 12)
        pdf.setFillColorRGB(1, 1, 1)
        pdf.drawString(50, 520, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        img_path = f"temp_{ruta}.png"
        fig.savefig(img_path, dpi=150)
        pdf.drawImage(img_path, 50, 200, width=700, height=250)
        os.remove(img_path)
        pdf.save()
        messagebox.showinfo("✅ Exportación Exitosa", f"Reporte guardado como:\n{nombre_archivo}")
    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo exportar el PDF:\n{e}")

# ======================================================
# 📊 REPORTES OPERACIONALES
# ======================================================
def mostrar_reportes():
    clear_content()
    tk.Label(content_frame, text="📊 Reportes Operacionales por Ruta",
             font=("Segoe UI", 18, "bold"), fg=ACCENT, bg=BG).pack(pady=15)

    frame_sel = tk.Frame(content_frame, bg=BG)
    frame_sel.pack(pady=10)
    tk.Label(frame_sel, text="Seleccionar Ruta:", fg=TEXT, bg=BG, font=("Segoe UI", 11)).grid(row=0, column=0, padx=5)
    ruta_sel = tk.StringVar(value=rutas_disponibles[0])
    drop = ttk.Combobox(frame_sel, textvariable=ruta_sel, values=rutas_disponibles, state="readonly", width=20)
    drop.grid(row=0, column=1, padx=5)
    tk.Button(frame_sel, text="🔄 Actualizar", bg=ACCENT, fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat", width=12,
              command=lambda: actualizar()).grid(row=0, column=2, padx=10)

    frame_plot = tk.Frame(content_frame, bg=BG)
    frame_plot.pack(fill="both", expand=True, padx=30, pady=20)

    def actualizar():
        for widget in frame_plot.winfo_children():
            widget.destroy()

        ruta = ruta_sel.get()
        df = planificador.calcular_operacion(ruta, datetime.now())
        resumen = planificador.obtener_resumen_global(df)

        fig, axs = plt.subplots(2, 2, figsize=(10, 5))
        fig.suptitle(f"Análisis Operativo – {ruta}", fontsize=13, fontweight="bold")

        # 1️⃣ Barras
        axs[0, 0].bar(df["hora"], df["buses"], color=AZUL)
        axs[0, 0].set_title("Buses requeridos por hora")
        axs[0, 0].set_xlabel("Hora"); axs[0, 0].set_ylabel("Cantidad")
        for i, v in enumerate(df["buses"]):
            axs[0, 0].text(df["hora"][i], v + 0.1, str(int(v)), ha="center", fontsize=8, color="white")

        # 2️⃣ Línea
        axs[0, 1].plot(df["hora"], df["demanda"], color=ACCENT, marker="o")
        axs[0, 1].set_ylim(0, 1)
        axs[0, 1].set_title("Demanda promedio por hora")
        axs[0, 1].grid(True, linestyle="--", alpha=0.4)

        # 3️⃣ Pie chart ampliado
        wedges, texts, autotexts = axs[1, 0].pie(
            df["buses"],
            labels=df["hora"],
            autopct="%1.0f%%",
            startangle=90,
            pctdistance=0.75,
            labeldistance=1.1,
            radius=1.3,
            colors=plt.cm.plasma(df["hora"] / 24)
        )
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color("white")
        axs[1, 0].set_title("Distribución de flota operativa (%)", pad=35, fontsize=11, fontweight="bold")

        # 4️⃣ Heatmap
        corr = df[["demanda", "frecuencia", "buses"]].corr()
        im = axs[1, 1].imshow(corr, cmap="coolwarm", vmin=0, vmax=1, aspect="equal")
        axs[1, 1].set_title("Matriz de Correlación Operativa")
        axs[1, 1].set_xticks(range(len(corr.columns)))
        axs[1, 1].set_yticks(range(len(corr.columns)))
        axs[1, 1].set_xticklabels(corr.columns, rotation=45, ha="left")
        axs[1, 1].set_yticklabels(corr.columns)
        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                valor = corr.iloc[i, j]
                axs[1, 1].text(j, i, f"{valor:.2f}", ha="center", va="center",
                               color="white" if valor < 0.5 else "black", fontsize=8)
        fig.colorbar(im, ax=axs[1, 1], fraction=0.046, pad=0.04)

        plt.tight_layout()
        canvas_fig = FigureCanvasTkAgg(fig, master=frame_plot)
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack(fill="both", expand=True)

        # 🧭 Panel lateral sincronizado (sin demanda promedio)
        for widget in side_menu.winfo_children():
            if str(widget).endswith("info_lbl") or str(widget).endswith("pdf_btn"):
                widget.destroy()

        info_lbl = tk.Label(side_menu, name="info_lbl",
                            text=f"Ruta seleccionada:\n{ruta}\n{RUTAS[ruta]['nombre']}\n\n"
                                 f"Frecuencia Promedio: {resumen['frecuencia_promedio']} min\n"
                                 f"Flota Máxima: {resumen['flota_maxima']}\n"
                                 f"Hora Pico: {resumen['hora_pico']}:00 hrs",
                            bg=PANEL, fg=TEXT, font=("Segoe UI", 10), justify="left")
        info_lbl.pack(side="bottom", pady=10, padx=10)

        pdf_btn = tk.Button(side_menu, name="pdf_btn", text="📄 Exportar PDF",
                            bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                            relief="flat", width=18,
                            command=lambda: exportar_pdf(ruta, fig))
        pdf_btn.pack(side="bottom", pady=5)

    actualizar()

# ======================================================
# ➕ AGREGAR NUEVA RUTA
# ======================================================
def agregar_ruta():
    archivo = filedialog.askopenfilename(filetypes=[("CSV o TXT", "*.csv *.txt")])
    if archivo:
        try:
            df = pd.read_csv(archivo)
            columnas_requeridas = {"hora", "demanda", "frecuencia", "buses", "duracion"}
            if not columnas_requeridas.issubset(df.columns):
                messagebox.showerror("❌ Error",
                                     "El archivo CSV no tiene las columnas requeridas:\n"
                                     "hora, demanda, frecuencia, buses, duracion")
                return

            nombre = os.path.basename(archivo).split(".")[0]
            # Estructura completa requerida por los módulos
            RUTAS[nombre] = {
                                "nombre": f"Ruta personalizada ({nombre})",
                                "paradas": [
                                            {"id": f"{nombre}_1", "nombre": "Inicio", "tiempo_transcurso": 0, "latitud": 8.983, "longitud": -79.520},
                                            {"id": f"{nombre}_2", "nombre": "Intermedia", "tiempo_transcurso": 30, "latitud": 8.987, "longitud": -79.530},
                                            {"id": f"{nombre}_3", "nombre": "Final", "tiempo_transcurso": 60, "latitud": 8.990, "longitud": -79.540}
                                            ],
                                                "tiempos": {"duracion_min": 60}
                        ,   }

            rutas_disponibles.append(nombre)

            messagebox.showinfo("✅ Ruta agregada",
                                f"Se añadió la ruta: {nombre}\n"
                                "Ahora puede seleccionarla en el menú desplegable.")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo leer el archivo:\n{e}")

# ======================================================
# 🧭 MENÚ LATERAL
# ======================================================
tk.Label(side_menu, text="🚍 MOVILIDAD 4.0", bg=PANEL, fg=ACCENT,
         font=("Segoe UI", 14, "bold")).pack(pady=20)

btn_style = {
    "bg": PANEL, "fg": TEXT, "font": ("Segoe UI", 10, "bold"),
    "activebackground": ACCENT, "activeforeground": "white",
    "bd": 0, "relief": "flat", "width": 20, "anchor": "w"
}

tk.Button(side_menu, text="📈 Reportes", command=mostrar_reportes, **btn_style).pack(pady=8)
tk.Button(side_menu, text="➕ Agregar Ruta", command=agregar_ruta, **btn_style).pack(pady=8)

mostrar_reportes()
root.mainloop()
