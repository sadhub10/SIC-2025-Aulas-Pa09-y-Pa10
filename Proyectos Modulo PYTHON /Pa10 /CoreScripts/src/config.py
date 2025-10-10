import os
import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox
import pandas as pd

class FileSelector(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.file_path = None
        self.df = None

        # Container principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.mostrar_menu()

    def __del__(self):
        """Destructor para limpiar recursos"""
        self.cleanup()

    def cleanup(self):
        """Limpia recursos antes de destruir"""
        try:
            self.df = None
            self.file_path = None
        except:
            pass

    def mostrar_menu(self):
        """Muestra la vista principal con el botón para cargar CSV."""
        for widget in self.container.winfo_children():
            try:
                widget.destroy()
            except:
                pass

        # Título principal
        label_title = ctk.CTkLabel(
            self.container,
            text="📊 Heart Risk System",
            font=("Segoe UI", 32, "bold"),
            text_color="#00BFFF"
        )
        label_title.pack(pady=(60, 20))

        # Subtítulo
        label_sub = ctk.CTkLabel(
            self.container,
            text="Selecciona el archivo CSV del dataset para comenzar el análisis",
            font=("Segoe UI", 16),
            text_color="#CCCCCC"
        )
        label_sub.pack(pady=(0, 40))

        # Botón de carga
        self.btn_cargar = ctk.CTkButton(
            self.container,
            text="📂 Cargar archivo CSV",
            command=self.cargar_archivo,
            width=280,
            height=60,
            font=("Segoe UI", 16, "bold"),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_cargar.pack(pady=20)

        # Label de estado
        self.label_ruta = ctk.CTkLabel(
            self.container,
            text="Ningún archivo seleccionado.",
            font=("Segoe UI", 14),
            wraplength=700,
            text_color="#AAAAAA"
        )
        self.label_ruta.pack(pady=(20, 10))

        # Información adicional
        info_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        info_frame.pack(pady=(40, 0))

        info_text = """
        💡 Formatos aceptados: CSV
        📋 Asegúrate de que tu archivo contenga encabezados
        🔍 Se validará la estructura del archivo
        """
        
        label_info = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Segoe UI", 12),
            text_color="#888888",
            justify="left"
        )
        label_info.pack()

    def cargar_archivo(self):
        """Permite al usuario seleccionar un archivo CSV."""
        filetypes = [("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        ruta = filedialog.askopenfilename(
            title="Seleccionar dataset CSV",
            initialdir=os.getcwd(),
            filetypes=filetypes
        )

        if ruta:
            try:
                self.file_path = ruta
                self.df = pd.read_csv(ruta)
                nombre = os.path.basename(ruta)
                self.label_ruta.configure(text=f"✅ Archivo cargado: {nombre}")
                
                # Notificar al parent (MainApp) que se cargaron los datos
                if hasattr(self.parent, 'cargar_datos'):
                    self.parent.cargar_datos(self.df)
                
                # Mostrar tabla automáticamente
                self.after(500, self.mostrar_tabla)
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")
                self.label_ruta.configure(text="❌ Error al cargar el archivo.")
        else:
            self.label_ruta.configure(text="❌ No se seleccionó ningún archivo.")

    def mostrar_tabla(self):
        """Muestra la tabla del dataset."""
        for widget in self.container.winfo_children():
            try:
                widget.destroy()
            except:
                pass

        # Encabezado con información
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20))

        label_title = ctk.CTkLabel(
            header_frame,
            text="📋 Vista del Dataset",
            font=("Segoe UI", 24, "bold"),
            text_color="#00BFFF"
        )
        label_title.pack(side="left", padx=20)

        label_info = ctk.CTkLabel(
            header_frame,
            text=f"{len(self.df)} filas × {len(self.df.columns)} columnas",
            font=("Segoe UI", 14),
            text_color="#AAAAAA"
        )
        label_info.pack(side="left", padx=10)

        # Frame de tabla con estilo mejorado
        frame_tabla_container = ctk.CTkFrame(self.container)
        frame_tabla_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Configurar estilo del Treeview
        style = ttk.Style()
        style.theme_use("default")
        
        # Estilo para el body
        style.configure("Custom.Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       borderwidth=0,
                       font=("Segoe UI", 10))
        
        # Estilo para selección
        style.map('Custom.Treeview', 
                 background=[('selected', '#0078D7')])
        
        # Estilo para los headers
        style.configure("Custom.Treeview.Heading",
                       background="#1e1e1e",
                       foreground="white",
                       relief="flat",
                       font=("Segoe UI", 10, "bold"))
        
        style.map("Custom.Treeview.Heading",
                 background=[('active', '#0078D7')])

        # Crear Treeview
        tree = ttk.Treeview(
            frame_tabla_container, 
            columns=list(self.df.columns), 
            show='headings',
            style="Custom.Treeview"
        )
        
        # Configurar columnas
        for col in self.df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120, minwidth=80)

        # Insertar datos
        for idx, row in self.df.iterrows():
            values = [str(val) if pd.notna(val) else "" for val in row]
            # Alternar colores para mejor legibilidad
            tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)
            tree.insert("", "end", values=values, tags=tags)

        # Configurar tags para colores alternados
        tree.tag_configure('evenrow', background='#2b2b2b')
        tree.tag_configure('oddrow', background='#333333')

        # Scrollbars
        vsb = ttk.Scrollbar(frame_tabla_container, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame_tabla_container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        # Botones inferiores
        frame_botones = ctk.CTkFrame(self.container, fg_color="transparent")
        frame_botones.pack(pady=20)

        btn_regresar = ctk.CTkButton(
            frame_botones,
            text="← Volver",
            command=self.mostrar_menu,
            width=160,
            height=45,
            font=("Segoe UI", 14),
            fg_color="#444",
            hover_color="#666"
        )
        btn_regresar.pack(side="left", padx=10)

        btn_stats = ctk.CTkButton(
            frame_botones,
            text="📊 Ver estadísticas",
            command=self.mostrar_estadisticas,
            width=180,
            height=45,
            font=("Segoe UI", 14),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        btn_stats.pack(side="left", padx=10)

        btn_continuar = ctk.CTkButton(
            frame_botones,
            text="Continuar al preprocesamiento →",
            command=self.ir_a_preprocesamiento,
            width=250,
            height=45,
            font=("Segoe UI", 14),
            fg_color="#00AA00",
            hover_color="#008800"
        )
        btn_continuar.pack(side="left", padx=10)

    def mostrar_estadisticas(self):
        """Muestra estadísticas descriptivas del dataset"""
        for widget in self.container.winfo_children():
            try:
                widget.destroy()
            except:
                pass

        # Encabezado
        label_title = ctk.CTkLabel(
            self.container,
            text="📈 Estadísticas Descriptivas",
            font=("Segoe UI", 24, "bold"),
            text_color="#00BFFF"
        )
        label_title.pack(pady=(10, 20))

        # Frame scrollable para las estadísticas
        scrollable = ctk.CTkScrollableFrame(self.container)
        scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Información general
        info_frame = ctk.CTkFrame(scrollable, fg_color="#1e1e1e")
        info_frame.pack(fill="x", pady=10, padx=10)

        info_text = f"""
📊 INFORMACIÓN GENERAL DEL DATASET

Dimensiones:        {self.df.shape[0]} filas × {self.df.shape[1]} columnas
Valores nulos:      {self.df.isnull().sum().sum()} ({(self.df.isnull().sum().sum() / (self.df.shape[0] * self.df.shape[1]) * 100):.2f}%)
Duplicados:         {self.df.duplicated().sum()}
Memoria usada:      {self.df.memory_usage(deep=True).sum() / 1024:.2f} KB

Tipos de datos:
{self.df.dtypes.value_counts().to_string()}
        """
        
        label_info = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Courier", 11),
            justify="left",
            text_color="#CCCCCC"
        )
        label_info.pack(pady=15, padx=15, anchor="w")

        # Separador
        separator = ctk.CTkLabel(
            scrollable,
            text="─" * 80,
            font=("Segoe UI", 10),
            text_color="#444444"
        )
        separator.pack(pady=10)

        # Estadísticas descriptivas numéricas
        label_numeric = ctk.CTkLabel(
            scrollable,
            text="📊 Estadísticas de Variables Numéricas",
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        )
        label_numeric.pack(pady=(10, 10), anchor="w", padx=10)

        stats_df = self.df.describe()
        
        frame_stats = ctk.CTkFrame(scrollable)
        frame_stats.pack(fill="both", expand=True, pady=10, padx=10)

        # Configurar estilo
        style = ttk.Style()
        style.configure("Stats.Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       font=("Courier", 10))
        style.configure("Stats.Treeview.Heading",
                       background="#1e1e1e",
                       foreground="white",
                       font=("Segoe UI", 10, "bold"))

        tree_stats = ttk.Treeview(
            frame_stats, 
            columns=['stat'] + list(stats_df.columns), 
            show='headings',
            style="Stats.Treeview"
        )
        
        tree_stats.heading('stat', text='Estadística')
        tree_stats.column('stat', width=120, anchor='w')

        for col in stats_df.columns:
            tree_stats.heading(col, text=col)
            tree_stats.column(col, anchor="center", width=100)

        for idx, row in stats_df.iterrows():
            values = [idx] + [f"{val:.2f}" if isinstance(val, float) else str(val) for val in row]
            tree_stats.insert("", "end", values=values)

        vsb = ttk.Scrollbar(frame_stats, orient="vertical", command=tree_stats.yview)
        hsb = ttk.Scrollbar(frame_stats, orient="horizontal", command=tree_stats.xview)
        tree_stats.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree_stats.pack(fill="both", expand=True)

        # Valores nulos por columna
        if self.df.isnull().sum().sum() > 0:
            label_nulls = ctk.CTkLabel(
                scrollable,
                text="⚠️ Valores Nulos por Columna",
                font=("Segoe UI", 16, "bold"),
                text_color="#FFAA00"
            )
            label_nulls.pack(pady=(20, 10), anchor="w", padx=10)

            null_frame = ctk.CTkFrame(scrollable, fg_color="#1e1e1e")
            null_frame.pack(fill="x", pady=10, padx=10)

            null_info = ""
            for col in self.df.columns:
                nulls = self.df[col].isnull().sum()
                if nulls > 0:
                    pct = (nulls / len(self.df)) * 100
                    null_info += f"  {col:<25} {nulls:>5} ({pct:>5.2f}%)\n"

            if null_info:
                label_null_detail = ctk.CTkLabel(
                    null_frame,
                    text=null_info,
                    font=("Courier", 10),
                    justify="left",
                    text_color="#CCCCCC"
                )
                label_null_detail.pack(pady=10, padx=15, anchor="w")

        # Botones de navegación
        nav_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        nav_frame.pack(pady=20)

        btn_volver = ctk.CTkButton(
            nav_frame,
            text="← Volver a la tabla",
            command=self.mostrar_tabla,
            width=180,
            height=45,
            font=("Segoe UI", 14),
            fg_color="#444",
            hover_color="#666"
        )
        btn_volver.pack(side="left", padx=10)

        btn_menu = ctk.CTkButton(
            nav_frame,
            text="🏠 Menú principal",
            command=self.mostrar_menu,
            width=180,
            height=45,
            font=("Segoe UI", 14),
            fg_color="#666",
            hover_color="#888"
        )
        btn_menu.pack(side="left", padx=10)

    def ir_a_preprocesamiento(self):
        """Navega al módulo de preprocesamiento"""
        if hasattr(self.parent, 'mostrar_procesamiento'):
            self.parent.mostrar_procesamiento()
        else:
            messagebox.showinfo(
                "Información", 
                "Usa el menú lateral para ir a 'Preprocesar'"
            )