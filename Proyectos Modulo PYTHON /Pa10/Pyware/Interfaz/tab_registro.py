
import tkinter as tk
from tkinter import ttk, messagebox
import datetime, os, csv
from .state import ruta_csv_actual

def obtener_fecha_actual_espanol():
    ahora = datetime.datetime.now()
    dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    return f"{dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}, {ahora.year}"

def generar_mensaje_retroalimentacion(datos):
    mensajes = ["¡Tu registro ha sido guardado con éxito!"]

    try:
        dolor = int(datos.get('dolor', 0))
        fatiga = int(datos.get('fatiga', 0))
    except ValueError:
        dolor, fatiga = 0, 0

    clima = datos.get('clima', '')
    dieta = datos.get('dieta', '')
    sueno = datos.get('sueno', '')
    actividad = datos.get('actividad', '')

    # Síntomas altos
    if dolor >= 4 or fatiga >= 4:
        mensajes.append("Vemos que hoy ha sido un día con síntomas elevados. Recuerda ser amable contigo mismo y descansar.")

    # Clima
    if clima in ["Lluvioso", "Húmedo"]:
        mensajes.append("Los días húmedos pueden intensificar la rigidez. Mantente abrigado y realiza estiramientos suaves.")

    # Dieta
    if dieta == "Inflamatoria":
        mensajes.append("Notamos una dieta pro-inflamatoria. Incluir más vegetales, granos integrales o pescado azul puede ayudar.")
    elif dieta == "Antiinflamatoria":
        mensajes.append("¡Excelente elección con una dieta antiinflamatoria! Es un gran apoyo para tu cuerpo.")

    # Sueño
    if sueno in ["Malo", "Horrible"]:
        mensajes.append(f"Un sueño '{sueno.lower()}' eleva la fatiga y el dolor. Prioriza higiene del sueño esta noche.")
    elif sueno in ["Excelente", "Bueno"]:
        mensajes.append("¡Qué bien esa buena noche de sueño! Mantener esa rutina te ayudará a estabilizar síntomas.")

    # Actividad
    if actividad == "Sí":
        mensajes.append("¡Felicidades por mantenerte activo! Cada movimiento cuenta.")
    else:
        if dolor < 3 and fatiga < 3:
            mensajes.append("En días suaves, una caminata corta puede ayudar a la movilidad.")
        else:
            mensajes.append("Hoy prioriza el descanso. Movilidad suave y pausas frecuentes.")

    return "\n\n- ".join(mensajes)

