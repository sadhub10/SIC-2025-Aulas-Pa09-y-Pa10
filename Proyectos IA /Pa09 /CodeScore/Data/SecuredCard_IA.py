#CodeScore
import flet as ft
import backend_fraude as bf
from datetime import datetime


def main(page: ft.Page):

    #---------------------CONFIGURACIÓN GENERAL DE LA PÁGINA---------------------

    page.title = "Sistema Inteligente de Detección de Fraude"
    page.bgcolor = "white"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = "start"
    page.scroll = ft.ScrollMode.AUTO

    AZUL = "#1565C0"

    # Inicializar backend (modelos + "BD" CSV)
    bf.inicializar_backend()

    # Estado simple
    state = {
        "is_admin": False,
    }

    # Mensaje de estado
    status_text = ft.Text("", size=11, color="green")

    def set_status(msg: str, error: bool = False):
        status_text.value = msg
        status_text.color = "red" if error else "green"
        page.update()


    #---------------------UTILIDADES GENERALES---------------------


    def cargar_usuarios_dropdown_options():
        df = bf.obtener_usuarios()
        opts = []
        for _, row in df.iterrows():
            etiqueta = f"{row['nombre']} - {row['cedula']}"
            opts.append(ft.dropdown.Option(row["cedula"], text=etiqueta))
        return opts

    #---------------------HEADER (LOGO + TÍTULO + MODO)---------------------

    def manejar_cambio_modo(e):
        if modo_dropdown.value == "usuario":
            state["is_admin"] = False
            admin_login_row.visible = False
            actualizar_tabs_visibles()
            set_status("Modo Usuario activado.")
        else:
            admin_login_row.visible = True
            set_status(
                "Ingrese la contraseña de administrador para desbloquear las pestañas.",
                error=False,
            )
        page.update()

    modo_dropdown = ft.Dropdown(
        width=200,
        options=[
            ft.dropdown.Option("usuario", text="Modo Usuario"),
            ft.dropdown.Option("admin", text="Modo Administrador"),
        ],
        value="usuario",
        on_change=manejar_cambio_modo,
    )

    header = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Image(
                            src="Data/logo1.png",  #LOGO
                            width=48,
                            height=48,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "SecureCard IA",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL,
                                ),
                                ft.Text(
                                    "Sistema Inteligente de Detección de Fraude en Transacciones con Tarjeta",
                                    size=12,
                                    color="black",
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(expand=True),
                ft.Row(
                    [
                        ft.Text("Modo:", color="black", size=12),
                        modo_dropdown,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        border=ft.border.only(bottom=ft.BorderSide(1, AZUL)),
    )


    #---------------------LOGIN ADMIN (ACTIVO)---------------------

    admin_password_field = ft.TextField(
        label="Contraseña administrador",
        password=True,
        can_reveal_password=True,
        width=250,
    )

    def validar_admin(e):
        pwd = admin_password_field.value or ""
        if bf.validar_password_admin(pwd):
            state["is_admin"] = True
            admin_login_row.visible = False
            actualizar_tabs_visibles()
            set_status("Modo Administrador activado. Pestañas desbloqueadas.", error=False)
        else:
            state["is_admin"] = False
            modo_dropdown.value = "usuario"
            actualizar_tabs_visibles()
            set_status("Contraseña incorrecta. Se mantiene en Modo Usuario.", error=True)
        page.update()

    admin_login_row = ft.Row(
        [
            ft.Text("Acceso administrador:", size=12),
            admin_password_field,
            ft.ElevatedButton(
                "Validar",
                on_click=validar_admin,
                bgcolor=AZUL,
                color="white",
            ),
        ],
        spacing=10,
        visible=False,
    )

    #---------------------DROPDOWNS DE USUARIOS---------------------

    usuarios_dropdown_1 = ft.Dropdown(
        label="Seleccionar usuario",
        options=cargar_usuarios_dropdown_options(),
        width=350,
    )
    usuarios_dropdown_2 = ft.Dropdown(
        label="Seleccionar usuario",
        options=cargar_usuarios_dropdown_options(),
        width=350,
    )
    usuarios_admin_dropdown = ft.Dropdown(
        label="Seleccionar usuario",
        options=cargar_usuarios_dropdown_options(),
        width=350,
    )

    def recargar_usuarios_en_todos():
        opts = cargar_usuarios_dropdown_options()
        usuarios_dropdown_1.options = opts
        usuarios_dropdown_2.options = opts
        usuarios_admin_dropdown.options = opts
        page.update()


    #---------------------PESTAÑA 1: NUEVA TRANSACCIÓN---------------------

    # ---- formulario para nuevo usuario ----
    cedula_field = ft.TextField(label="Cédula", width=200)
    nombre_field = ft.TextField(label="Nombre completo", width=250)

    def guardar_nuevo_usuario(e):
        cedula = cedula_field.value or ""
        nombre = nombre_field.value or ""
        try:
            creado = bf.crear_usuario(cedula, nombre)
        except ValueError as ve:
            set_status(str(ve), error=True)
            return

        if not creado:
            set_status("Ya existe un usuario con esa cédula.", error=True)
        else:
            set_status("Usuario creado correctamente.", error=False)
            cedula_field.value = ""
            nombre_field.value = ""
            recargar_usuarios_en_todos()
        nuevo_usuario_form.visible = False
        page.update()

    def cancelar_nuevo_usuario(e):
        cedula_field.value = ""
        nombre_field.value = ""
        nuevo_usuario_form.visible = False
        page.update()

    nuevo_usuario_form = ft.Column(
        [
            ft.Text("Nuevo usuario", size=14, weight=ft.FontWeight.BOLD, color=AZUL),
            ft.Row([cedula_field, nombre_field], spacing=10),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Guardar",
                        on_click=guardar_nuevo_usuario,
                        bgcolor=AZUL,
                        color="white",
                    ),
                    ft.TextButton("Cancelar", on_click=cancelar_nuevo_usuario),
                ],
                spacing=10,
            ),
        ],
        spacing=5,
        visible=False,
    )

    def mostrar_form_nuevo_usuario(e):
        nuevo_usuario_form.visible = not nuevo_usuario_form.visible
        page.update()

    btn_nuevo_usuario_1 = ft.OutlinedButton(
        "Registrar nuevo usuario",
        icon="person_add",
        on_click=mostrar_form_nuevo_usuario,
    )

    # ---- campos de la transacción ----
    type_dropdown = ft.Dropdown(
        label="Tipo de transacción",
        width=220,
        options=[
            ft.dropdown.Option("CASH_IN"),
            ft.dropdown.Option("CASH_OUT"),
            ft.dropdown.Option("TRANSFER"),
            ft.dropdown.Option("DEBIT"),
            ft.dropdown.Option("PAYMENT"),
        ],
        value="CASH_OUT",
    )

    amount_field = ft.TextField(
        label="Monto de la transacción (amount)",
        width=200,
        helper_text="Obligatorio. Ej: 1500.50",
    )

    date_field = ft.TextField(
        label="Fecha (YYYY-MM-DD)",
        width=200,
        helper_text="Opcional. Ej: 2025-11-10",
    )

    time_field = ft.TextField(
        label="Hora (HH:MM, 24h)",
        width=200,
        helper_text="Opcional. Ej: 13:05",
    )

    # ---- panel de resumen del usuario (derecha) ----
    saldo_text = ft.Text("Saldo actual: $0.00", size=16, weight=ft.FontWeight.BOLD)
    total_tx_text = ft.Text("Total de transacciones: 0", size=12)
    ultimas_list = ft.Column(spacing=4)

    def actualizar_resumen_usuario():
        cedula = usuarios_dropdown_1.value
        if not cedula:
            saldo_text.value = "Saldo actual: $0.00"
            total_tx_text.value = "Total de transacciones: 0"
            ultimas_list.controls = []
            page.update()
            return

        resumen = bf.obtener_resumen_usuario(cedula)
        saldo = resumen["saldo_actual"]
        total_tx = resumen["total_transacciones"]
        ultimas = resumen["ultimas"]

        saldo_text.value = f"Saldo actual: ${saldo:,.2f}"
        total_tx_text.value = f"Total de transacciones: {total_tx}"

        ultimas_list.controls = []
        if not ultimas:
            ultimas_list.controls.append(
                ft.Text("Sin transacciones registradas.", size=11)
            )
        else:
            for tx in ultimas:
                linea = ft.Text(
                    f"TX #{tx['tx_id']} | {tx['timestamp']} | "
                    f"{tx['tipo']} | ${tx['monto']:.2f} | Riesgo: {tx['riesgo']}",
                    size=11,
                )
                ultimas_list.controls.append(linea)

        page.update()

    def on_cambio_usuario_1(e):
        actualizar_resumen_usuario()

    usuarios_dropdown_1.on_change = on_cambio_usuario_1

    # ---- botón evaluar/guardar ----
    def on_evaluar_y_guardar(e):
        cedula = usuarios_dropdown_1.value
        if not cedula:
            set_status("Debes seleccionar un usuario.", error=True)
            return

        tipo = type_dropdown.value or "CASH_OUT"

        if not amount_field.value:
            set_status("Debes ingresar un monto para la transacción.", error=True)
            return
        try:
            amount = float(amount_field.value)
        except ValueError:
            set_status("El monto debe ser numérico.", error=True)
            return

        timestamp_manual = None
        if date_field.value and time_field.value:
            try:
                dt = datetime.strptime(
                    f"{date_field.value} {time_field.value}", "%Y-%m-%d %H:%M"
                )
                timestamp_manual = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                set_status(
                    "Fecha u hora inválida. Usa formato YYYY-MM-DD y HH:MM.",
                    error=True,
                )
                return

        entrada = {
            "step": 0,
            "type": tipo,
            "amount": amount,
            "timestamp_manual": timestamp_manual,
        }

        try:
            resultado = bf.crear_transaccion_para_usuario(cedula, entrada)
        except Exception as ex:
            set_status(f"Error al crear/evaluar transacción: {ex}", error=True)
            return

        tx_id = resultado["tx_id"]
        prob = resultado["prediccion"]["prob_fraude"]
        riesgo = resultado["prediccion"]["riesgo_final"]

        set_status(
            f"Transacción #{tx_id} evaluada y guardada correctamente. "
            f"Prob. fraude={prob:.3f}, nivel de riesgo={riesgo}.",
            error=False,
        )

        # actualizar panel de resumen (saldo y lista de movimientos)
        actualizar_resumen_usuario()
        page.update()

    btn_evaluar_guardar = ft.ElevatedButton(
        "Evaluar y guardar transacción",
        icon="save",
        bgcolor=AZUL,
        color="white",
        on_click=on_evaluar_y_guardar,
    )

    pestaña1_contenido = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Text(
                    "Nueva transacción",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL,
                ),
                ft.Text(
                    "Seleccione un usuario, defina los parámetros de la transacción "
                    "y el sistema evaluará el riesgo de fraude usando modelos "
                    "no supervisados y supervisados.",
                    size=12,
                    color="black",
                ),
                ft.Divider(),
                ft.Row(
                    [usuarios_dropdown_1, btn_nuevo_usuario_1],
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
                nuevo_usuario_form,
                ft.Divider(),
                ft.Row(
                    [
                        # Columna izquierda: formulario
                        ft.Column(
                            [
                                ft.Text("Parámetros de la transacción:", size=14),
                                ft.Row([type_dropdown, amount_field], spacing=10),
                                ft.Row([date_field, time_field], spacing=10),
                                ft.Text(
                                    "La fecha y hora son opcionales. Si se omiten, se usa la fecha/hora actual.",
                                    size=11,
                                    color="grey",
                                ),
                                ft.Divider(),
                                btn_evaluar_guardar,
                            ],
                            spacing=15,
                            expand=True,
                        ),
                        # Columna derecha: resumen de cuenta
                        ft.Container(
                            width=400,
                            content=ft.Card(
                                content=ft.Container(
                                    padding=15,
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Resumen de la cuenta del usuario",
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=AZUL,
                                            ),
                                            saldo_text,
                                            total_tx_text,
                                            ft.Text(
                                                "Últimas transacciones:",
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ultimas_list,
                                        ],
                                        spacing=8,
                                    ),
                                )
                            ),
                        ),
                    ],
                    spacing=30,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=15,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
    )


    #---------------------PESTAÑA 2: EVALUACIÓN DE TRANSACCIONES---------------------

    tx_dropdown = ft.Dropdown(
        label="Seleccionar transacción",
        options=[],
        width=300,
    )

    detalle_transaccion_column = ft.Column([], spacing=5)

    def cargar_transacciones_usuario_eval(e=None):
        cedula = usuarios_dropdown_2.value
        tx_dropdown.options = []
        detalle_transaccion_column.controls.clear()
        if not cedula:
            page.update()
            return

        df_tx = bf.obtener_transacciones_por_usuario(cedula)
        opts = []
        for _, row in df_tx.iterrows():
            label = (
                f"TX #{int(row['tx_id'])} - {row['timestamp_eval']} "
                f"- Riesgo {row['riesgo']}"
            )
            opts.append(ft.dropdown.Option(str(int(row["tx_id"])), text=label))
        tx_dropdown.options = opts
        page.update()

    usuarios_dropdown_2.on_change = cargar_transacciones_usuario_eval

    def mostrar_detalle_transaccion(e=None):
        detalle_transaccion_column.controls.clear()
        if not tx_dropdown.value:
            page.update()
            return

        try:
            tx_id = int(tx_dropdown.value)
        except Exception:
            set_status("ID de transacción inválido.", error=True)
            return

        fila = bf.obtener_transaccion_por_id(tx_id)
        if fila is None:
            set_status("No se encontró la transacción seleccionada.", error=True)
            return

        prob = float(fila["prob_fraude"])
        riesgo = fila["riesgo"]
        recomendacion = fila["recomendacion"]
        timestamp = fila["timestamp_eval"]
        resumen_just = fila.get("justificacion_resumen", "")
        monto = float(fila.get("Amount", 0.0))

        caracteristicas = []
        if riesgo == "BAJO":
            caracteristicas.append(
                "Transacción estándar dentro del rango habitual de montos del usuario."
            )
            caracteristicas.append(
                "Frecuencia de transacciones normal, sin picos ni repeticiones inusuales."
            )
        elif riesgo == "MEDIO":
            caracteristicas.append(
                "Monto algo elevado en comparación con el historial típico del usuario."
            )
            caracteristicas.append(
                "Actividad reciente ligeramente superior a lo habitual o con cierta variación en los montos."
            )
        else:  # ALTO
            caracteristicas.append(
                "Monto muy alto en comparación con el rango normal de gasto del usuario."
            )
            caracteristicas.append(
                "Varias transacciones recientes en un intervalo corto o con montos muy similares."
            )
            caracteristicas.append(
                "Patrón general de la operación claramente atípico respecto al historial del usuario."
            )

        # --- controles de retroalimentación del usuario ---
        feedback_group = ft.RadioGroup(
            value=None,  # sin selección inicial
            content=ft.Row(
                [
                    ft.Radio(value="fraude", label="Sí, fue fraude"),
                    ft.Radio(
                        value="no_fraude",
                        label="No, fue una transacción legítima",
                    ),
                    ft.Radio(value="no_seguro", label="No estoy seguro"),
                ],
                spacing=15,
            ),
        )

        def on_enviar_feedback(ev):
            val = feedback_group.value
            if val is None:
                set_status(
                    "Selecciona una opción de retroalimentación antes de enviar.",
                    error=True,
                )
                return

            if val == "fraude":
                msg = (
                    f"Retroalimentación enviada: marcaste la transacción "
                    f"#{tx_id} como FRAUDE REAL."
                )
            elif val == "no_fraude":
                msg = (
                    f"Retroalimentación enviada: marcaste la transacción "
                    f"#{tx_id} como transacción LEGÍTIMA."
                )
            else:  # no_seguro
                msg = (
                    f"Retroalimentación enviada: marcaste la transacción "
                    f"#{tx_id} como 'No estoy seguro'."
                )

            # Mostrar mensaje en la barra de estado
            set_status(msg, error=False)

            # Limpiar selección para simular que ya se envió
            feedback_group.value = None
            page.update()

        btn_enviar_feedback = ft.ElevatedButton(
            "Enviar retroalimentación",
            icon="send",
            bgcolor=AZUL,
            color="white",
            on_click=on_enviar_feedback,
        )

        detalle_transaccion_column.controls.append(
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column(
                        [
                            ft.Text(
                                f"Detalle de la transacción #{tx_id}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=AZUL,
                            ),
                            ft.Text(
                                f"Fecha/Hora de evaluación: {timestamp}",
                                size=12,
                            ),
                            ft.Text(
                                f"Monto de la transacción: ${monto:.2f}",
                                size=13,
                            ),
                            ft.Text(
                                f"Probabilidad de fraude: {prob:.3f}",
                                size=14,
                            ),
                            ft.Text(f"Nivel de riesgo: {riesgo}", size=14),
                            ft.Text(
                                f"Recomendación del sistema: {recomendacion}",
                                size=13,
                            ),
                            ft.Text(
                                "Justificación (resumen):",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(resumen_just, size=12),
                            ft.Text(
                                "Principales características que influyeron en la decisión:",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=AZUL,
                            ),
                            ft.Column(
                                [ft.Text(f"- {c}", size=12) for c in caracteristicas],
                                spacing=2,
                            ),
                            ft.Divider(),
                            ft.Text(
                                "Retroalimentación del usuario:",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=AZUL,
                            ),
                            ft.Text(
                                "¿Consideras que esta transacción fue realmente un fraude?",
                                size=12,
                            ),
                            feedback_group,
                            ft.Row(
                                [btn_enviar_feedback],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        spacing=8,
                    ),
                )
            )
        )

        set_status(f"Detalle de la transacción #{tx_id} mostrado.", error=False)
        page.update()

    tx_dropdown.on_change = mostrar_detalle_transaccion

    pestaña2_contenido = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Text(
                    "Evaluación de transacciones",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL,
                ),
                ft.Text(
                    "Seleccione un usuario y luego una transacción para ver el análisis completo y la justificación.",
                    size=12,
                    color="black",
                ),
                ft.Divider(),
                ft.Row([usuarios_dropdown_2, tx_dropdown], spacing=20),
                ft.Divider(),
                detalle_transaccion_column,
            ],
            spacing=10,
            expand=True,
        ),
    )


    #---------------------PESTAÑA 3: ADMINISTRACIÓN---------------------

    usuarios_admin_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)
    transacciones_admin_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)

    def recargar_lista_usuarios_admin():
        usuarios_admin_list.controls.clear()
        df = bf.obtener_usuarios()
        if df.empty:
            usuarios_admin_list.controls.append(
                ft.Text("No hay usuarios registrados.")
            )
        else:
            for _, row in df.iterrows():
                ced = row["cedula"]
                nom = row["nombre"]
                saldo = float(row.get("saldo", 0.0))

                def make_on_delete(cedula_actual):
                    def on_delete(ev):
                        ok = bf.eliminar_usuario(cedula_actual)
                        if ok:
                            set_status(
                                "Usuario y sus transacciones eliminados.", error=False
                            )
                            recargar_lista_usuarios_admin()
                            recargar_usuarios_en_todos()
                            transacciones_admin_list.controls.clear()
                        else:
                            set_status(
                                "No se pudo eliminar el usuario.", error=True
                            )
                        page.update()

                    return on_delete

                usuarios_admin_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(
                                                f"{nom}",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Text(f"Cédula: {ced}", size=12),
                                            ft.Text(
                                                f"Saldo actual: ${saldo:,.2f}",
                                                size=11,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Container(expand=True),
                                    ft.IconButton(
                                        icon="delete",
                                        tooltip="Eliminar usuario",
                                        icon_color="red",
                                        on_click=make_on_delete(ced),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        )
                    )
                )
        page.update()

    def cargar_transacciones_admin(e=None):
        transacciones_admin_list.controls.clear()
        cedula = usuarios_admin_dropdown.value
        if not cedula:
            page.update()
            return

        df_tx = bf.obtener_transacciones_por_usuario(cedula)
        if df_tx.empty:
            transacciones_admin_list.controls.append(
                ft.Text("Este usuario no tiene transacciones registradas.")
            )
        else:
            for _, row in df_tx.iterrows():
                tx_id = int(row["tx_id"])
                timestamp = row["timestamp_eval"]
                prob = float(row["prob_fraude"])
                riesgo = row["riesgo"]
                monto = float(row["Amount"])

                def make_on_delete_tx(tx_id_local):
                    def on_delete_tx(ev):
                        ok = bf.eliminar_transaccion(tx_id_local)
                        if ok:
                            set_status("Transacción eliminada.", error=False)
                            cargar_transacciones_admin()
                        else:
                            set_status(
                                "No se pudo eliminar la transacción.", error=True
                            )
                        page.update()

                    return on_delete_tx

                transacciones_admin_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(
                                                f"Transacción #{tx_id}",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Text(f"Fecha: {timestamp}", size=11),
                                            ft.Text(
                                                f"Monto: ${monto:.2f} | Prob. fraude: {prob:.3f} | Riesgo: {riesgo}",
                                                size=11,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Container(expand=True),
                                    ft.IconButton(
                                        icon="delete",
                                        tooltip="Eliminar transacción",
                                        icon_color="red",
                                        on_click=make_on_delete_tx(tx_id),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        )
                    )
                )

        page.update()

    usuarios_admin_dropdown.on_change = cargar_transacciones_admin

    pestaña3_contenido = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Text(
                    "Administración",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL,
                ),
                ft.Text(
                    "Gestione usuarios y transacciones del sistema.",
                    size=12,
                    color="black",
                ),
                ft.Divider(),
                ft.Text(
                    "Usuarios registrados",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL,
                ),
                usuarios_admin_list,
                ft.Divider(),
                ft.Text(
                    "Transacciones por usuario",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL,
                ),
                usuarios_admin_dropdown,
                transacciones_admin_list,
            ],
            spacing=10,
            expand=True,
        ),
    )

    #---------------------TABS---------------------

    tab_nueva = ft.Tab(text="Nueva transacción", content=pestaña1_contenido)
    tab_eval = ft.Tab(text="Evaluación", content=pestaña2_contenido)
    tab_admin = ft.Tab(text="Administración", content=pestaña3_contenido)

    tabs = ft.Tabs(
        tabs=[tab_nueva],
        selected_index=0,
        expand=True,
    )

    def actualizar_tabs_visibles():
        if state["is_admin"]:
            tabs.tabs = [tab_nueva, tab_eval, tab_admin]
        else:
            tabs.tabs = [tab_nueva]
            tabs.selected_index = 0
        page.update()


    #---------------------CONEXION DE PÁGINA--------------------

    page.add(
        header,
        admin_login_row,
        tabs,
        ft.Divider(),
        status_text,
    )

    recargar_lista_usuarios_admin()
    actualizar_tabs_visibles()
    # por si ya hay algún usuario seleccionado al inicio
    actualizar_resumen_usuario()

#---------------------APLICACIÓN---------------------

if __name__ == "__main__":
    ft.app(target=main)