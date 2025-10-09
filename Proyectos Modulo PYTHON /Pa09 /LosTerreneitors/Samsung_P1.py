import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import os
from PIL import Image, ImageTk


class IAAnalisisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hábitos de IA y Pensamiento Crítico - Análisis Universitario")
        self.root.geometry("1400x900")

        # 🎨 Paleta
        self.color_verde = "#2E7D32"
        self.color_naranja = "#F57C00"
        self.color_azul = "#1976D2"
        self.color_bg = "#F5F5F5"
        self.color_card = "#FFFFFF"

        self.df = None
        self.df_limpio = None

        # Columnas de PC
        self.pc_cols = [
            'pc_analisis', 'pc_inferencia', 'pc_evaluacion',
            'pc_autorregulacion', 'pc_apertura_mental'
        ]

        self.configurar_estilos()
        self.root.configure(bg=self.color_bg)
        self.crear_header()

        # Notebook
        self.notebook = ttk.Notebook(root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(8, 10))

        # Pestañas
        self.crear_pestana_importar()
        self.crear_pestana_limpiar()
        self.crear_pestana_dashboard()
        self.crear_pestana_reporte()

    # ==================== UI / ESTILOS ====================
    def configurar_estilos(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('Custom.TNotebook', background=self.color_bg, borderwidth=0)
        style.configure('Custom.TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 10, 'bold'))
        style.map('Custom.TNotebook.Tab',
                  background=[('selected', self.color_verde)],
                  foreground=[('selected', 'white'), ('!selected', '#555555')])

        style.configure('TFrame', background=self.color_bg)
        style.configure('TLabel', background=self.color_bg, foreground='#333333')
        style.configure('TButton', font=('Segoe UI', 9), padding=[10, 6])

    def crear_header(self):
        header_frame = tk.Frame(self.root, bg='white', height=96)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        try:
            # Ruta de tu logo (si no existe, muestra solo el título)
            logo_path = r"Logo_Proyecto_Samsung.png"
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                ar = img.width / img.height
                new_h = 80
                new_w = int(new_h * ar)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)

                container = tk.Frame(header_frame, bg='white')
                container.pack(expand=True)

                tk.Label(container, image=self.logo_img, bg='white').pack(side='left', padx=16)
                tk.Label(container,
                         text="Análisis: Hábitos de IA y Pensamiento Crítico",
                         font=('Segoe UI', 16, 'bold'),
                         fg=self.color_verde, bg='white').pack(side='left', padx=16)
            else:
                tk.Label(header_frame,
                         text="Análisis: Hábitos de IA y Pensamiento Crítico",
                         font=('Segoe UI', 18, 'bold'),
                         fg=self.color_verde, bg='white').pack(expand=True)
        except Exception:
            tk.Label(header_frame,
                     text="Análisis: Hábitos de IA y Pensamiento Crítico",
                     font=('Segoe UI', 18, 'bold'),
                     fg=self.color_verde, bg='white').pack(expand=True)

    # ==================== PESTAÑAS ====================
    def crear_pestana_importar(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📥 Importar")

        btn = ttk.Frame(frame)
        btn.pack(pady=20)
        ttk.Button(btn, text="Cargar CSV", command=self.cargar_csv, width=20).pack(side='left', padx=5)
        ttk.Button(btn, text="Ver Info del Dataset", command=self.mostrar_info, width=20).pack(side='left', padx=5)
        ttk.Button(btn, text="Validar Columnas", command=self.validar_columnas, width=20).pack(side='left', padx=5)

        ttk.Label(frame, text="Vista Previa de Datos:", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        self.tree_importar = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree_importar.yview)
        hsb.config(command=self.tree_importar.xview)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree_importar.pack(fill='both', expand=True)

        self.lbl_info_importar = ttk.Label(frame, text="", font=('Segoe UI', 10))
        self.lbl_info_importar.pack(pady=5)

    def crear_pestana_limpiar(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🧹 Limpiar")

        btn = ttk.Frame(frame)
        btn.pack(pady=20)
        ttk.Button(btn, text="Limpiar y Estandarizar Datos", command=self.limpiar_datos, width=25).pack(side='left', padx=5)
        ttk.Button(btn, text="Ver Datos Limpios", command=self.mostrar_datos_limpios, width=20).pack(side='left', padx=5)

        ttk.Label(frame, text="Proceso de Limpieza y Estandarización:", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        self.txt_limpieza = tk.Text(text_frame, height=12, yscrollcommand=scrollbar.set,
                                    font=('Consolas', 9), bg='#FAFAFA', relief='flat', borderwidth=10)
        self.txt_limpieza.pack(fill='both', expand=True)
        scrollbar.config(command=self.txt_limpieza.yview)

        ttk.Label(frame, text="Vista Previa de Datos Limpios:", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        self.tree_limpiar = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree_limpiar.yview)
        hsb.config(command=self.tree_limpiar.xview)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree_limpiar.pack(fill='both', expand=True)

    def crear_pestana_dashboard(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Dashboard")

        controls = ttk.Frame(frame)
        controls.pack(pady=(8, 12))
        ttk.Button(controls, text="🔄 Generar Gráficos", command=self.generar_graficos, width=20).pack(side='left', padx=8)
        ttk.Button(controls, text="💾 Guardar Gráficos PNG", command=self.guardar_graficos, width=20).pack(side='left', padx=8)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=10, pady=(0, 14))

        self.graficos_frame = ttk.Frame(frame)
        self.graficos_frame.pack(fill='both', expand=True, padx=10, pady=(26, 12))

    def crear_pestana_reporte(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📄 Reporte")

        btn = ttk.Frame(frame)
        btn.pack(pady=20)
        ttk.Button(btn, text="📊 Exportar CSV Limpio", command=self.exportar_csv, width=20).pack(side='left', padx=5)
        ttk.Button(btn, text="🖼️ Exportar Gráficos PNG", command=self.exportar_graficos, width=20).pack(side='left', padx=5)
        ttk.Button(btn, text="📝 Generar Reporte Completo", command=self.generar_reporte_completo, width=25).pack(side='left', padx=5)

        ttk.Label(frame, text="Reporte de Análisis Completo:", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        self.txt_reporte = tk.Text(text_frame, height=25, yscrollcommand=scrollbar.set,
                                   font=('Consolas', 9), bg='#FAFAFA', relief='flat', borderwidth=10)
        self.txt_reporte.pack(fill='both', expand=True)
        scrollbar.config(command=self.txt_reporte.yview)

    # ==================== CARGA / INFO / VALIDACIÓN ====================
    def cargar_csv(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de encuesta",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if archivo:
            try:
                self.df = pd.read_csv(archivo)
                self.mostrar_vista_previa(self.tree_importar, self.df)
                self.lbl_info_importar.config(
                    text=f"✓ Dataset cargado: {len(self.df)} estudiantes, {len(self.df.columns)} variables"
                )
                messagebox.showinfo("Éxito", "CSV cargado correctamente.\n\nAhora valida las columnas obligatorias.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar CSV:\n{str(e)}")

    def mostrar_vista_previa(self, tree, df, max_rows=100):
        tree.delete(*tree.get_children())
        if df is None:
            return
        tree['columns'] = list(df.columns)
        tree['show'] = 'headings'
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        for _, row in df.head(max_rows).iterrows():
            tree.insert('', 'end', values=list(row))

    def mostrar_info(self):
        if self.df is None:
            messagebox.showwarning("Advertencia", "Primero carga un dataset")
            return
        info_text = f"INFORMACIÓN DEL DATASET\n{'='*60}\n\n"
        info_text += f"Dimensiones: {len(self.df)} filas × {len(self.df.columns)} columnas\n\n"
        info_text += "COLUMNAS DISPONIBLES:\n" + "-"*60 + "\n"
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            nulls = self.df[col].isna().sum()
            info_text += f"  • {col}\n    Tipo: {dtype} | Nulos: {nulls}\n"
        messagebox.showinfo("Información del Dataset", info_text)

    def validar_columnas(self):
        if self.df is None:
            messagebox.showwarning("Advertencia", "Primero carga un dataset")
            return
        cols_req = self.pc_cols + ['pc_total', 'promedio_academico', 'horas_estudio_dia', 'metodo_estudio']
        faltantes = [c for c in cols_req if c not in self.df.columns]
        if faltantes:
            msg = "⚠️ COLUMNAS FALTANTES:\n\n" + "\n".join([f"  • {c}" for c in faltantes])
            msg += "\n\nEl análisis completo requiere estas columnas."
            messagebox.showwarning("Validación", msg)
        else:
            msg = "✓ VALIDACIÓN EXITOSA\n\nPensamiento Crítico:\n"
            for c in self.pc_cols:
                msg += f"  ✓ {c}\n"
            msg += "  ✓ pc_total\n\nVariables de análisis:\n  ✓ promedio_academico\n  ✓ horas_estudio_dia\n  ✓ metodo_estudio\n\nPuedes proceder a limpiar los datos."
            messagebox.showinfo("Validación", msg)

    # ==================== LIMPIEZA (helpers) ====================
    def _sanitize_str(self, x):
        if pd.isna(x):
            return ""
        return str(x).strip().upper()

    def _normalizar_categoria(self, serie, mapping, desconocido="DESCONOCIDO"):
        """
        Limpia espacios, pasa a mayúsculas y mapea sinónimos.
        Convierte vacíos y N/A a DESCONOCIDO.
        """
        s = serie.apply(self._sanitize_str)
        vacios = s.isin(["", "NAN", "NA", "N/A", "NONE", "NULL"])
        s[vacios] = desconocido
        s = s.map(lambda v: mapping.get(v, mapping.get(v.strip(), v)))
        s = s.replace({"": desconocido})
        return s

    def limpiar_datos(self):
        if self.df is None:
            messagebox.showwarning("Advertencia", "Primero carga un dataset")
            return

        # Log en el panel de texto
        self.txt_limpieza.delete(1.0, tk.END)
        log = self.txt_limpieza

        try:
            df = self.df.copy()
            filas_ini, cols_ini = df.shape

            log.insert(tk.END, "="*70 + "\nLIMPIEZA Y ESTANDARIZACIÓN (v2)\n" + "="*70 + "\n\n")

            # ---------- 0) Quitar columnas basura conocidas ----------
            basura_cols = [c for c in df.columns if c.lower().startswith("columna_ruido")]
            if basura_cols:
                df.drop(columns=basura_cols, inplace=True, errors="ignore")
                log.insert(tk.END, f"🧹 Columnas basura eliminadas: {', '.join(basura_cols)}\n")

            # ---------- 1) Eliminar duplicados (por todas las columnas) ----------
            dups = df.duplicated().sum()
            if dups > 0:
                df = df.drop_duplicates().reset_index(drop=True)
                log.insert(tk.END, f"🗑️ Filas duplicadas eliminadas: {dups}\n")
            else:
                log.insert(tk.END, "✓ Sin duplicados exactos\n")

            # ---------- 2) PROMEDIO ACADÉMICO [1-3] ----------
            if "promedio_academico" in df.columns:
                s = pd.to_numeric(df["promedio_academico"], errors="coerce")
                invalidos = s.isna().sum()
                s = s.clip(lower=1, upper=3)           # límites válidos
                med = s.median(skipna=True)
                s = s.fillna(med)                      # imputación
                df["promedio_academico"] = s
                log.insert(tk.END, f"📚 promedio_academico → inválidos/imputados: {invalidos}, mediana={med:.2f}\n")

            # ---------- 3) HORAS DE ESTUDIO ----------
            if "horas_estudio_dia" in df.columns:
                h = pd.to_numeric(df["horas_estudio_dia"], errors="coerce")
                antes_nan = h.isna().sum()
                h[(h < 0) | (h > 16)] = np.nan          # negativos y > 16h/día como inválidos
                extremos = h.isna().sum() - antes_nan
                med = h.median(skipna=True)
                h = h.fillna(med)
                df["horas_estudio_dia"] = h
                df["horas_bin"] = pd.cut(h, bins=[-0.001, 2, 5, 16], labels=["0-2h", "3-5h", "6+h"])
                log.insert(tk.END, f"⏰ horas_estudio_dia → outliers>16/negativos: {extremos}, imputación mediana={med:.2f}\n")

            # ---------- 4) CATEGORÍAS: MÉTODO E IA ----------
            map_metodo = {
                "INDIVIDUAL": "INDIVIDUAL", "  INDIVIDUAL": "INDIVIDUAL",
                "GRUPAL": "GRUPAL", "  GRUPAL": "GRUPAL",
                "DIGITAL": "DIGITAL",
                "LIBROS": "LIBROS",
                "DESCONOCIDO": "DESCONOCIDO",
            }
            map_ia = {
                "DIARIO": "DIARIO", "SEMANAL": "SEMANAL", "MENSUAL": "MENSUAL",
                "NUNCA": "NUNCA", "OCASIONAL": "OCASIONAL", "RARA VEZ": "OCASIONAL",
                "DESCONOCIDO": "DESCONOCIDO",
            }

            if "metodo_estudio" in df.columns:
                df["metodo_estudio"] = self._normalizar_categoria(df["metodo_estudio"], map_metodo)
                log.insert(tk.END, "🧭 metodo_estudio normalizado (espacios, mayúsc., N/A → DESCONOCIDO)\n")

            if "ia_frecuencia" in df.columns:
                df["ia_frecuencia"] = self._normalizar_categoria(df["ia_frecuencia"], map_ia)
                log.insert(tk.END, "🤖 ia_frecuencia normalizada (sinónimos y N/A)\n")

            # ---------- 5) PENSAMIENTO CRÍTICO Likert [1-5] ----------
            pc_cols_presentes = [c for c in self.pc_cols if c in df.columns]
            for c in pc_cols_presentes:
                s = pd.to_numeric(df[c], errors="coerce")
                inval = s.isna().sum()
                s = s.clip(lower=1, upper=5)
                med = s.median(skipna=True)
                s = s.fillna(med)
                df[c] = s
                log.insert(tk.END, f"🧠 {c} → inválidos/imputados: {inval}, mediana={med:.2f}\n")

            if pc_cols_presentes:
                df["pc_total"] = df[pc_cols_presentes].mean(axis=1).round(2)
                log.insert(tk.END, f"   ► pc_total recalculado con {len(pc_cols_presentes)} dimensiones\n")

            # ---------- 6) EDAD / SEMESTRE ----------
            if "edad" in df.columns:
                s = pd.to_numeric(df["edad"], errors="coerce")
                s[(s < 16) | (s > 80)] = np.nan
                med = s.median(skipna=True)
                df["edad"] = s.fillna(med)
                log.insert(tk.END, f"👤 edad → fuera de rango imputados a mediana={med:.0f}\n")

            if "semestre" in df.columns:
                s = pd.to_numeric(df["semestre"], errors="coerce")
                s[(s < 1) | (s > 12)] = np.nan
                med = s.median(skipna=True)
                df["semestre"] = s.fillna(med)
                log.insert(tk.END, f"🏫 semestre → fuera de rango imputados a mediana={med:.0f}\n")

            # ---------- 7) Strings con espacios extra ----------
            for c in df.columns:
                if df[c].dtype == object:
                    df[c] = (df[c].astype(str)
                                   .str.strip()
                                   .str.upper()
                                   .replace({"NAN": "DESCONOCIDO", "": "DESCONOCIDO"}))

            # ---------- 8) Validación final mínima ----------
            cols_clave = [c for c in ["promedio_academico", "horas_estudio_dia", "pc_total"] if c in df.columns]
            if cols_clave:
                antes = len(df)
                df = df.dropna(subset=cols_clave)
                eliminadas = antes - len(df)
                if eliminadas > 0:
                    log.insert(tk.END, f"🚮 Filas eliminadas por NaN en claves {cols_clave}: {eliminadas}\n")

            # ---------- 9) Resumen ----------
            filas_fin, cols_fin = df.shape
            log.insert(tk.END, f"\nResumen: {filas_ini}×{cols_ini}  →  {filas_fin}×{cols_fin}\n")
            log.insert(tk.END, "✅ LIMPIEZA COMPLETADA (v2)\n")

            self.df_limpio = df
            self.mostrar_vista_previa(self.tree_limpiar, self.df_limpio)
            messagebox.showinfo("Éxito",
                "Datos limpiados y estandarizados correctamente (v2).\nRevisa el log para ver duplicados eliminados, categorías normalizadas y outliers tratados.")

        except Exception as e:
            messagebox.showerror("Error", f"Error en la limpieza:\n{str(e)}")

    def mostrar_datos_limpios(self):
        if self.df_limpio is None:
            messagebox.showwarning("Advertencia", "Primero limpia los datos")
        else:
            self.mostrar_vista_previa(self.tree_limpiar, self.df_limpio)

    # ==================== GRÁFICOS (espaciado ampliado) ====================
    def generar_graficos(self):
        if self.df_limpio is None:
            messagebox.showwarning("Advertencia", "Primero limpia los datos")
            return

        for w in self.graficos_frame.winfo_children():
            w.destroy()

        try:
            fig = Figure(figsize=(14, 10))
            fig.patch.set_facecolor(self.color_bg)

            # MÁS ESPACIO: subplots y título
            fig.subplots_adjust(
                top=0.83, bottom=0.08, left=0.07, right=0.98,
                hspace=0.60, wspace=0.45
            )
            fig.suptitle('Dashboard: Hábitos de IA y Pensamiento Crítico',
                fontsize=16, fontweight='bold', y=0.96, color=self.color_verde)

            # 1) Barras
            ax1 = fig.add_subplot(2, 2, 1)
            if {'horas_bin', 'promedio_academico'}.issubset(self.df_limpio.columns):
                grouped = self.df_limpio.groupby('horas_bin', observed=True).agg(
                    promedio_academico=('promedio_academico', 'mean'),
                    pc_total=('pc_total', 'mean')
                ).reset_index()
                x = np.arange(len(grouped))
                width = 0.35
                ax1.bar(x - width/2, grouped['promedio_academico'], width,
                        label='Promedio Académico', color=self.color_azul, alpha=0.95)
                ax1.bar(x + width/2, grouped['pc_total'], width,
                        label='Pensamiento Crítico', color=self.color_naranja, alpha=0.95)
                ax1.set_xticks(x)
                ax1.set_xticklabels(grouped['horas_bin'])
                ax1.set_xlabel('Horas de Estudio por Día', fontweight='bold')
                ax1.set_ylabel('Puntaje', fontweight='bold')
                ax1.set_title('Rendimiento y PC según Horas de Estudio', fontsize=12, fontweight='bold', pad=12)
                ax1.legend(loc='upper right', frameon=False)
                ax1.grid(axis='y', alpha=0.3)
            else:
                ax1.text(0.5, 0.5, 'Faltan columnas: horas_bin/promedio_academico',
                         ha='center', va='center', transform=ax1.transAxes)

            # 2) Pie (donut)
            ax2 = fig.add_subplot(2, 2, 2)
            if 'metodo_estudio' in self.df_limpio.columns:
                counts = self.df_limpio['metodo_estudio'].value_counts()
                colors = plt.cm.Set3(np.linspace(0, 1, len(counts)))
                wedges, texts, autotexts = ax2.pie(
                    counts.values, labels=counts.index, autopct='%1.1f%%', startangle=90,
                    colors=colors, pctdistance=0.75, labeldistance=1.10, textprops={'fontsize': 10}
                )
                centre = plt.Circle((0, 0), 0.52, fc=self.color_bg)
                ax2.add_artist(centre)
                ax2.set_title('Distribución de Métodos de Estudio', fontsize=12, fontweight='bold', pad=12)
                for a in autotexts:
                    a.set_color('white'); a.set_fontweight('bold')
                ax2.axis('equal')
            else:
                ax2.text(0.5, 0.5, 'Falta columna: metodo_estudio',
                         ha='center', va='center', transform=ax2.transAxes)

            # 3) Líneas
            ax3 = fig.add_subplot(2, 2, 3)
            if {'horas_bin', 'promedio_academico'}.issubset(self.df_limpio.columns):
                grouped = self.df_limpio.groupby('horas_bin', observed=True).agg(
                    promedio_academico=('promedio_academico', 'mean'),
                    pc_total=('pc_total', 'mean')
                ).reset_index()
                x = range(len(grouped))
                ax3.plot(x, grouped['promedio_academico'], marker='o', linewidth=2.4,
                         label='Promedio Académico', color=self.color_azul)
                ax3.plot(x, grouped['pc_total'], marker='s', linewidth=2.4,
                         label='Pensamiento Crítico', color=self.color_naranja)
                ax3.set_xticks(list(x))
                ax3.set_xticklabels(grouped['horas_bin'])
                ax3.set_xlabel('Grupos de Horas de Estudio', fontweight='bold')
                ax3.set_ylabel('Puntaje Promedio', fontweight='bold')
                ax3.set_title('Tendencia: Rendimiento y PC vs Horas', fontsize=12, fontweight='bold', pad=12)
                ax3.legend(loc='best', frameon=False)
                ax3.grid(True, alpha=0.3)
            else:
                ax3.text(0.5, 0.5, 'Faltan columnas: horas_bin/promedio_academico',
                         ha='center', va='center', transform=ax3.transAxes)

            # 4) Boxplot + línea PC
            ax4 = fig.add_subplot(2, 2, 4)
            if {'metodo_estudio', 'promedio_academico'}.issubset(self.df_limpio.columns):
                metodos = sorted(self.df_limpio['metodo_estudio'].unique())
                datos = [self.df_limpio[self.df_limpio['metodo_estudio'] == m]['promedio_academico'].dropna()
                         for m in metodos]
                ax4.boxplot(datos, labels=metodos, patch_artist=True,
                            boxprops=dict(facecolor='#BBDEFB', alpha=0.9),
                            medianprops=dict(color='red', linewidth=2))
                ax4.set_xlabel('Método de Estudio', fontweight='bold')
                ax4.set_ylabel('Promedio Académico', fontweight='bold')
                ax4.set_title('Dispersión del Rendimiento por Método', fontsize=12, fontweight='bold', pad=12)
                ax4.tick_params(axis='x', rotation=15)
                ax4.grid(axis='y', alpha=0.3)

                if 'pc_total' in self.df_limpio.columns:
                    pc_medias = [
                        float(self.df_limpio[self.df_limpio['metodo_estudio'] == m]['pc_total'].mean())
                        for m in metodos
                    ]
                    ax4_t = ax4.twinx()
                    ax4_t.plot(range(1, len(metodos)+1), pc_medias, marker='D',
                               color=self.color_naranja, linewidth=2.2, markersize=7, label='PC Promedio')
                    ax4_t.set_ylabel('PC Promedio', fontweight='bold', color=self.color_naranja)
                    ax4_t.tick_params(axis='y', labelcolor=self.color_naranja)
                    ax4_t.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)
            else:
                ax4.text(0.5, 0.5, 'Faltan columnas: metodo_estudio/promedio_academico',
                         ha='center', va='center', transform=ax4.transAxes)

            canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

            self.fig = fig
            messagebox.showinfo("Éxito", "✓ Gráficos generados con más espacio y mejor acomodo.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráficos:\n{str(e)}")

    # ==================== EXPORTACIONES & REPORTE ====================
    def guardar_graficos(self):
        if not hasattr(self, 'fig'):
            messagebox.showwarning("Advertencia", "Primero genera los gráficos")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="dashboard_ia_pensamiento_critico.png"
        )
        if archivo:
            try:
                self.fig.savefig(archivo, dpi=300, bbox_inches='tight', facecolor=self.color_bg)
                messagebox.showinfo("Éxito", f"✓ Gráficos guardados en:\n{archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")

    def exportar_csv(self):
        if self.df_limpio is None:
            messagebox.showwarning("Advertencia", "Primero limpia los datos")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="datos_limpios_ia_pc.csv"
        )
        if archivo:
            try:
                self.df_limpio.to_csv(archivo, index=False, encoding='utf-8-sig')
                messagebox.showinfo("Éxito", f"✓ CSV limpio guardado en:\n{archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

    def exportar_graficos(self):
        self.guardar_graficos()

    def generar_reporte_completo(self):
        if self.df_limpio is None:
            messagebox.showwarning("Advertencia", "Primero limpia los datos")
            return
        try:
            self.txt_reporte.delete(1.0, tk.END)
            r = "="*80 + "\n"
            r += "      REPORTE DE ANÁLISIS: HÁBITOS DE IA Y PENSAMIENTO CRÍTICO\n"
            r += "                    EN ESTUDIANTES UNIVERSITARIOS\n"
            r += "="*80 + "\n\n"
            r += f"📊 Total de estudiantes analizados: {len(self.df_limpio)}\n"
            r += f"📅 Fecha de generación: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n"

            # 1) Descriptivas
            r += "━"*80 + "\n1. ESTADÍSTICAS DESCRIPTIVAS GENERALES\n" + "━"*80 + "\n\n"
            if 'promedio_academico' in self.df_limpio.columns:
                s = self.df_limpio['promedio_academico']
                r += f"📚 PROMEDIO ACADÉMICO [1-3]  → Media: {s.mean():.3f} | Mediana: {s.median():.3f} | σ: {s.std():.3f} | Min: {s.min():.3f} | Max: {s.max():.3f}\n\n"
            if 'horas_estudio_dia' in self.df_limpio.columns:
                s = self.df_limpio['horas_estudio_dia']
                r += f"⏰ HORAS/DÍA  → Media: {s.mean():.2f} | Mediana: {s.median():.2f} | σ: {s.std():.2f} | Min: {s.min():.2f} | Max: {s.max():.2f}\n\n"

            # 2) PC
            r += "━"*80 + "\n2. PENSAMIENTO CRÍTICO [Likert 1-5]\n" + "━"*80 + "\n\n"
            pcs = [c for c in self.pc_cols if c in self.df_limpio.columns]
            if pcs:
                for c in pcs:
                    r += f"   • {c.replace('pc_', '').replace('_', ' ').title():20s}: {self.df_limpio[c].mean():.3f}\n"
                if 'pc_total' in self.df_limpio.columns:
                    r += f"\n   ► PC TOTAL: {self.df_limpio['pc_total'].mean():.3f}  (σ={self.df_limpio['pc_total'].std():.3f})\n\n"

            # 3) Distribuciones
            r += "━"*80 + "\n3. DISTRIBUCIONES\n" + "━"*80 + "\n\n"
            if 'metodo_estudio' in self.df_limpio.columns:
                r += "📖 MÉTODOS DE ESTUDIO:\n"
                for k, v in self.df_limpio['metodo_estudio'].value_counts().items():
                    r += f"   • {k:15s}: {v:4d} ({v/len(self.df_limpio)*100:5.1f}%)\n"
                r += "\n"
            if 'ia_frecuencia' in self.df_limpio.columns:
                r += "🤖 FRECUENCIA DE USO DE IA:\n"
                for k, v in self.df_limpio['ia_frecuencia'].value_counts().items():
                    r += f"   • {k:15s}: {v:4d} ({v/len(self.df_limpio)*100:5.1f}%)\n"
                r += "\n"
            if 'horas_bin' in self.df_limpio.columns:
                r += "⏱️  HORAS (bins):\n"
                for k, v in self.df_limpio['horas_bin'].value_counts().sort_index().items():
                    r += f"   • {str(k):10s}: {v:4d} ({v/len(self.df_limpio)*100:5.1f}%)\n"
                r += "\n"

            # 4) Relaciones
            r += "━"*80 + "\n4. RELACIONES: IA ↔ PC ↔ RENDIMIENTO\n" + "━"*80 + "\n\n"
            if {'ia_frecuencia', 'promedio_academico'}.issubset(self.df_limpio.columns):
                r += f"   {'Frecuencia IA':<15} {'N':<6} {'Prom.Acad.':<12} {'PC Total':<10}\n"
                r += f"   {'-'*15} {'-'*6} {'-'*12} {'-'*10}\n"
                g = self.df_limpio.groupby('ia_frecuencia').agg(
                    n=('ia_frecuencia', 'size'),
                    promedio_academico=('promedio_academico', 'mean'),
                    pc_total=('pc_total', 'mean')
                ).reset_index()
                for _, row in g.iterrows():
                    r += f"   {row['ia_frecuencia'][:15]:<15} {int(row['n']):<6d} {row['promedio_academico']:<12.3f} {row['pc_total']:<10.3f}\n"
                r += "\n"

            if {'metodo_estudio', 'promedio_academico'}.issubset(self.df_limpio.columns):
                r += f"   {'Método':<15} {'N':<6} {'Prom.Acad.':<12} {'PC Total':<10}\n"
                r += f"   {'-'*15} {'-'*6} {'-'*12} {'-'*10}\n"
                g = self.df_limpio.groupby('metodo_estudio').agg(
                    n=('metodo_estudio', 'size'),
                    promedio_academico=('promedio_academico', 'mean'),
                    pc_total=('pc_total', 'mean')
                ).reset_index()
                for _, row in g.iterrows():
                    r += f"   {row['metodo_estudio'][:15]:<15} {int(row['n']):<6d} {row['promedio_academico']:<12.3f} {row['pc_total']:<10.3f}\n"
                r += "\n"

            if {'horas_bin', 'promedio_academico'}.issubset(self.df_limpio.columns):
                r += f"   {'Horas/día':<15} {'N':<6} {'Prom.Acad.':<12} {'PC Total':<10}\n"
                r += f"   {'-'*15} {'-'*6} {'-'*12} {'-'*10}\n"
                g = self.df_limpio.groupby('horas_bin', observed=True).agg(
                    n=('horas_bin', 'size'),
                    promedio_academico=('promedio_academico', 'mean'),
                    pc_total=('pc_total', 'mean')
                ).reset_index()
                for _, row in g.iterrows():
                    r += f"   {str(row['horas_bin'])[:15]:<15} {int(row['n']):<6d} {row['promedio_academico']:<12.3f} {row['pc_total']:<10.3f}\n"
                r += "\n"

            # 5) Correlaciones
            r += "━"*80 + "\n5. CORRELACIONES (Pearson)\n" + "━"*80 + "\n\n"
            if {'horas_estudio_dia', 'promedio_academico'}.issubset(self.df_limpio.columns):
                r += f"   • Horas ↔ Promedio: {self.df_limpio['horas_estudio_dia'].corr(self.df_limpio['promedio_academico']):7.3f}\n"
            if {'pc_total', 'promedio_academico'}.issubset(self.df_limpio.columns):
                r += f"   • PC ↔ Promedio:    {self.df_limpio['pc_total'].corr(self.df_limpio['promedio_academico']):7.3f}\n"
            if {'pc_total', 'horas_estudio_dia'}.issubset(self.df_limpio.columns):
                r += f"   • PC ↔ Horas:       {self.df_limpio['pc_total'].corr(self.df_limpio['horas_estudio_dia']):7.3f}\n"
            r += "\n"

            # 6) Insights
            r += "━"*80 + "\n6. INSIGHTS Y RECOMENDACIONES\n" + "━"*80 + "\n\n"
            if {'horas_bin', 'promedio_academico'}.issubset(self.df_limpio.columns):
                means = self.df_limpio.groupby('horas_bin', observed=True)['promedio_academico'].mean()
                if len(means) >= 2 and means.iloc[-1] > means.iloc[0]:
                    r += "   ✓ Más horas de estudio se asocian con mejor rendimiento.\n"
                else:
                    r += "   ⚠ No hay evidencia clara de que más horas impliquen mejor rendimiento.\n"
            if {'pc_total', 'promedio_academico'}.issubset(self.df_limpio.columns):
                corr = self.df_limpio['pc_total'].corr(self.df_limpio['promedio_academico'])
                if corr > 0.3:
                    r += "   ✓ PC y rendimiento correlacionan positivamente: fortalecer PC puede mejorar el desempeño.\n"
                elif corr < -0.1:
                    r += "   ⚠ Correlación negativa: revisar sesgos o calidad de instrumentos.\n"
            if 'ia_frecuencia' in self.df_limpio.columns:
                n_ia = self.df_limpio[self.df_limpio['ia_frecuencia'].isin(['DIARIO', 'SEMANAL'])].shape[0]
                r += f"   📈 {n_ia/len(self.df_limpio)*100:.1f}% usa IA semanal o diariamente. Promover guías de uso responsable.\n\n"

            r += "📋 RECOMENDACIONES:\n" \
                 "   1) Promover uso crítico de IA como apoyo.\n" \
                 "   2) Diseñar actividades que evalúen calidad del estudio.\n" \
                 "   3) Integrar ejercicios de análisis, inferencia y evaluación.\n" \
                 "   4) Verificar información generada por IA.\n" \
                 "   5) Monitorear IA–PC–rendimiento durante el semestre.\n\n" \
                 + "="*80 + "\n" + "                              FIN DEL REPORTE\n" + "="*80 + "\n"

            self.txt_reporte.insert(tk.END, r)
            messagebox.showinfo("Éxito", "✓ Reporte completo generado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte:\n{str(e)}")


# ==================== MAIN ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = IAAnalisisApp(root)
    root.mainloop()