def mostrar_registro_diario(panel_contenedor: tk.Frame):
    for w in panel_contenedor.winfo_children():
        w.destroy()

    fecha_hoy = obtener_fecha_actual_espanol()

    canvas = tk.Canvas(panel_contenedor, bg="white")
    scrollbar = ttk.Scrollbar(panel_contenedor, orient="vertical", command=canvas.yview)
    marco_scroll = tk.Frame(canvas, bg="white")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=marco_scroll, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    marco_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    tk.Label(marco_scroll, text=f"Registro de Hoy - {fecha_hoy}",
             font=("Arial", 16, "bold"), fg="#4B0082", bg="white").pack(pady=20, padx=20, anchor="w")

    opciones_0_5 = [str(i) for i in range(6)]
    rigidez_var = tk.StringVar(value="0")
    dolor_var = tk.StringVar(value="0")
    inflamacion_var = tk.StringVar(value="0")
    fatiga_var = tk.StringVar(value="0")
    estado_animo_var = tk.StringVar(value="-- Seleccionar --")
    actividad_fisica_var = tk.StringVar(value="-- Seleccionar --")
    calidad_sueno_var = tk.StringVar(value="-- Seleccionar --")
    tipo_dieta_var = tk.StringVar(value="-- Seleccionar --")
    clima_actual_var = tk.StringVar(value="-- Seleccionar --")
    temperatura_var = tk.StringVar(value="")

    formulario = tk.Frame(marco_scroll, bg="white", padx=20, pady=10)
    formulario.pack(fill="x", padx=20)

    def crear_campo(parent, texto, var, valores, fila, col=0, tipo='combo'):
        tk.Label(parent, text=texto, bg="white").grid(row=fila, column=col, sticky="w", padx=10 if col==0 else 40)
        if tipo == 'combo':
            ttk.Combobox(parent, textvariable=var, values=valores, state="readonly", width=22)\
                .grid(row=fila+1, column=col, sticky="w", padx=10 if col==0 else 40)
        else:
            tk.Entry(parent, textvariable=var, width=18)\
                .grid(row=fila+1, column=col, sticky="w", padx=10 if col==0 else 40)

    tk.Label(formulario, text="Clima y Entorno", font=("Arial", 12, "bold"),
             bg="white", fg="#4B0082").grid(row=0, column=0, columnspan=3, sticky="w", pady=(20, 5))
    crear_campo(formulario, "Tipo de Clima", clima_actual_var,
                ["Soleado","Seco","Ventoso","Nublado","Lluvioso","Húmedo"], 1, 0)
    crear_campo(formulario, "Temperatura (°C)", temperatura_var, [], 1, 1, tipo='entry')

    tk.Label(formulario, text=" Síntomas", font=("Arial", 12, "bold"),
             bg="white", fg="#1976D2").grid(row=3, column=0, columnspan=3, sticky="w", pady=(20, 5))
    crear_campo(formulario, "Rigidez (0-5)", rigidez_var, opciones_0_5, 4, 0)
    crear_campo(formulario, "Dolor (0-5)", dolor_var, opciones_0_5, 4, 1)
    crear_campo(formulario, "Inflamación (0-5)", inflamacion_var, opciones_0_5, 4, 2)
    crear_campo(formulario, "Fatiga (0-5)", fatiga_var, opciones_0_5, 6, 0)

    tk.Label(formulario, text="Estado Emocional y Otros", font=("Arial", 12, "bold"),
             bg="white", fg="#1976D2").grid(row=8, column=0, columnspan=3, sticky="w", pady=(20, 5))
    crear_campo(formulario, "Estado de Ánimo", estado_animo_var,
                ["Feliz","Tranquilo","Optimista","Neutral","Estresado","Ansioso","Irritable","Frustrado","Triste"], 9, 0)
    crear_campo(formulario, "¿Actividad Física?", actividad_fisica_var, ["Sí","No"], 9, 1)
    crear_campo(formulario, "Calidad del Sueño", calidad_sueno_var,
                ["Excelente","Bueno","Ok","Malo","Horrible"], 11, 0)
    crear_campo(formulario, "Tipo de Dieta", tipo_dieta_var,
                ["Antiinflamatoria","Balanceada","Inflamatoria"], 11, 1)

    def validar_y_guardar():
        obligatorios = [rigidez_var, dolor_var, inflamacion_var, fatiga_var,
                        estado_animo_var, actividad_fisica_var, calidad_sueno_var,
                        tipo_dieta_var, clima_actual_var]
        if "-- Seleccionar --" in [v.get() for v in obligatorios] or not temperatura_var.get():
            messagebox.showerror("Error", "Por favor, complete todos los campos.", parent=panel_contenedor)
            return
        try:
            float(temperatura_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "La temperatura debe ser un número válido.", parent=panel_contenedor)
            return

        nueva_fila = [
            datetime.datetime.now().strftime("%Y-%m-%d"),
            clima_actual_var.get(),
            float(temperatura_var.get().replace(",", ".")),
            1 if actividad_fisica_var.get() == "Sí" else 0,
            calidad_sueno_var.get(),
            tipo_dieta_var.get(),
            rigidez_var.get(),
            dolor_var.get(),
            inflamacion_var.get(),
            fatiga_var.get(),
            estado_animo_var.get()
        ]
        nombre_archivo = ruta_csv_actual()
        try:
            existe = os.path.exists(nombre_archivo)
            with open(nombre_archivo, 'a', newline='', encoding='utf-8') as f:
                escritor = csv.writer(f)
                if not existe:
                    escritor.writerow([
                        'fecha','clima','temperatura_C','actividad_fisica','sueño','dieta_tipo',
                        'rigidez_score','dolor_score','inflamacion_score','fatiga_score','estado_animo'
                    ])
                escritor.writerow(nueva_fila)

            # Datos de feedback
            datos_fb = {
                "dolor": dolor_var.get(),
                "fatiga": fatiga_var.get(),
                "clima": clima_actual_var.get(),
                "dieta": tipo_dieta_var.get(),
                "sueno": calidad_sueno_var.get(),
                "actividad": actividad_fisica_var.get()
            }
            mensaje = generar_mensaje_retroalimentacion(datos_fb)
            messagebox.showinfo("Análisis Diario", mensaje, parent=panel_contenedor)
        except Exception as e:
            messagebox.showerror("Error de Guardado", f"Ocurrió un error al guardar: {e}", parent=panel_contenedor)

    tk.Button(marco_scroll, text="Guardar y Analizar Registro",
              bg="#4B0082", fg="white", font=("Arial", 12, "bold"), width=30,
              command=validar_y_guardar).pack(pady=40)
