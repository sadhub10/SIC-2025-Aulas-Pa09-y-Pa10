import os
import numpy as np
import pandas as pd
import flet as ft
import shutil
from flet.matplotlib_chart import MatplotlibChart
from matplotlib.figure import Figure
import datetime as dt

CSV_PATH = "finanzas_empresaxyz_expandido.csv"


def _smart_parse_dates(obj):
    """Parsea una serie o un valor escalar intentando dayfirst=True y dayfirst=False.
    Devuelve la versión con más valores no nulos (heurística simple).
    """
    try:
        # Serie
        if isinstance(obj, pd.Series):
            if pd.api.types.is_datetime64_any_dtype(obj):
                return obj
            # intentar dayfirst=True y False
            t1 = pd.to_datetime(obj, errors="coerce", dayfirst=True)
            t2 = pd.to_datetime(obj, errors="coerce", dayfirst=False)
            return t1 if t1.notna().sum() >= t2.notna().sum() else t2

        # Escalar
        for dayfirst in (True, False):
            try:
                val = pd.to_datetime(obj, errors="coerce", dayfirst=dayfirst)
                if not pd.isna(val):
                    return val
            except Exception:
                continue
        return pd.NaT
    except Exception:
        return pd.NaT


# ===================== UTILIDADES DE DATOS =====================
def ensure_dataframe(path=CSV_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        cols = [
            "id", "fecha", "mes", "ingresos", "gastos_fijos", "gastos_variables",
            "ventas", "activos_corrientes", "pasivos_corrientes"
        ]
        pd.DataFrame(columns=cols).to_csv(path, index=False)

    df = pd.read_csv(path)

    # Asegurar columna id
    if "id" not in df.columns:
        # generamos ids secuenciales si no existe
        df.insert(0, "id", range(1, len(df) + 1))

    # Compatibilidad con tu CSV mensual original
    if "ingresos_mensuales" in df.columns:
        df["mes"] = _smart_parse_dates(df["mes"]) if "mes" in df.columns else pd.NaT
        df["fecha"] = df["mes"]
        df.rename(
            columns={"ingresos_mensuales": "ingresos", "ventas_mensuales": "ventas"},
            inplace=True,
        )
    else:
        if "fecha" in df.columns:
            df["fecha"] = _smart_parse_dates(df["fecha"]) if "fecha" in df.columns else pd.NaT
        if "mes" in df.columns:
            df["mes"] = _smart_parse_dates(df["mes"]) if "mes" in df.columns else pd.NaT

    # Derivar siempre 'mes' a partir de 'fecha' cuando esté disponible.
    # Esto evita inconsistencias si el CSV importado trae una columna 'mes' en un formato equivocado.
    if "fecha" in df.columns:
        try:
            df["mes"] = df["fecha"].dt.to_period("M").dt.to_timestamp()
        except Exception:
            # si falla la conversión (fechas no parseadas), mantener lo que haya o NaT
            if "mes" not in df.columns:
                df["mes"] = pd.NaT

    for c in [
        "ingresos",
        "gastos_fijos",
        "gastos_variables",
        "ventas",
        "activos_corrientes",
        "pasivos_corrientes",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Derivadas
    if "gastos_fijos" in df.columns and "gastos_variables" in df.columns:
        df["gastos_totales"] = df["gastos_fijos"].fillna(0) + df["gastos_variables"].fillna(0)
    else:
        df["gastos_totales"] = np.nan

    if "ingresos" in df.columns:
        ingresos_safe = df["ingresos"].fillna(0).replace(0, 1e-9)
        df["margen_ganancia"] = (df["ingresos"].fillna(0) - df["gastos_totales"].fillna(0)) / ingresos_safe
    else:
        df["margen_ganancia"] = np.nan

    if "activos_corrientes" in df.columns and "pasivos_corrientes" in df.columns:
        pasivos_safe = df["pasivos_corrientes"].fillna(0).replace(0, 1e-9)
        df["liquidez_corriente"] = df["activos_corrientes"].fillna(0) / pasivos_safe
    else:
        df["liquidez_corriente"] = np.nan

    def classify_by_profit(row):
        """Clasifica el riesgo según la ganancia absoluta: ingresos - gastos_totales.
        rentabilidad > 0 => BAJO, < 0 => ALTO, == 0 o datos faltantes => MEDIO
        """
        try:
            ingresos = row.get("ingresos", np.nan)
            gastos_tot = row.get("gastos_totales", np.nan)
            if pd.isna(ingresos) or pd.isna(gastos_tot):
                return "MEDIO"
            profit = ingresos - gastos_tot
            if profit > 0:
                return "BAJO"
            if profit < 0:
                return "ALTO"
            return "MEDIO"
        except Exception:
            return "MEDIO"

    df["riesgo"] = df.apply(classify_by_profit, axis=1)

    if "fecha" in df.columns:
        df.sort_values("fecha", inplace=True)

    return df


def append_row(row: dict, path=CSV_PATH):
    df = ensure_dataframe(path)

    fecha = _smart_parse_dates(row.get("fecha"))
    if pd.isna(fecha):
        raise ValueError("Fecha inválida.")

    row["fecha"] = fecha
    row["mes"] = fecha.to_period("M").to_timestamp()

    for c in [
        "ingresos",
        "gastos_fijos",
        "gastos_variables",
        "ventas",
        "activos_corrientes",
        "pasivos_corrientes",
    ]:
        row[c] = pd.to_numeric(row.get(c, np.nan), errors="coerce")

    row["gastos_totales"] = (row["gastos_fijos"] or 0) + (row["gastos_variables"] or 0)
    ingresos_safe = row["ingresos"] if row["ingresos"] not in [None, 0, np.nan] else 1e-9
    row["margen_ganancia"] = ((row["ingresos"] or 0) - row["gastos_totales"]) / ingresos_safe
    pasivos_safe = row["pasivos_corrientes"] if row["pasivos_corrientes"] not in [None, 0, np.nan] else 1e-9
    row["liquidez_corriente"] = (row["activos_corrientes"] or 0) / pasivos_safe

    liq = row["liquidez_corriente"]
    marg = row["margen_ganancia"]
    # Clasificación por ganancia absoluta: ingresos - gastos_totales
    try:
        ingresos_val = row.get("ingresos", np.nan)
        gastos_val = row.get("gastos_totales", np.nan)
        if pd.isna(ingresos_val) or pd.isna(gastos_val):
            row["riesgo"] = "MEDIO"
        else:
            profit = ingresos_val - gastos_val
            if profit > 0:
                row["riesgo"] = "BAJO"
            elif profit < 0:
                row["riesgo"] = "ALTO"
            else:
                row["riesgo"] = "MEDIO"
    except Exception:
        row["riesgo"] = "MEDIO"

    expected_cols = [
        "id",
        "fecha",
        "mes",
        "ingresos",
        "gastos_fijos",
        "gastos_variables",
        "ventas",
        "activos_corrientes",
        "pasivos_corrientes",
        "gastos_totales",
        "margen_ganancia",
        "liquidez_corriente",
        "riesgo",
    ]
    row_df = pd.DataFrame([{c: row.get(c, np.nan) for c in expected_cols}])

    # asignar id nuevo
    max_id = int(df["id"].max()) if "id" in df.columns and not df.empty else 0
    row_df["id"] = max_id + 1

    full = pd.concat([df.reindex(columns=expected_cols, fill_value=np.nan), row_df], ignore_index=True)
    # reordenar columnas colocando id primero si está presente en df original
    if "id" in full.columns:
        cols_order = [c for c in full.columns if c != "id"]
        cols_order = ["id"] + cols_order
        full = full.reindex(columns=cols_order)

    full.to_csv(path, index=False)


def normalize_csv(path=CSV_PATH):
    """Carga el CSV, normaliza fecha/mes/numéricos y sobrescribe el archivo.
    Esto corrige CSVs que contengan una columna 'mes' en un formato incorrecto.
    """
    df = ensure_dataframe(path)
    # asegurar tipos
    if "fecha" in df.columns:
        df["fecha"] = _smart_parse_dates(df["fecha"]) if "fecha" in df.columns else pd.NaT
        try:
            df["mes"] = df["fecha"].dt.to_period("M").dt.to_timestamp()
        except Exception:
            df["mes"] = _smart_parse_dates(df["mes"]) if "mes" in df.columns else pd.NaT

    for col in [
        "ingresos",
        "gastos_fijos",
        "gastos_variables",
        "ventas",
        "activos_corrientes",
        "pasivos_corrientes",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # recalcular derivadas
    if "gastos_fijos" in df.columns and "gastos_variables" in df.columns:
        df["gastos_totales"] = df["gastos_fijos"].fillna(0) + df["gastos_variables"].fillna(0)
    if "ingresos" in df.columns:
        ingresos_safe = df["ingresos"].fillna(0).replace(0, 1e-9)
        df["margen_ganancia"] = (df["ingresos"].fillna(0) - df["gastos_totales"].fillna(0)) / ingresos_safe
    if "activos_corrientes" in df.columns and "pasivos_corrientes" in df.columns:
        pasivos_safe = df["pasivos_corrientes"].fillna(0).replace(0, 1e-9)
        df["liquidez_corriente"] = df["activos_corrientes"].fillna(0) / pasivos_safe

    # recalcular riesgo
    def _clas(r):
        try:
            ing = r.get("ingresos", pd.NA)
            g = r.get("gastos_totales", pd.NA)
            if pd.isna(ing) or pd.isna(g):
                return "MEDIO"
            p = ing - g
            return "BAJO" if p > 0 else ("ALTO" if p < 0 else "MEDIO")
        except Exception:
            return "MEDIO"

    df["riesgo"] = df.apply(_clas, axis=1)
    # guardar en ISO para fecha y mes
    if "fecha" in df.columns:
        try:
            df["fecha"] = df["fecha"].dt.strftime("%Y-%m-%d")
        except Exception:
            pass
    if "mes" in df.columns:
        try:
            df["mes"] = df["mes"].dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    # backup y escritura
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak_normalize")
    df.to_csv(path, index=False)


# ===================== GRÁFICOS =====================
def fig_ingresos_vs_gastos_promedio(df: pd.DataFrame) -> Figure:
    d = df.copy()
    if "mes" in d.columns:
        d["mes"] = _smart_parse_dates(d["mes"])
    grp = d.groupby(d["mes"].dt.month_name(), sort=False)[["ingresos", "gastos_totales"]].mean()
    # figura más grande
    fig = Figure(figsize=(16, 9))
    ax = fig.add_subplot(111)
    grp.plot(kind="bar", ax=ax)
    ax.set_title("Ingresos vs Gastos Promedio por Mes")
    ax.set_ylabel("Monto (USD)")
    ax.set_xlabel("Mes")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def fig_distribucion_riesgo(df: pd.DataFrame) -> Figure:
    # Mostrar sólo ALTO y BAJO (omitimos 'MEDIO' por petición)
    counts = df["riesgo"].value_counts().reindex(["ALTO", "BAJO"]).fillna(0)
    # Si ambos son 0 (ej. df vacío o sin esos niveles), crear una serie mínima para evitar errores
    if counts.sum() == 0:
        counts = pd.Series([0, 0], index=["ALTO", "BAJO"])

    fig = Figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    # usar colores CSS/hex compatibles con Matplotlib (evitar métodos de Flet no expuestos)
    counts.plot(kind="bar", ax=ax, color=["#E53935", "#2E7D32"])  # rojo para ALTO, verde para BAJO
    ax.set_title("Distribución de Riesgo (ALTO vs BAJO)")
    ax.set_ylabel("Cantidad de Registros")
    ax.set_xlabel("Nivel de Riesgo")
    # ajustar límites y ticks de y de forma segura
    ymax = max(int(counts.max()) + 1, 1)
    ax.set_ylim(0, ymax)
    step = 1 if ymax <= 25 else max(1, ymax // 10)
    ax.set_yticks(np.arange(0, ymax + 1, step))
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    return fig


def fig_evolucion_mensual(df: pd.DataFrame) -> Figure:
    d = df.copy()
    if "mes" in d.columns:
        d["mes"] = _smart_parse_dates(d["mes"])
    mensual = d.groupby("mes")[["ingresos", "gastos_totales"]].mean().sort_index()
    fig = Figure(figsize=(16, 9))
    ax = fig.add_subplot(111)
    mensual.plot(marker="o", ax=ax)
    ax.set_title("Evolución Mensual Promedio — Ingresos vs Gastos")
    ax.set_ylabel("Monto (USD)")
    ax.set_xlabel("Mes")
    fig.tight_layout()
    return fig


def fig_margen_linea(df: pd.DataFrame) -> Figure:
    d = df.copy()
    if "mes" in d.columns:
        d["mes"] = _smart_parse_dates(d["mes"])
    prov = (
        d.groupby(d["mes"].dt.to_period("M").dt.to_timestamp())["margen_ganancia"]
        .mean()
        .sort_index()
    )
    fig = Figure(figsize=(16, 9))
    ax = fig.add_subplot(111)
    prov.plot(marker="o", ax=ax)
    ax.set_title("Margen de Ganancia Promedio por Mes")
    ax.set_ylabel("Margen Promedio")
    ax.set_xlabel("Mes")
    fig.tight_layout()
    return fig


# ===================== APP FLET =====================
def main(page: ft.Page):
    page.title = "Análisis de Riesgo Financiero — Microempresas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.scroll = ft.ScrollMode.ADAPTIVE

    df = ensure_dataframe()

    # --- DatePicker ---
    date_picker = ft.DatePicker()
    page.overlay.append(date_picker)

    def on_date_changed(e):
        if date_picker.value:
            fecha_field.value = date_picker.value.strftime("%Y-%m-%d")
            page.update()

    date_picker.on_change = on_date_changed

    # --- Controles de captura ---
    # Campo fecha SIN on_tap. Usamos un ícono para abrir el date picker.
    # TextField no soporta `on_tap`; usar `on_click` o un IconButton como sufijo.
    def _open_date_picker(e=None):
        date_picker.open = True
        page.update()

    fecha_field = ft.TextField(
        label="Fecha",
        read_only=True,
        on_click=_open_date_picker,
        suffix=ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            tooltip="Elegir fecha",
            on_click=_open_date_picker,
        ),
    )

    # Si tu versión de Flet no tiene NumbersOnlyInputFilter, puedes cambiar a keyboard_type=ft.KeyboardType.NUMBER
    def num_field(lbl):
        try:
            return ft.TextField(label=lbl, input_filter=ft.NumbersOnlyInputFilter())
        except Exception:
            return ft.TextField(label=lbl, keyboard_type=ft.KeyboardType.NUMBER)

    ingresos_field = num_field("Ingresos (USD)")
    gf_field = num_field("Gastos fijos (USD)")
    gv_field = num_field("Gastos variables (USD)")
    ventas_field = num_field("Ventas (USD)")
    act_field = num_field("Activos corrientes (USD)")
    pas_field = num_field("Pasivos corrientes (USD)")

    # SnackBar requiere un `content` en esta versión de Flet
    snackbar = ft.SnackBar(content=ft.Text(""), open=False)

    # --- Eliminar registro (definido antes de build_table para poder referenciarlo)
    delete_target_id = {"id": None}
    # id temporal para edición desde los campos de captura
    edit_target_id = {"id": None}

    def delete_by_id(target_id: int):
        try:
            print(f"delete_by_id called for id={target_id}")
            df_current = ensure_dataframe()
            if "id" in df_current.columns and target_id in df_current["id"].values:
                # backup antes de sobrescribir
                bak = CSV_PATH + ".bak"
                shutil.copy2(CSV_PATH, bak)
                df_current = df_current[df_current["id"] != target_id]
                df_current.to_csv(CSV_PATH, index=False)
                snackbar.content = ft.Text(f"Registro eliminado. Backup: {bak}")
                snackbar.open = True
                refresh_all()
                # garantizar actualización de conclusiones y mostrar confirmación
                update_conclusiones(ensure_dataframe())
            else:
                snackbar.content = ft.Text("No se encontró el registro para eliminar.")
                snackbar.open = True
            page.update()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al eliminar: {ex}")
            snackbar.open = True
            page.update()

    # Dialogo de confirmacion
    confirm_delete_dialog = ft.AlertDialog(
        title=ft.Text("Confirmar eliminación"),
        content=ft.Text("¿Desea eliminar este registro?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.dialog.close()),
            ft.ElevatedButton("Eliminar", bgcolor=ft.Colors.RED_400, on_click=lambda e: (page.dialog.close(), delete_by_id(delete_target_id["id"]))),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def delete_row(e: ft.ControlEvent):
        # abrir dialogo y guardar id objetivo
        try:
            target = e.control.data
            print(f"delete_row called for id={target}")
            delete_target_id["id"] = int(target)
            page.dialog = confirm_delete_dialog
            page.dialog.open = True
            page.update()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al preparar eliminación: {ex}")
            snackbar.open = True
            page.update()

    # --- Tabla ---
    # Estado para paginación / búsqueda
    table_page = {"page": 0, "page_size": 10, "query": ""}
    # Estado de selección de filas (ids)
    selected_ids = set()

    def toggle_select(e: ft.ControlEvent):
        try:
            rid = int(e.control.data)
            print(f"toggle_select called for id={rid}, value={e.control.value}")
            if e.control.value:
                selected_ids.add(rid)
            else:
                selected_ids.discard(rid)
        except Exception:
            pass
        # no actualizar toda la página para ser rápido; actualizar tabla si es necesario
        page.update()

    # Actualizar registro por id
    def update_by_id(target_id: int, new_values: dict):
        try:
            print(f"update_by_id called for id={target_id} with values={new_values}")
            df_current = ensure_dataframe()
            mask = df_current["id"] == target_id
            if not mask.any():
                snackbar.content = ft.Text("Registro no encontrado para actualizar.")
                snackbar.open = True
                page.update()
                return
            # actualizar columnas provistas
            # convertir y normalizar antes de asignar para evitar asignaciones de str a columnas numéricas
            nv = new_values.copy()
            # fecha
            if "fecha" in nv and nv["fecha"]:
                try:
                    nv["fecha"] = _smart_parse_dates(nv["fecha"])
                except Exception:
                    nv["fecha"] = pd.NaT
            # numéricos
            for col in ["ingresos", "gastos_fijos", "gastos_variables", "ventas", "activos_corrientes", "pasivos_corrientes"]:
                if col in nv:
                    try:
                        nv[col] = pd.to_numeric(nv[col], errors="coerce")
                    except Exception:
                        nv[col] = np.nan

            for k, v in nv.items():
                if k in df_current.columns:
                    df_current.loc[mask, k] = v

            # Normalizar tipos y recalcular derivadas para las filas afectadas
            # convertir fecha (usar parsing inteligente)
            try:
                df_current.loc[mask, "fecha"] = _smart_parse_dates(df_current.loc[mask, "fecha"]) if "fecha" in df_current.columns else pd.NaT
                df_current.loc[mask, "mes"] = df_current.loc[mask, "fecha"].dt.to_period("M").dt.to_timestamp()
            except Exception:
                pass

            for col in ["ingresos", "gastos_fijos", "gastos_variables", "ventas", "activos_corrientes", "pasivos_corrientes"]:
                if col in df_current.columns:
                    df_current.loc[mask, col] = pd.to_numeric(df_current.loc[mask, col], errors="coerce")

            # recalcular campos derivados
            if "gastos_fijos" in df_current.columns and "gastos_variables" in df_current.columns:
                df_current.loc[mask, "gastos_totales"] = df_current.loc[mask, "gastos_fijos"].fillna(0) + df_current.loc[mask, "gastos_variables"].fillna(0)
            else:
                df_current.loc[mask, "gastos_totales"] = np.nan

            if "ingresos" in df_current.columns:
                ingresos_safe = df_current.loc[mask, "ingresos"].fillna(0).replace(0, 1e-9)
                df_current.loc[mask, "margen_ganancia"] = (df_current.loc[mask, "ingresos"].fillna(0) - df_current.loc[mask, "gastos_totales"].fillna(0)) / ingresos_safe
            else:
                df_current.loc[mask, "margen_ganancia"] = np.nan

            if "activos_corrientes" in df_current.columns and "pasivos_corrientes" in df_current.columns:
                pasivos_safe = df_current.loc[mask, "pasivos_corrientes"].fillna(0).replace(0, 1e-9)
                df_current.loc[mask, "liquidez_corriente"] = df_current.loc[mask, "activos_corrientes"].fillna(0) / pasivos_safe
            else:
                df_current.loc[mask, "liquidez_corriente"] = np.nan

            def clasifica_row_by_profit(r):
                try:
                    ingresos_val = r.get("ingresos", np.nan)
                    gastos_val = r.get("gastos_totales", np.nan)
                    if pd.isna(ingresos_val) or pd.isna(gastos_val):
                        return "MEDIO"
                    profit = ingresos_val - gastos_val
                    if profit > 0:
                        return "BAJO"
                    if profit < 0:
                        return "ALTO"
                    return "MEDIO"
                except Exception:
                    return "MEDIO"

            df_current.loc[mask, "riesgo"] = df_current.loc[mask].apply(clasifica_row_by_profit, axis=1)

            # Guardar y refrescar
            df_current.to_csv(CSV_PATH, index=False)
            snackbar.content = ft.Text("Registro actualizado.")
            snackbar.open = True
            refresh_all()
            # garantizar actualización de conclusiones y mostrar confirmación
            update_conclusiones(ensure_dataframe())
            # limpiar campos de captura después de actualizar
            fecha_field.value = ""
            ingresos_field.value = ""
            gf_field.value = ""
            gv_field.value = ""
            ventas_field.value = ""
            act_field.value = ""
            pas_field.value = ""
            page.update()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al actualizar: {ex}")
            snackbar.open = True
            page.update()

    # Eliminar seleccionados
    def delete_selected(e: ft.ControlEvent):
        try:
            print("delete_selected called, selected_ids=", selected_ids)
            if not selected_ids:
                snackbar.content = ft.Text("No hay registros seleccionados.")
                snackbar.open = True
                page.update()
                return
            # Eliminación inmediata con backup
            bak = CSV_PATH + ".bak"
            shutil.copy2(CSV_PATH, bak)
            df_current = ensure_dataframe()
            df_current = df_current[~df_current["id"].isin(list(selected_ids))]
            df_current.to_csv(CSV_PATH, index=False)
            selected_ids.clear()
            snackbar.content = ft.Text(f"Registros eliminados. Backup: {bak}")
            snackbar.open = True
            refresh_all()
            # garantizar actualización de conclusiones y mostrar confirmación
            update_conclusiones(ensure_dataframe())
            page.update()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al preparar eliminación: {ex}")
            snackbar.open = True
            page.update()

    # Editar seleccionado (solo 1)
    def edit_selected(e: ft.ControlEvent):
        try:
            print("edit_selected called, selected_ids=", selected_ids)
            if len(selected_ids) != 1:
                snackbar.content = ft.Text("Selecciona exactamente 1 registro para editar.")
                snackbar.open = True
                page.update()
                return
            # volcar los datos del registro seleccionado en los campos de captura para editar
            target = next(iter(selected_ids))
            df_current = ensure_dataframe()
            if target not in df_current["id"].values:
                snackbar.content = ft.Text("Registro no encontrado para editar.")
                snackbar.open = True
                page.update()
                return
            row = df_current[df_current["id"] == target].iloc[0]
            # poblar campos de captura
            fecha_field.value = str(row.get("fecha", ""))
            ingresos_field.value = str(row.get("ingresos", ""))
            gf_field.value = str(row.get("gastos_fijos", ""))
            gv_field.value = str(row.get("gastos_variables", ""))
            ventas_field.value = str(row.get("ventas", ""))
            act_field.value = str(row.get("activos_corrientes", ""))
            pas_field.value = str(row.get("pasivos_corrientes", ""))
            edit_target_id["id"] = int(target)
            snackbar.content = ft.Text("Editando registro en los campos de captura. Modifica y pulsa 'Recargar datos' para guardar.")
            snackbar.open = True
            page.update()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al preparar edición: {ex}")
            snackbar.open = True
            page.update()

    def open_edit_dialog(target_id: int):
        try:
            df_current = ensure_dataframe()
            if target_id not in df_current["id"].values:
                snackbar.content = ft.Text("Registro no encontrado para editar.")
                snackbar.open = True
                page.update()
                return
            row = df_current[df_current["id"] == target_id].iloc[0]

            ef_fecha = ft.TextField(label="Fecha (YYYY-MM-DD)", value=str(row.get("fecha", "")))
            ef_ing = ft.TextField(label="Ingresos", value=str(row.get("ingresos", "")))
            ef_gf = ft.TextField(label="Gastos fijos", value=str(row.get("gastos_fijos", "")))
            ef_gv = ft.TextField(label="Gastos variables", value=str(row.get("gastos_variables", "")))
            ef_ventas = ft.TextField(label="Ventas", value=str(row.get("ventas", "")))
            ef_act = ft.TextField(label="Activos corrientes", value=str(row.get("activos_corrientes", "")))
            ef_pas = ft.TextField(label="Pasivos corrientes", value=str(row.get("pasivos_corrientes", "")))

            def save_edit(ev):
                try:
                    new_vals = {
                        "fecha": ef_fecha.value,
                        "ingresos": ef_ing.value,
                        "gastos_fijos": ef_gf.value,
                        "gastos_variables": ef_gv.value,
                        "ventas": ef_ventas.value,
                        "activos_corrientes": ef_act.value,
                        "pasivos_corrientes": ef_pas.value,
                    }
                    update_by_id(target_id, new_vals)
                finally:
                    page.dialog.close()

            edit_dialog = ft.AlertDialog(
                title=ft.Text("Editar registro"),
                content=ft.Column([ef_fecha, ef_ing, ef_gf, ef_gv, ef_ventas, ef_act, ef_pas], spacing=8),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda ev: page.dialog.close()),
                    ft.ElevatedButton("Guardar", on_click=save_edit),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.dialog = edit_dialog
            page.dialog.open = True
            page.update()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al abrir diálogo de edición: {ex}")
            snackbar.open = True
            page.update()

    def build_table(dfi: pd.DataFrame) -> ft.Column:
        # mostrar columnas con nombres cortos; mapear a las columnas reales del DataFrame
        cols = [
            "id",
            "fecha",
            "mes",
            "ingresos",
            "gastos_F",
            "gastos_V",
            "gastos_T",
            "ventas",
            "activos",
            "pasivos",
            "margen_gan",
            "liquidez",
            "riesgo",
        ]

        mapping = {
            "id": "id",
            "fecha": "fecha",
            "mes": "mes",
            "ingresos": "ingresos",
            "gastos_F": "gastos_fijos",
            "gastos_V": "gastos_variables",
            "gastos_T": "gastos_totales",
            "ventas": "ventas",
            "activos": "activos_corrientes",
            "pasivos": "pasivos_corrientes",
            "margen_gan": "margen_ganancia",
            "liquidez": "liquidez_corriente",
            "riesgo": "riesgo",
        }

        # construir DataFrame de visualización con columnas cortas (si la columna real existe, copiarla)
        display_df = pd.DataFrame()
        for disp in cols:
            real = mapping.get(disp, disp)
            if real in dfi.columns:
                display_df[disp] = dfi[real]
            else:
                display_df[disp] = np.nan

        # asegurar tipo fecha en la columna de visualización para orden correcto
        if "fecha" in display_df.columns:
            display_df["fecha"] = _smart_parse_dates(display_df["fecha"]) if "fecha" in display_df.columns else pd.NaT
        if "mes" in display_df.columns:
            display_df["mes"] = _smart_parse_dates(display_df["mes"]) if "mes" in display_df.columns else pd.NaT

        # usar display_df para las operaciones posteriores
        dfi = display_df.copy()

        def fmt(v):
            if isinstance(v, float):
                return f"{v:.2f}"
            return str(v)

        # Aplicar búsqueda simple sobre stringified row
        if table_page["query"]:
            q = table_page["query"].lower()
            mask = dfi.apply(lambda r: r.astype(str).str.lower().str.contains(q).any(), axis=1)
            filtered = dfi[mask]
        else:
            filtered = dfi

        # orden y paginación
        filtered = filtered.sort_values("fecha", ascending=False)
        total = len(filtered)
        start = table_page["page"] * table_page["page_size"]
        end = start + table_page["page_size"]
        page_slice = filtered.iloc[start:end]

        rows = []
        for _, r in page_slice.iterrows():
            # checkbox de selección (valor según selected_ids para persistir entre refresh)
            rid = int(r["id"]) if not pd.isna(r["id"]) else None
            sel = ft.Checkbox(value=(rid in selected_ids), data=rid, on_change=toggle_select)
            cells = [ft.DataCell(sel)]
            cells += [ft.DataCell(ft.Text(fmt(r[c]))) for c in cols]
            # botones por fila: Editar y Eliminar
            edit_btn = ft.TextButton("Editar", data=rid, on_click=lambda e, _id=rid: open_edit_dialog(_id))
            del_btn = ft.TextButton("Eliminar", data=rid, on_click=lambda e, _id=rid: delete_by_id(_id))
            actions_row_cells = ft.Row([edit_btn, del_btn], spacing=6)
            del_cell = ft.DataCell(actions_row_cells)
            cells.append(del_cell)
            rows.append(ft.DataRow(cells=cells))

        columns = [ft.DataColumn(ft.Text("Sel"))] + [ft.DataColumn(ft.Text(c)) for c in cols] + [ft.DataColumn(ft.Text("Acciones"))]

        # Controles de paginación y búsqueda
        def on_search(e):
            table_page["query"] = e.control.value or ""
            table_page["page"] = 0
            refresh_all()

        def prev_page(e):
            if table_page["page"] > 0:
                table_page["page"] -= 1
                refresh_all()

        def next_page(e):
            if end < total:
                table_page["page"] += 1
                refresh_all()

        pager = ft.Row([
            ft.ElevatedButton("Anterior", on_click=prev_page),
            ft.Text(f"Página {table_page['page']+1} / {max(1, (total+table_page['page_size']-1)//table_page['page_size'])}"),
            ft.ElevatedButton("Siguiente", on_click=next_page),
        ], alignment=ft.MainAxisAlignment.CENTER)

        search = ft.TextField(label="Buscar", on_change=on_search)

        table = ft.DataTable(
            columns=columns,
            rows=rows,
            vertical_lines=ft.BorderSide(0.2, ft.Colors.GREY_300),
            heading_row_color=ft.Colors.BLUE_50,
        )

        # botones de acciones sobre selección
        actions_row = ft.Row([
            ft.ElevatedButton("Eliminar seleccionados", bgcolor=ft.Colors.RED_400, on_click=delete_selected),
            ft.ElevatedButton("Editar seleccionado", on_click=edit_selected),
        ], spacing=10)

        return ft.Column([search, actions_row, table, pager], spacing=8)

    table_container = ft.Container(content=build_table(df), padding=10)

    # --- Gráficos (agrandados y centrados) ---
    # Creamos charts reutilizables para que refresh_all() pueda actualizar sus figuras
    chart1 = MatplotlibChart(fig_ingresos_vs_gastos_promedio(df), expand=True)
    chart2 = MatplotlibChart(fig_distribucion_riesgo(df), expand=True)
    chart3 = MatplotlibChart(fig_evolucion_mensual(df), expand=True)
    chart4 = MatplotlibChart(fig_margen_linea(df), expand=True)

    # Contenedores grandes que ocupen la mayor parte de la pantalla (fallback a height fijo)
    chart_container1 = ft.Container(content=chart1, alignment=ft.alignment.center, height=850, padding=10, expand=True)
    chart_container2 = ft.Container(content=chart2, alignment=ft.alignment.center, height=850, padding=10, expand=True)
    chart_container3 = ft.Container(content=chart3, alignment=ft.alignment.center, height=850, padding=10, expand=True)
    chart_container4 = ft.Container(content=chart4, alignment=ft.alignment.center, height=850, padding=10, expand=True)

    # --- Conclusiones / Alertas ---
    def build_conclusiones(dfi: pd.DataFrame):
        d = dfi.copy()
        if "mes" in d.columns:
            d["mes"] = _smart_parse_dates(d["mes"])
        # calcular moda de riesgo por mes (timestamp al inicio del mes)
        moda_por_mes = d.groupby(d["mes"].dt.to_period("M").dt.to_timestamp())["riesgo"].agg(
            lambda s: s.mode().iat[0] if not s.mode().empty else "MEDIO"
        )

        # formatear meses en español (abreviado)
        spanish_months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

        def fmt_spanish(ts):
            try:
                m = pd.to_datetime(ts, dayfirst=True)
                return f"{spanish_months[m.month-1]} {m.year}"
            except Exception:
                return str(ts)

        # mostrar meses por categoría separada: ALTO, MEDIO, BAJO
        alto_idx = moda_por_mes[moda_por_mes == "ALTO"].index
        medio_idx = moda_por_mes[moda_por_mes == "MEDIO"].index
        bajo_idx = moda_por_mes[moda_por_mes == "BAJO"].index

        alto_meses = [fmt_spanish(idx) for idx in alto_idx]
        medio_meses = [fmt_spanish(idx) for idx in medio_idx]
        bajo_meses = [fmt_spanish(idx) for idx in bajo_idx]

        chips = []
        if alto_meses:
            chips.append(
                ft.Chip(label=ft.Text(f"⚠ Meses con ALTO riesgo ({len(alto_meses)}): {', '.join(alto_meses)}"), bgcolor=ft.Colors.RED_50)
            )
        if medio_meses:
            chips.append(
                ft.Chip(label=ft.Text(f"ℹ Meses con RIESGO MEDIO ({len(medio_meses)}): {', '.join(medio_meses)}"), bgcolor=ft.Colors.YELLOW_50)
            )
        if bajo_meses:
            chips.append(
                ft.Chip(label=ft.Text(f"✅ Meses con BAJO riesgo ({len(bajo_meses)}): {', '.join(bajo_meses)}"), bgcolor=ft.Colors.GREEN_50)
            )

        recomend = ft.Text(
            "Sugerencia: refuerza el flujo de caja en meses con ALTO riesgo (mejorar liquidez, "
            "reducir gastos variables y fortalecer márgenes).",
            weight=ft.FontWeight.W_600,
        )
        return ft.Column([*chips, recomend], spacing=10)

    conclusiones_view = ft.Container(content=build_conclusiones(df), padding=10)
    # timestamp de última actualización de conclusiones
    last_conclusiones_update = {"ts": None}

    def update_conclusiones(dfi: pd.DataFrame, show_snackbar: bool = True):
        """Actualizar el panel de conclusiones y opcionalmente mostrar confirmación."""
        try:
            now = dt.datetime.now()
            last_conclusiones_update["ts"] = now
            ts_str = now.strftime("%Y-%m-%d %H:%M:%S")
            conclusiones_view.content = ft.Column([ft.Text(f"Última actualización: {ts_str}", size=12), build_conclusiones(dfi)])
            if show_snackbar:
                snackbar.content = ft.Text("Conclusiones actualizadas.")
                snackbar.open = True
            page.update()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al actualizar conclusiones: {ex}")
            snackbar.open = True
            page.update()

    # --- Eventos ---
    def refresh_all():
        nonlocal df, table_container, chart1, chart2, chart3, chart4, conclusiones_view
        df = ensure_dataframe()
        # reconstruir tabla y forzar update del contenedor
        table_container.content = build_table(df)
        try:
            table_container.update()
        except Exception:
            pass

        # actualizar figuras y forzar redraw de cada chart control
        try:
            chart1.figure = fig_ingresos_vs_gastos_promedio(df)
            chart1.update()
        except Exception:
            pass
        try:
            chart2.figure = fig_distribucion_riesgo(df)
            chart2.update()
        except Exception:
            pass
        try:
            chart3.figure = fig_evolucion_mensual(df)
            chart3.update()
        except Exception:
            pass
        try:
            chart4.figure = fig_margen_linea(df)
            chart4.update()
        except Exception:
            pass

        # actualizar conclusiones (sin snackbar en refresh general)
        update_conclusiones(df, show_snackbar=False)
        page.update()


    # (La lógica de eliminación está implementada arriba con confirmación y delete_by_id)

    def on_add_click(e):
        try:
            if not fecha_field.value:
                raise ValueError("Selecciona una fecha.")
            row = dict(
                fecha=fecha_field.value,
                ingresos=ingresos_field.value or 0,
                gastos_fijos=gf_field.value or 0,
                gastos_variables=gv_field.value or 0,
                ventas=ventas_field.value or 0,
                activos_corrientes=act_field.value or 0,
                pasivos_corrientes=pas_field.value or 0,
            )
            append_row(row)

            # limpiar algunos inputs
            fecha_field.value = ""
            ingresos_field.value = ""
            gf_field.value = ""
            gv_field.value = ""
            ventas_field.value = ""
            act_field.value = ""
            pas_field.value = ""

            snackbar.content = ft.Text("Registro agregado y gráficos actualizados.")
            snackbar.open = True
            refresh_all()
            # garantizar actualización de conclusiones y mostrar confirmación
            update_conclusiones(ensure_dataframe())
        except Exception as ex:
            snackbar.content = ft.Text(f"Error: {ex}")
            snackbar.open = True
            page.update()

    add_btn = ft.ElevatedButton("Agregar registro", icon=ft.Icons.ADD, on_click=on_add_click)
    # File picker para importación/exportación
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    def on_reload(e):
        # si hay un target de edición en los campos, guardarlo
        try:
            if edit_target_id.get("id"):
                tid = edit_target_id["id"]
                new_vals = {
                    "fecha": fecha_field.value,
                    "ingresos": ingresos_field.value,
                    "gastos_fijos": gf_field.value,
                    "gastos_variables": gv_field.value,
                    "ventas": ventas_field.value,
                    "activos_corrientes": act_field.value,
                    "pasivos_corrientes": pas_field.value,
                }
                print("Saving edit from capture fields for id=", tid)
                update_by_id(tid, new_vals)
                edit_target_id["id"] = None
            refresh_all()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al recargar/guardar: {ex}")
            snackbar.open = True
            page.update()

    reload_btn = ft.ElevatedButton("Recargar datos", icon=ft.Icons.REFRESH, on_click=on_reload)
    def on_normalize(e):
        try:
            normalize_csv()
            snackbar.content = ft.Text("CSV normalizado correctamente (backup: .bak_normalize).")
            snackbar.open = True
            refresh_all()
            page.update()
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al normalizar CSV: {ex}")
            snackbar.open = True
            page.update()

    normalize_btn = ft.ElevatedButton("Normalizar CSV", icon=ft.Icons.SETTINGS, on_click=on_normalize)

    # FilePicker result handler (soporta importación y 'guardar como')
    def on_filepicker_result(e: ft.FilePickerResultEvent):
        try:
            if not e.files:
                return
            op = getattr(e, "operation", None)
            # operación de guardar (export)
            if op == "save" or getattr(e, "save_path", None) is not None:
                dest = e.files[0].path
                try:
                    ensure_dataframe()  # asegura estructura
                    df_export = ensure_dataframe()
                    df_export.to_csv(dest, index=False)
                    snackbar.content = ft.Text(f"CSV exportado a: {dest}")
                    snackbar.open = True
                    # refrescar vistas para asegurar gráficas/conclusiones actualizadas
                    refresh_all()
                    update_conclusiones(ensure_dataframe())
                    page.update()
                except Exception as ex:
                    snackbar.content = ft.Text(f"Error al guardar CSV: {ex}")
                    snackbar.open = True
                    page.update()
                return

            # operación de abrir/seleccionar (import)
            src = e.files[0].path
            # validar CSV antes de reemplazar
            try:
                df_new = pd.read_csv(src)
            except Exception as ex:
                snackbar.content = ft.Text(f"No se pudo leer el CSV seleccionado: {ex}")
                snackbar.open = True
                page.update()
                return

            # Validación mínima: debe contener 'fecha' y 'ingresos', y al menos una columna de gastos
            required = {"fecha", "ingresos"}
            gastos_any = {"gastos_fijos", "gastos_variables"}
            cols = set(df_new.columns.astype(str))
            if not required.issubset(cols):
                snackbar.content = ft.Text(f"CSV inválido: faltan columnas requeridas {required - cols}")
                snackbar.open = True
                page.update()
                return
            if not (gastos_any & cols):
                snackbar.content = ft.Text(f"CSV inválido: debe contener al menos una de las columnas de gastos: {gastos_any}")
                snackbar.open = True
                page.update()
                return

            # crear backup y escribir
            if os.path.exists(CSV_PATH):
                bak = CSV_PATH + ".bak"
                shutil.copy2(CSV_PATH, bak)
            # normalizar columnas esperadas antes de guardar: mantenemos todas las columnas del CSV importado
            df_new.to_csv(CSV_PATH, index=False)
            snackbar.content = ft.Text(f"CSV importado correctamente. Backup: {CSV_PATH}.bak")
            snackbar.open = True
            refresh_all()
            update_conclusiones(ensure_dataframe())
        except Exception as ex:
            snackbar.content = ft.Text(f"Error en operación de archivo: {ex}")
            snackbar.open = True
            page.update()

    file_picker.on_result = on_filepicker_result

    def on_import_click(e):
        # abrir selector de archivo para importar
        file_picker.pick_files(allow_multiple=False)

    import_btn = ft.ElevatedButton("Importar CSV", icon=ft.Icons.UPLOAD_FILE, on_click=on_import_click)

    # Exportar CSV (Guardar como)
    def on_export_click(e):
        try:
            df_export = ensure_dataframe()
            # intentar guardar directamente en la carpeta Descargas del usuario (Windows)
            try:
                downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                if not os.path.isdir(downloads):
                    raise FileNotFoundError("Carpeta Descargas no encontrada")
                ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                dest = os.path.join(downloads, f"finanzas_empresaxyz_export_{ts}.csv")
                df_export.to_csv(dest, index=False)
                snackbar.content = ft.Text(f"CSV exportado a: {dest}")
                snackbar.open = True
                # actualizar vistas: asegurar que las gráficas reflejen los datos actuales
                refresh_all()
                update_conclusiones(ensure_dataframe())
                page.update()
                return
            except Exception:
                # fallback a diálogo de guardar (save_file)
                try:
                    file_picker.save_file(suggested_name="finanzas_empresaxyz_export.csv")
                    return
                except Exception:
                    # último recurso: guardar en el directorio actual
                    suggested = os.path.join(os.getcwd(), "finanzas_empresaxyz_export.csv")
                    df_export.to_csv(suggested, index=False)
                    snackbar.content = ft.Text(f"CSV exportado a: {suggested}")
                    snackbar.open = True
                    refresh_all()
                    update_conclusiones(ensure_dataframe())
                    page.update()
                    return
        except Exception as ex:
            snackbar.content = ft.Text(f"Error al exportar CSV: {ex}")
            snackbar.open = True
            page.update()

    export_btn = ft.ElevatedButton("Exportar CSV", icon=ft.Icons.DOWNLOAD, on_click=on_export_click)

    captura_tab = ft.Container(
        content=ft.Column(
            [
                ft.Text("Ingreso de datos diarios", size=20, weight=ft.FontWeight.W_700),
                fecha_field,
                ft.ResponsiveRow(
                    [
                        ft.Container(ingresos_field, col={"xs": 12, "md": 4}),
                        ft.Container(gf_field, col={"xs": 12, "md": 4}),
                        ft.Container(gv_field, col={"xs": 12, "md": 4}),
                        ft.Container(ventas_field, col={"xs": 12, "md": 4}),
                        ft.Container(act_field, col={"xs": 12, "md": 4}),
                        ft.Container(pas_field, col={"xs": 12, "md": 4}),
                    ],
                    run_spacing=10,
                    spacing=10,
                ),
                add_btn,
                reload_btn,
                ft.Row([import_btn, export_btn, normalize_btn], spacing=10),
                ft.Divider(),
                ft.Text("Vista de registros (últimas filas)", weight=ft.FontWeight.W_600),
                table_container,
            ],
            spacing=15,
        ),
        padding=15,
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        tabs=[
            ft.Tab(text="Captura de datos", content=captura_tab, icon=ft.Icons.EDIT_NOTE),
            ft.Tab(
                text="Ingresos vs Gastos (mes)",
                icon=ft.Icons.BAR_CHART,
                content=ft.Container(chart_container1, padding=10),
            ),
            ft.Tab(
                text="Distribución de Riesgo",
                icon=ft.Icons.SHOW_CHART,
                content=ft.Container(chart_container2, padding=10),
            ),
            ft.Tab(
                text="Evolución mensual",
                icon=ft.Icons.TIMELINE,
                content=ft.Container(chart_container3, padding=10),
            ),
            ft.Tab(
                text="Margen por mes",
                icon=ft.Icons.LINE_AXIS,
                content=ft.Container(chart_container4, padding=10),
            ),
            ft.Tab(text="Conclusiones", icon=ft.Icons.LIGHTBULB, content=ft.Container(conclusiones_view, padding=10)),
        ],
    )

    page.add(tabs, snackbar)


if __name__ == "__main__":
    ft.app(target=main)
