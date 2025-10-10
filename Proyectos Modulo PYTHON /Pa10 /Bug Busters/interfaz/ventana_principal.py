import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class VentanaPrincipal(tk.Tk): #Interfaz gráfica principal de BusPredict

    def __init__(self, analizador, predictor, buscador):
        super().__init__()

        # Propiedades principales
        self.title("BusPredict - Sistema de Transporte Público")
        self.geometry("1150x700")
        self.configure(bg="#F5F5F5")

        self.analizador = analizador
        self.predictor = predictor
        self.buscador = buscador

        self._construir_interfaz()

    # =====================================================
    # Estructura General
    # =====================================================
    def _construir_interfaz(self):
        # Encabezado superior
        header = tk.Frame(self, bg="#283593", height=80)
        header.pack(fill="x")

        tk.Label(
            header, text="🚌  BusPredict",
            fg="white", bg="#283593",
            font=("Segoe UI", 22, "bold")
        ).pack(side="left", padx=25)
        tk.Label(
            header, text="Predicción y análisis diario del transporte público",
            fg="white", bg="#283593", font=("Segoe UI", 12)
        ).pack(side="left", padx=15)

        # Menú lateral
        self.menu_frame = tk.Frame(self, bg="#E8EAF6", width=220)
        self.menu_frame.pack(fill="y", side="left")

        tk.Label(
            self.menu_frame, text="MENÚ PRINCIPAL",
            bg="#3F51B5", fg="white", font=("Segoe UI", 12, "bold")
        ).pack(fill="x", pady=(0, 10))

        self._crear_boton_menu("🏠 Inicio", self._mostrar_inicio)
        self._crear_boton_menu("🔍 Buscar Ruta", self._mostrar_busqueda_origen_destino)
        self._crear_boton_menu("📊 Análisis del Día", self._mostrar_analisis_dia)
        self._crear_boton_menu("❌ Salir", self.destroy)

        # Contenedor central
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(fill="both", expand=True)

        # Mostrar pantalla inicial
        self._mostrar_inicio()

        # Pie de página
        footer = tk.Label(
            self,
            text="© 2025 Samsung Innovation Campus | BusPredict UTP",
            bg="#E8EAF6", fg="#333333", font=("Segoe UI", 9)
        )
        footer.pack(fill="x", side="bottom")

    def _crear_boton_menu(self, texto, comando):
        tk.Button(
            self.menu_frame, text=texto, bg="#5C6BC0", fg="white",
            font=("Segoe UI", 11, "bold"), relief="flat",
            activebackground="#3949AB", activeforeground="white",
            command=comando
        ).pack(fill="x", padx=15, pady=8)

    # =====================================================
    # Pantalla de inicio limpia
    # =====================================================
    def _mostrar_inicio(self):
        self._limpiar_contenido()

        bg_color = "#F5F6FA"
        accent_color = "#283593"
        self.content_frame.config(bg=bg_color)

        # Encabezado principal
        header = tk.Frame(self.content_frame, bg=accent_color, height=110)
        header.pack(fill="x", pady=(0, 20))

        tk.Label(
            header, text="BusPredict",
            font=("Segoe UI", 28, "bold"), bg=accent_color, fg="white"
        ).pack(pady=(18, 0))

        tk.Label(
            header,
            text="Sistema Inteligente de Predicción de Transporte Público",
            font=("Segoe UI", 12), bg=accent_color, fg="#C5CAE9"
        ).pack(pady=(0, 10))

        # Texto de bienvenida simple
        bienvenida = (
            "Bienvenido a BusPredict, una herramienta desarrollada por estudiantes del "
            "Samsung Innovation Campus - UTP.\n"
            "Explora las opciones del menú lateral para consultar rutas o analizar la operación del día."
        )
        tk.Label(
            self.content_frame, text=bienvenida,
            font=("Segoe UI", 12), bg=bg_color, fg="#333333",
            justify="center", wraplength=800
        ).pack(pady=60)

        # Sección de desarrolladores (ahora al final, más discreta)
        equipo_frame = tk.Frame(self.content_frame, bg="#E8EAF6", bd=1, relief="solid")
        equipo_frame.pack(side="bottom", pady=40, ipadx=10, ipady=5)

        tk.Label(
            equipo_frame, text="Desarrollado por:",
            font=("Segoe UI", 10, "bold"), bg="#E8EAF6", fg="#1A237E"
        ).pack()

        tk.Label(
            equipo_frame,
            text="Juan Castillo   •   Joseph Batista   •   Marco Rodríguez   •   Laura Rivera",
            font=("Segoe UI", 9), bg="#E8EAF6", fg="#3F51B5"
        ).pack(pady=(3, 0))

    # =====================================================
    #Buscar Ruta
    # =====================================================
    def _mostrar_busqueda_origen_destino(self):
        self._limpiar_contenido()
        tk.Label(
            self.content_frame, text="🧭 Buscar Ruta por Origen y Destino",
            font=("Segoe UI", 20, "bold"), bg="white"
        ).pack(pady=25)

        form = tk.Frame(self.content_frame, bg="white")
        form.pack(pady=10)

        tk.Label(form, text="Origen:", font=("Segoe UI", 12), bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_origen = tk.Entry(form, font=("Segoe UI", 12), width=30)
        self.entry_origen.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(form, text="Destino:", font=("Segoe UI", 12), bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_destino = tk.Entry(form, font=("Segoe UI", 12), width=30)
        self.entry_destino.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(
            self.content_frame, text="Buscar Rutas Posibles",
            font=("Segoe UI", 11, "bold"), bg="#3949AB", fg="white",
            relief="flat", padx=20, pady=5, command=self._buscar_rutas
        ).pack(pady=15)

    def _buscar_rutas(self):
        origen = self.entry_origen.get().strip()
        destino = self.entry_destino.get().strip()

        if not origen or not destino:
            messagebox.showwarning("Atención", "Debes ingresar tanto el origen como el destino.")
            return

        rutas = self.buscador.buscar_rutas(origen, destino)
        self._limpiar_contenido()

        if rutas.empty:
            tk.Label(
                self.content_frame,
                text=f"No se encontraron rutas entre '{origen}' y '{destino}'.",
                font=("Segoe UI", 12), bg="white"
            ).pack(pady=30)
            return

        tk.Label(
            self.content_frame, text=f"Rutas entre '{origen}' y '{destino}':",
            font=("Segoe UI", 14, "bold"), bg="white"
        ).pack(pady=10)

        for _, row in rutas.iterrows():
            texto = f"{row['id_ruta']} - {row['nombre_ruta']} ({row['via']})"
            tk.Button(
                self.content_frame, text=texto, font=("Segoe UI", 10),
                bg="#5C6BC0", fg="white", relief="flat", width=75,
                command=lambda r=row: self._mostrar_resultados_ruta(r["id_ruta"], r["nombre_ruta"])
            ).pack(pady=5)

    # =====================================================
    # Resultados de Ruta
    # =====================================================
    def _mostrar_resultados_ruta(self, id_ruta, nombre_ruta):
        self._limpiar_contenido()
        tk.Label(
            self.content_frame, text=f"📍 Ruta seleccionada: {nombre_ruta}",
            font=("Segoe UI", 18, "bold"), bg="white"
        ).pack(pady=20)

        try:
            self.predictor.preparar_modelo()
            predicciones, _ = self.predictor.predecir_dia_completo(id_ruta, "laboral")

            promedio = predicciones["intervalo_predicho"].mean()
            hora_min = int(predicciones.loc[predicciones["intervalo_predicho"].idxmin(), "hora"])
            hora_max = int(predicciones.loc[predicciones["intervalo_predicho"].idxmax(), "hora"])

            info_frame = tk.Frame(self.content_frame, bg="white")
            info_frame.pack(pady=10)

            def tarjeta(titulo, valor, color):
                frame = tk.Frame(info_frame, bg=color, width=240, height=90)
                frame.pack_propagate(False)
                frame.pack(side="left", padx=10)
                tk.Label(frame, text=titulo, bg=color, fg="white", font=("Segoe UI", 10, "bold")).pack(pady=(10, 0))
                tk.Label(frame, text=valor, bg=color, fg="white", font=("Segoe UI", 14, "bold")).pack(pady=(0, 5))

            tarjeta("🕒 Promedio del Día", f"{promedio:.1f} min", "#3949AB")
            tarjeta("🌅 Mejor Hora", f"{hora_min:02d}:00 h", "#2E7D32")
            tarjeta("🌇 Peor Hora", f"{hora_max:02d}:00 h", "#C62828")

            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(predicciones["hora"], predicciones["intervalo_predicho"], marker="o")
            ax.set_title("Intervalo Promedio por Hora", fontsize=11, fontweight="bold")
            ax.set_xlabel("Hora del Día")
            ax.set_ylabel("Minutos")
            ax.grid(True, linestyle="--", alpha=0.6)

            canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

            tk.Button(
                self.content_frame, text="⬅ Volver a la búsqueda",
                font=("Segoe UI", 11, "bold"), bg="#3949AB", fg="white",
                relief="flat", padx=20, pady=5,
                command=self._mostrar_busqueda_origen_destino
            ).pack(pady=15)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")

    # =====================================================
    # 📅 Análisis del Día 
    # =====================================================
    def _mostrar_analisis_dia(self):
        """Menú de selección de métricas del día"""
        self._limpiar_contenido()

        # Fondo neutro y padding general
        self.content_frame.config(bg="#F5F6FA")

        container = tk.Frame(self.content_frame, bg="white", bd=1, relief="solid")
        container.pack(pady=50, ipadx=30, ipady=30)

        tk.Label(
            container, text="📊  Análisis del Día",
            font=("Segoe UI", 20, "bold"), bg="white", fg="#1A237E"
        ).pack(pady=(0, 15))

        tk.Label(
            container, text="Selecciona una métrica para visualizar:",
            font=("Segoe UI", 12), bg="white", fg="#333333"
        ).pack(pady=(0, 15))

        # Opciones disponibles
        opciones = [
            ("🏆  Top 10 rutas más transitadas", self._grafico_top_rutas),
            ("⏱️  Promedio de intervalos por ruta", self._grafico_intervalos_promedio),
            ("🕓  Distribución de eventos por hora", self._grafico_distribucion_horaria),
            ("⚖️  Rutas con mayor variabilidad", self._grafico_rutas_inestables)
        ]

        botones_frame = tk.Frame(container, bg="white")
        botones_frame.pack(pady=10)

        for texto, funcion in opciones:
            tk.Button(
                botones_frame,
                text=texto,
                font=("Segoe UI", 11, "bold"),
                bg="#5C6BC0",
                fg="white",
                relief="flat",
                activebackground="#3949AB",
                width=50,
                height=2,
                command=funcion
            ).pack(pady=8)

        # Botón para volver al inicio
        tk.Button(
            container,
            text="⬅  Volver al Menú Principal",
            font=("Segoe UI", 10, "bold"),
            bg="#3949AB", fg="white",
            relief="flat", padx=15, pady=6,
            activebackground="#1A237E",
            command=self._mostrar_inicio
        ).pack(pady=(25, 0))

            # ---------------- gráficos (envoltorio) ----------------
    def _grafico_top_rutas(self):
        self._mostrar_grafico_unico("🏆 Top 10 rutas más transitadas", self._generar_top_rutas)

    def _grafico_intervalos_promedio(self):
        self._mostrar_grafico_unico("⏱️ Promedio de intervalos por ruta", self._generar_intervalos_promedio)

    def _grafico_distribucion_horaria(self):
        self._mostrar_grafico_unico("🕓 Distribución de eventos por hora", self._generar_distribucion_horaria)

    def _grafico_rutas_inestables(self):
        self._mostrar_grafico_unico("⚖️ Rutas con mayor variabilidad", self._generar_rutas_inestables)

    # ---------------- render genérico ----------------
    def _mostrar_grafico_unico(self, titulo, funcion_generadora):
        """Renderiza una sola figura con botón de volver"""
        self._limpiar_contenido()

        tk.Label(self.content_frame, text=titulo,
                 font=("Segoe UI", 18, "bold"), bg="white").pack(pady=15)

        try:
            fig = funcion_generadora()
            canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el gráfico:\n{e}")

        tk.Button(self.content_frame, text="⬅ Volver a métricas",
                  bg="#3949AB", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=15, pady=5,
                  command=self._mostrar_analisis_dia).pack(pady=10)

    # ---------------- generadores de figuras ----------------
    def _generar_top_rutas(self):
        resultados = self.analizador.generar_reporte_completo()
        top_rutas = resultados["top_rutas"].head(10)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(top_rutas["nombre_ruta"], top_rutas["pasajeros_totales"])
        ax.set_xlabel("Total de pasajeros")
        ax.set_ylabel("Ruta")
        ax.set_title("Top 10 rutas más transitadas del día", fontsize=11, fontweight="bold")
        plt.tight_layout()
        return fig

    def _generar_intervalos_promedio(self):
        intervalos = self.analizador.intervalos_por_ruta(top_n=10)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(intervalos["nombre_ruta"], intervalos["intervalo_promedio"])
        ax.set_ylabel("Intervalo promedio (min)")
        ax.set_title("Promedio de intervalos entre buses por ruta", fontsize=11, fontweight="bold")
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        return fig

    def _generar_distribucion_horaria(self):
        resultados = self.analizador.generar_reporte_completo()
        dist = resultados["distribucion_hora"]
        horas = list(dist["eventos_por_hora"].keys())
        valores = list(dist["eventos_por_hora"].values())
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(horas, valores)
        ax.set_xlabel("Hora del día")
        ax.set_ylabel("Número de eventos")
        ax.set_title("Distribución de eventos por hora", fontsize=11, fontweight="bold")
        plt.tight_layout()
        return fig

    def _generar_rutas_inestables(self):
        intervalos = self.analizador.intervalos_por_ruta(top_n=30)
        intervalos = intervalos.sort_values("intervalo_desviacion", ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(intervalos["nombre_ruta"], intervalos["intervalo_desviacion"])
        ax.set_xlabel("Desviación estándar (min)")
        ax.set_title("Rutas con mayor variabilidad en intervalos", fontsize=11, fontweight="bold")
        plt.tight_layout()
        return fig

    # =====================================================
    # Limpieza
    # =====================================================
    def _limpiar_contenido(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

