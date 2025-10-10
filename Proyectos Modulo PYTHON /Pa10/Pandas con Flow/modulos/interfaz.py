import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class InterfazManager:
    """Clase para manejar la interfaz principal del sistema"""
    
    def __init__(self, root, datos_manager, graficos_manager, clima_manager):
        self.root = root
        self.datos_manager = datos_manager
        self.graficos_manager = graficos_manager
        self.clima_manager = clima_manager
        
        # Variables de estado
        self.cultivo_actual = None
        
        # Elementos de la interfaz
        self.texto_resultados = None
        self.entrada_cultivo = None
        self.barra_estado = None
        self.boton_analisis = None
        self.boton_clima = None
        self.boton_grafico_cultivo = None
        
    def configurar_interfaz(self):
        """Configura la interfaz principal del sistema optimizada sin scroll"""
        # Frame principal
        frame_principal = tk.Frame(self.root, bg="lightgray")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título más compacto
        titulo = tk.Label(frame_principal, 
                         text="ASISTENTE AGRICOLA - PANAMA", 
                         font=("Arial", 14, "bold"), 
                         bg="lightgray", fg="darkgreen")
        titulo.pack(pady=5)
        
        # Crear layout de dos columnas
        frame_columnas = tk.Frame(frame_principal, bg="lightgray")
        frame_columnas.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Columna izquierda
        columna_izq = tk.Frame(frame_columnas, bg="lightgray")
        columna_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Columna derecha  
        columna_der = tk.Frame(frame_columnas, bg="lightgray")
        columna_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Búsqueda en columna izquierda
        self._crear_frame_busqueda_compacto(columna_izq)
        
        # Resultados en columna izquierda
        self._crear_frame_resultados_compacto(columna_izq)
        
        # Acciones en columna derecha
        self._crear_frame_acciones_compacto(columna_der)
        
        # Clima en columna derecha
        self._crear_frame_clima_compacto(columna_der)
        
        # Barra de estado en la parte inferior
        self._crear_barra_estado()
    
    def _crear_frame_busqueda_compacto(self, parent):
        """Crea el frame de búsqueda de cultivos compacto"""
        frame_busqueda = tk.LabelFrame(parent, text="Búsqueda", 
                                      font=("Arial", 10, "bold"), bg="lightgray")
        frame_busqueda.pack(fill=tk.X, pady=3)
        
        # Frame para entrada y botón
        frame_entrada = tk.Frame(frame_busqueda, bg="lightgray")
        frame_entrada.pack(pady=3)
        
        self.entrada_cultivo = tk.Entry(frame_entrada, font=("Arial", 11), width=25)
        self.entrada_cultivo.pack(side=tk.LEFT, padx=3)
        
        tk.Button(frame_entrada, text="Buscar", command=self.buscar_cultivo,
                 bg="green", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=3)
        
        tk.Button(frame_entrada, text="Limpiar", command=self.limpiar_resultados,
                 bg="red", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=3)
        
        # Frame para cultivos sugeridos - versión compacta
        frame_sugerencias = tk.Frame(frame_busqueda, bg="lightgray")
        frame_sugerencias.pack(fill=tk.X, pady=2)
        
        # Obtener todos los cultivos disponibles
        todos_cultivos = self.datos_manager.obtener_lista_cultivos()
        
        # Crear botones de cultivos en filas de 5 para acomodar los 25 cultivos
        for i in range(0, len(todos_cultivos), 5):
            frame_fila = tk.Frame(frame_sugerencias, bg="lightgray")
            frame_fila.pack(fill=tk.X, pady=1)
            
            for j in range(i, min(i + 5, len(todos_cultivos))):
                cultivo = todos_cultivos[j]
                btn = tk.Button(frame_fila, text=cultivo, 
                               command=lambda c=cultivo: self._seleccionar_cultivo_sugerido(c),
                               bg="lightblue", fg="darkblue", font=("Arial", 8),
                               relief=tk.RAISED, bd=1)
                btn.pack(side=tk.LEFT, padx=1, pady=1, fill=tk.X, expand=True)
    
    def _crear_frame_resultados_compacto(self, parent):
        """Crea el frame para mostrar resultados de forma compacta"""
        frame_resultados = tk.LabelFrame(parent, text="Información", 
                                        font=("Arial", 10, "bold"), bg="lightgray")
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=3)
        
        self.texto_resultados = scrolledtext.ScrolledText(frame_resultados, 
                                                         height=12, width=50, 
                                                         font=("Arial", 9))
        self.texto_resultados.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Mensaje inicial compacto
        mensaje_inicial = """Asistente Agrícola - Panamá

INSTRUCCIONES:
1. Seleccione un cultivo
2. Obtenga información detallada  
3. Use botones de análisis

Cultivos: Arroz, Maíz, Frijol, Plátano, Yuca,
Ñame, Café, Cacao, Naranja, Mango, etc.
        """
        self.texto_resultados.insert(tk.END, mensaje_inicial)
    
    def _crear_frame_acciones_compacto(self, parent):
        """Crea el frame con botones de acciones de forma compacta"""
        frame_acciones = tk.LabelFrame(parent, text="Acciones", 
                                      font=("Arial", 10, "bold"), bg="lightgray")
        frame_acciones.pack(fill=tk.X, pady=3)
        
        # Botones principales
        frame_botones1 = tk.Frame(frame_acciones, bg="lightgray")
        frame_botones1.pack(fill=tk.X, pady=2)
        
        self.boton_analisis = tk.Button(frame_botones1, text="Análisis", 
                                       command=self.mostrar_analisis_detallado,
                                       bg="blue", fg="white", font=("Arial", 9),
                                       state=tk.DISABLED)
        self.boton_analisis.pack(fill=tk.X, pady=1)
        
        self.boton_grafico_cultivo = tk.Button(frame_botones1, text="Gráficos", 
                                              command=self.generar_grafico_cultivo,
                                              bg="purple", fg="white", font=("Arial", 9),
                                              state=tk.DISABLED)
        self.boton_grafico_cultivo.pack(fill=tk.X, pady=1)
        
        self.boton_clima = tk.Button(frame_botones1, text="Clima", 
                                    command=self.verificar_clima,
                                    bg="orange", fg="white", font=("Arial", 9),
                                    state=tk.DISABLED)
        self.boton_clima.pack(fill=tk.X, pady=1)
        
        # Botones adicionales
        frame_botones2 = tk.Frame(frame_acciones, bg="lightgray")
        frame_botones2.pack(fill=tk.X, pady=2)
        
        tk.Button(frame_botones2, text="Dataset", 
                 command=lambda: self.datos_manager.mostrar_dataset(self.root),
                 bg="teal", fg="white", font=("Arial", 9)).pack(fill=tk.X, pady=1)
        
        tk.Button(frame_botones2, text="Estadísticas", 
                 command=lambda: self.datos_manager.mostrar_estadisticas(self.root),
                 bg="darkgreen", fg="white", font=("Arial", 9)).pack(fill=tk.X, pady=1)
        
        tk.Button(frame_botones2, text="Rendimientos", 
                 command=self.mostrar_grafico_rendimientos,
                 bg="maroon", fg="white", font=("Arial", 9)).pack(fill=tk.X, pady=1)
        
        # Separador y botón cerrar
        tk.Frame(frame_acciones, height=10, bg="lightgray").pack(pady=5)
        
        tk.Button(frame_acciones, text="CERRAR APLICACION", 
                 command=self.cerrar_aplicacion,
                 bg="red", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=5)
    
    def _crear_frame_clima_compacto(self, parent):
        """Crea el frame de información climática de forma compacta"""
        frame_clima = tk.LabelFrame(parent, text="Clima", 
                                   font=("Arial", 10, "bold"), bg="lightgray")
        frame_clima.pack(fill=tk.X, pady=3)
        
        # Labels para información del clima - más compactos
        self.label_ubicacion = tk.Label(frame_clima, text="Ubicación: No configurada", 
                                       font=("Arial", 8), bg="lightgray")
        self.label_ubicacion.pack(anchor=tk.W, padx=3, pady=1)
        
        self.label_temperatura = tk.Label(frame_clima, text="Temp: No disponible", 
                                         font=("Arial", 8), bg="lightgray")
        self.label_temperatura.pack(anchor=tk.W, padx=3, pady=1)
        
        self.label_humedad = tk.Label(frame_clima, text="Humedad: No disponible", 
                                     font=("Arial", 8), bg="lightgray")
        self.label_humedad.pack(anchor=tk.W, padx=3, pady=1)
        
        self.label_clima_desc = tk.Label(frame_clima, text="Condiciones: No disponible", 
                                        font=("Arial", 8), bg="lightgray")
        self.label_clima_desc.pack(anchor=tk.W, padx=3, pady=1)
        
        # Configurar elementos en el clima manager
        self.clima_manager.configurar_elementos_interfaz(
            self.label_ubicacion, self.label_temperatura, 
            self.label_humedad, self.label_clima_desc
        )
        
        # Botones de clima más compactos
        frame_botones_clima = tk.Frame(frame_clima, bg="lightgray")
        frame_botones_clima.pack(fill=tk.X, pady=2)
        
        tk.Button(frame_botones_clima, text="Actualizar", 
                 command=self.clima_manager.actualizar_interfaz_clima,
                 bg="skyblue", fg="black", font=("Arial", 8)).pack(fill=tk.X, pady=1)
        
        tk.Button(frame_botones_clima, text="Consultar Ciudad", 
                 command=lambda: self.clima_manager.consultar_clima_ciudad(self.root),
                 bg="lightcoral", fg="black", font=("Arial", 8)).pack(fill=tk.X, pady=1)
    
    def _crear_barra_estado(self):
        """Crea la barra de estado"""
        self.barra_estado = tk.Label(self.root, text="Sistema listo - Seleccione un cultivo para comenzar", 
                                    relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9))
        self.barra_estado.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Configurar barra de estado en los managers
        self.graficos_manager.barra_estado = self.barra_estado
        self.clima_manager.barra_estado = self.barra_estado
        self.datos_manager.barra_estado = self.barra_estado
    

    
    def _seleccionar_cultivo_sugerido(self, cultivo):
        """Selecciona un cultivo de las sugerencias"""
        self.entrada_cultivo.delete(0, tk.END)
        self.entrada_cultivo.insert(0, cultivo)
        self.buscar_cultivo()
    
    def buscar_cultivo(self):
        """Busca y muestra información del cultivo"""
        nombre_cultivo = self.entrada_cultivo.get().strip()
        
        if not nombre_cultivo:
            messagebox.showwarning("Advertencia", "Ingrese el nombre del cultivo")
            return
        
        # Buscar en el dataset
        cultivo_encontrado = self.datos_manager.buscar_cultivo(nombre_cultivo)
        
        if cultivo_encontrado is not None:
            self.cultivo_actual = cultivo_encontrado
            self.mostrar_informacion(self.cultivo_actual)
            
            # Habilitar botones
            self.boton_analisis.config(state=tk.NORMAL)
            self.boton_clima.config(state=tk.NORMAL)
            self.boton_grafico_cultivo.config(state=tk.NORMAL)
            
            self.barra_estado.config(text=f"Cultivo encontrado: {self.cultivo_actual['cultivo']}")
        else:
            messagebox.showinfo("No encontrado", 
                               f"Cultivo '{nombre_cultivo}' no encontrado en la base de datos")
            self.texto_resultados.delete(1.0, tk.END)
            self.boton_analisis.config(state=tk.DISABLED)
            self.boton_clima.config(state=tk.DISABLED)
            self.boton_grafico_cultivo.config(state=tk.DISABLED)
            self.barra_estado.config(text=f"Cultivo '{nombre_cultivo}' no encontrado")
    
    def limpiar_interfaz(self):
        """Limpia la interfaz y restablece valores por defecto"""
        # Limpiar campo de entrada
        self.entrada_cultivo.delete(0, tk.END)
        
        # Limpiar área de resultados y mostrar mensaje inicial
        self.texto_resultados.delete(1.0, tk.END)
        
        # Mensaje inicial por defecto
        mensaje_inicial = """
ASISTENTE PARA AGRICULTORES - PANAMA

INSTRUCCIONES:
1. Busque un cultivo usando el campo de arriba
2. Seleccione uno de los cultivos disponibles (botones azules)
3. Obtenga información detallada y recomendaciones
4. Use los botones de análisis y gráficos para más detalles

CULTIVOS DISPONIBLES EN EL SISTEMA:
- Granos Básicos: Arroz, Maíz, Frijol, Sorgo
- Tubérculos: Yuca, Ñame, Ñampí, Papa
- Plátanos: Plátano, Banano
- Frutas: Naranja, Limón, Mango, Papaya, Piña, Aguacate, Coco
- Hortalizas: Tomate, Cebolla, Pimiento, Lechuga, Repollo
- Cultivos Especiales: Café, Cacao, Caña de Azúcar

FUNCIONES PRINCIPALES:
- "Análisis Detallado": Comparaciones y estadísticas avanzadas
- "Generar Gráfico": Visualizaciones profesionales del cultivo
- "Verificar Clima": Compatibilidad con condiciones actuales

CONSEJO: Haga clic en cualquiera de los botones azules de cultivos para comenzar
        """
        self.texto_resultados.insert(tk.END, mensaje_inicial)
        
        # Deshabilitar botones de acción
        self.boton_analisis.config(state=tk.DISABLED)
        self.boton_clima.config(state=tk.DISABLED)
        self.boton_grafico_cultivo.config(state=tk.DISABLED)
        
        # Restablecer cultivo actual
        self.cultivo_actual = None
        
        # Actualizar barra de estado
        self.barra_estado.config(text="Sistema listo - Seleccione un cultivo para comenzar")
        
        # Enfocar el campo de entrada
        self.entrada_cultivo.focus()
    
    def mostrar_informacion(self, cultivo):
        """Muestra la información detallada del cultivo"""
        self.texto_resultados.delete(1.0, tk.END)
        
        info = f"""
CULTIVO: {cultivo['cultivo'].upper()}
{'='*50}

DATOS BÁSICOS:
- Temporada de siembra: {cultivo['temporada_siembra']}
- Tiempo de cosecha: {cultivo['tiempo_cosecha']}
- Temperatura ideal: {cultivo['temperatura_ideal']}
- Nivel de lluvia requerido: {cultivo['lluvia']}
- Rendimiento promedio: {cultivo['rendimiento_promedio']}

RECOMENDACIONES:
{cultivo['recomendaciones']}

ANÁLISIS RÁPIDO:
- Use 'Análisis Detallado' para comparaciones con otros cultivos
- Use 'Generar Gráfico' para visualizaciones específicas
- Use 'Verificar Clima' para compatibilidad climática actual

Consulta realizada: {cultivo['cultivo']} - Sistema listo para análisis
        """
        
        self.texto_resultados.insert(tk.END, info)
    
    def mostrar_analisis_detallado(self):
        """Muestra análisis detallado del cultivo actual"""
        if self.cultivo_actual is None:
            messagebox.showwarning("Advertencia", "Seleccione un cultivo primero")
            return
        
        ventana_analisis = tk.Toplevel(self.root)
        ventana_analisis.title(f"Análisis Detallado - {self.cultivo_actual['cultivo']}")
        ventana_analisis.geometry("800x600")
        
        # Notebook para pestañas
        notebook = ttk.Notebook(ventana_analisis)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña 1: Información general
        frame_general = ttk.Frame(notebook)
        notebook.add(frame_general, text="Información General")
        
        texto_general = scrolledtext.ScrolledText(frame_general, font=("Arial", 11))
        texto_general.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        cultivo = self.cultivo_actual
        
        info_general = f"""
ANÁLISIS DETALLADO - {cultivo['cultivo'].upper()}
{'='*50}

INFORMACIÓN COMPLETA:

Cultivo: {cultivo['cultivo']}
Temporada óptima de siembra: {cultivo['temporada_siembra']}
Tiempo hasta cosecha: {cultivo['tiempo_cosecha']}
Temperatura ideal: {cultivo['temperatura_ideal']}
Requerimientos de lluvia: {cultivo['lluvia']}
Rendimiento esperado: {cultivo['rendimiento_promedio']}

RECOMENDACIONES DETALLADAS:
{cultivo['recomendaciones']}

ANÁLISIS COMPARATIVO:
        """
        
        # Agregar análisis comparativo
        try:
            rendimiento_actual = float(cultivo['rendimiento_promedio'].split()[0])
            
            # Comparar con otros cultivos
            mejores = 0
            total = 0
            
            for _, fila in self.datos_manager.df.iterrows():
                try:
                    rend = float(fila['rendimiento_promedio'].split()[0])
                    if rend < rendimiento_actual:
                        mejores += 1
                    total += 1
                except:
                    continue
            
            if total > 0:
                percentil = (mejores / total) * 100
                info_general += f"\n• Este cultivo supera en rendimiento al {percentil:.1f}% de los cultivos disponibles"
                info_general += f"\n• Posición en ranking: {total - mejores} de {total} cultivos"
        
        except:
            pass
        
        # Cultivos similares
        similares = self.datos_manager.buscar_cultivos_similares(cultivo['cultivo'])
        if similares:
            info_general += f"\n\n🔗 CULTIVOS SIMILARES RECOMENDADOS:\n"
            for i, similar in enumerate(similares[:5], 1):
                info_general += f"{i}. {similar}\n"
        
        texto_general.insert(tk.END, info_general)
        
        # Pestaña 2: Comparaciones
        frame_comparaciones = ttk.Frame(notebook)
        notebook.add(frame_comparaciones, text="Comparaciones")
        
        # Lista de cultivos para comparar
        tk.Label(frame_comparaciones, text="Seleccione cultivos para comparar:", 
                font=("Arial", 12, "bold")).pack(pady=5)
        
        frame_seleccion = tk.Frame(frame_comparaciones)
        frame_seleccion.pack(fill=tk.X, padx=10, pady=5)
        
        # Listbox con cultivos
        listbox_cultivos = tk.Listbox(frame_seleccion, selectmode=tk.MULTIPLE, height=8)
        for cultivo_nombre in sorted(self.datos_manager.df['cultivo']):
            listbox_cultivos.insert(tk.END, cultivo_nombre)
        listbox_cultivos.pack(pady=5)
        
        # Área de resultados de comparación
        texto_comparacion = scrolledtext.ScrolledText(frame_comparaciones, height=15)
        texto_comparacion.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def generar_comparacion():
            seleccionados = [listbox_cultivos.get(i) for i in listbox_cultivos.curselection()]
            
            if not seleccionados:
                messagebox.showwarning("Advertencia", "Seleccione al menos un cultivo para comparar")
                return
            
            # Agregar cultivo actual si no está seleccionado
            if self.cultivo_actual['cultivo'] not in seleccionados:
                seleccionados.insert(0, self.cultivo_actual['cultivo'])
            
            texto_comparacion.delete(1.0, tk.END)
            
            comparacion = f"COMPARACIÓN DE CULTIVOS\n{'='*40}\n\n"
            
            for nombre in seleccionados:
                fila = self.datos_manager.df[self.datos_manager.df['cultivo'] == nombre].iloc[0]
                
                marcador = ">>> " if nombre == self.cultivo_actual['cultivo'] else "    "
                
                comparacion += f"{marcador}{nombre}:\n"
                comparacion += f"    • Rendimiento: {fila['rendimiento_promedio']}\n"
                comparacion += f"    • Tiempo: {fila['tiempo_cosecha']}\n"
                comparacion += f"    • Temporada: {fila['temporada_siembra']}\n"
                comparacion += f"    • Lluvia: {fila['lluvia']}\n"
                comparacion += f"    • Temperatura: {fila['temperatura_ideal']}\n\n"
            
            texto_comparacion.insert(tk.END, comparacion)
        
        tk.Button(frame_seleccion, text="Generar Comparación", 
                 command=generar_comparacion,
                 bg="green", fg="white", font=("Arial", 11)).pack(pady=10)
    
    def generar_grafico_cultivo(self):
        """Genera gráfico específico del cultivo actual"""
        if self.cultivo_actual is None:
            messagebox.showwarning("Advertencia", "Seleccione un cultivo primero")
            return
        
        self.graficos_manager.mostrar_grafico_cultivo(self.cultivo_actual, self.root)
    
    def mostrar_grafico_rendimientos(self):
        """Muestra gráfico general de rendimientos mejorado"""
        self.graficos_manager.mostrar_grafico_rendimientos_general(self.root)
    
    def verificar_clima(self):
        """Verifica compatibilidad climática del cultivo actual"""
        if self.cultivo_actual is None:
            messagebox.showwarning("Advertencia", "Seleccione un cultivo primero")
            return
        
        self.clima_manager.verificar_clima_cultivo(self.cultivo_actual, self.root)
    
    def limpiar_resultados(self):
        """Limpia la interfaz y resetea el estado"""
        # Limpiar entrada
        self.entrada_cultivo.delete(0, tk.END)
        
        # Limpiar área de resultados
        self.texto_resultados.delete('1.0', tk.END)
        
        # Mensaje inicial
        mensaje_inicial = """Asistente Agrícola - Panamá

INSTRUCCIONES:
1. Seleccione un cultivo
2. Obtenga información detallada  
3. Use botones de análisis

Cultivos: Arroz, Maíz, Frijol, Plátano, Yuca,
Ñame, Café, Cacao, Naranja, Mango, etc.
        """
        self.texto_resultados.insert(tk.END, mensaje_inicial)
        
        # Deshabilitar botones
        self.boton_analisis.config(state=tk.DISABLED)
        self.boton_clima.config(state=tk.DISABLED)
        self.boton_grafico_cultivo.config(state=tk.DISABLED)
        
        # Resetear estado
        self.cultivo_actual = None
        
        # Actualizar barra de estado
        self.barra_estado.config(text="Sistema listo - Seleccione un cultivo para comenzar")
    

    def cerrar_aplicacion(self):
        """Cierra la aplicación con confirmación"""
        from tkinter import messagebox
        respuesta = messagebox.askyesno("Cerrar Aplicación", 
                                       "¿Está seguro que desea cerrar la aplicación?")
        if respuesta:
            self.root.quit()
            self.root.destroy()