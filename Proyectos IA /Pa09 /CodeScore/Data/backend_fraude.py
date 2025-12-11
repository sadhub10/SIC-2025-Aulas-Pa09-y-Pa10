#CodeScore
import os
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd

#---------------------CONFIGURACIÓN GENERAL---------------------

# Rutas de modelos 
ISO_MODEL_PATH = "Data/modelo_isoforest_paysim_optimo.pkl"  # IsolationForest
SCALER_PATH = "Data/scaler_paysim.pkl"                    
XGB_MODEL_PATH = "Data/modelo_xgb_fraude.pkl"              # XGBoost supervisado

# Archivos "BD" CSV
USUARIOS_CSV = "Data/usuarios.csv"
TRANSACCIONES_CSV = "Data/transacciones.csv"

# Password solo para demo
ADMIN_PASSWORD = "admin123"

# Umbral de Isolation Forest
IF_THRESHOLD = 0.6


#---------------------VARIABLES GLOBALES---------------------

_usuarios_df: pd.DataFrame | None = None
_tx_df: pd.DataFrame | None = None

_iso_model = None
_xgb_model = None
_scaler = None
_xgb_features: list[str] = []
_if_threshold: float = IF_THRESHOLD


#---------------------UTILIDADES INTERNAS---------------------

def _safe_float(v, default=0.0) -> float:
    """Convierte a float de forma segura."""
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default

def _cargar_usuarios():
    global _usuarios_df
    if os.path.exists(USUARIOS_CSV):
        _usuarios_df = pd.read_csv(USUARIOS_CSV, dtype={"cedula": str})
        if "saldo" not in _usuarios_df.columns:
            _usuarios_df["saldo"] = 0.0
    else:
        _usuarios_df = pd.DataFrame(columns=["cedula", "nombre", "saldo"])
    _usuarios_df["cedula"] = _usuarios_df["cedula"].astype(str)

def _guardar_usuarios():
    global _usuarios_df
    if _usuarios_df is not None:
        _usuarios_df.to_csv(USUARIOS_CSV, index=False)

def _cargar_transacciones():
    global _tx_df
    if os.path.exists(TRANSACCIONES_CSV):
        _tx_df = pd.read_csv(TRANSACCIONES_CSV)
    else:
        _tx_df = pd.DataFrame(
            columns=[
                "tx_id",
                "cedula",
                "timestamp_eval",
                "type",
                "Amount",
                "saldo_resultante",
                "prob_fraude",
                "riesgo",
                "recomendacion",
                "justificacion_resumen",
            ]
        )

def _guardar_transacciones():
    global _tx_df
    if _tx_df is not None:
        _tx_df.to_csv(TRANSACCIONES_CSV, index=False)

def _obtener_saldo_usuario(cedula: str) -> float:
    global _usuarios_df
    df = _usuarios_df
    if df is None or df.empty:
        return 0.0
    fila = df[df["cedula"] == str(cedula)]
    if fila.empty:
        return 0.0
    return _safe_float(fila.iloc[0]["saldo"], 0.0)

def _actualizar_saldo_usuario(cedula: str, nuevo_saldo: float):
    global _usuarios_df
    df = _usuarios_df
    if df is None or df.empty:
        return
    idx = df.index[df["cedula"] == str(cedula)]
    if len(idx) == 0:
        return
    _usuarios_df.loc[idx, "saldo"] = nuevo_saldo
    _guardar_usuarios()


#---------------------CARGA DE MODELOS---------------------

def _cargar_modelos():
    """Carga modelos si existen. Si falta alguno, se continúa sin romper."""
    global _iso_model, _xgb_model, _scaler, _xgb_features, _if_threshold

    # Isolation Forest
    if _iso_model is None and os.path.exists(ISO_MODEL_PATH):
        try:
            _iso_model = joblib.load(ISO_MODEL_PATH)
        except Exception as ex:
            print(f"[WARN] No se pudo cargar IsolationForest: {ex}")
            _iso_model = None
    elif not os.path.exists(ISO_MODEL_PATH):
        print(f"[WARN] No se encontró {ISO_MODEL_PATH}. Se omitirá IsolationForest.")

    # XGBoost
    if _xgb_model is None and os.path.exists(XGB_MODEL_PATH):
        try:
            _xgb_model = joblib.load(XGB_MODEL_PATH)
        except Exception as ex:
            print(f"[WARN] No se pudo cargar XGBoost: {ex}")
            _xgb_model = None
    elif not os.path.exists(XGB_MODEL_PATH):
        print(f"[WARN] No se encontró {XGB_MODEL_PATH}. No habrá modelo supervisado.")

    # Scaler
    if _scaler is None and os.path.exists(SCALER_PATH):
        try:
            _scaler = joblib.load(SCALER_PATH)
        except Exception as ex:
            print(f"[WARN] No se pudo cargar SCALER: {ex}")
            _scaler = None
    elif not os.path.exists(SCALER_PATH):
        print(f"[WARN] No se encontró {SCALER_PATH}. Se usará entrada sin escalar.")

    # IMPORTANTE: columnas de entrenamiento de XGBoost
    _xgb_features = [
        "type",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "n_tx_ultima_hora",
        "n_tx_mismo_monto_ultima_hora",
        "n_tx_totales_usuario",
    ]

    _if_threshold = IF_THRESHOLD


#---------------------PREPROCESAMIENTO PARA MODELOS---------------------

def _preprocesar_para_modelos(entrada: dict):
    """
    Prepara X_raw (para XGBoost) con nombres correctos
    y X_scaled (para Isolation Forest).
    """
    global _xgb_features, _scaler

    vals = {
        "type": entrada.get("type", "TRANSFER"),
        "amount": _safe_float(entrada.get("amount")),
        "oldbalanceOrg": _safe_float(entrada.get("oldbalanceOrg")),
        "newbalanceOrig": _safe_float(entrada.get("newbalanceOrig")),
        "oldbalanceDest": _safe_float(entrada.get("oldbalanceDest")),
        "newbalanceDest": _safe_float(entrada.get("newbalanceDest")),
        "n_tx_ultima_hora": int(entrada.get("n_tx_ultima_hora", 0) or 0),
        "n_tx_mismo_monto_ultima_hora": int(
            entrada.get("n_tx_mismo_monto_ultima_hora", 0) or 0
        ),
        "n_tx_totales_usuario": int(entrada.get("n_tx_totales_usuario", 0) or 0),
    }

    # Codificación de tipo
    type_map = {"CASH_IN": 0, "CASH_OUT": 1, "TRANSFER": 2, "PAYMENT": 3, "DEBIT": 4}
    vals["type"] = type_map.get(vals["type"], 0)

    # Siempre DataFrame con columnas correctas
    X_raw = pd.DataFrame([[vals[c] for c in _xgb_features]], columns=_xgb_features)

    # Escalado para Isolation Forest (si hay scaler)
    if _scaler is not None:
        try:
            X_scaled = _scaler.transform(X_raw)
        except Exception as ex:
            print(f"[WARN] Error al escalar datos: {ex}")
            X_scaled = X_raw.values
    else:
        X_scaled = X_raw.values

    return X_raw, X_scaled


#---------------------FUNCIÓN PRINCIPAL DE PREDICCIÓN---------------------

def predecir_fraude_combinado(entrada: dict) -> dict:
    """
    Combina:
      - Isolation Forest (anomalías)
      - XGBoost (probabilidad supervisada)
    y aplica REGLAS DE NEGOCIO.
    """
    global _iso_model, _xgb_model, _if_threshold

    X_raw, X_scaled = _preprocesar_para_modelos(entrada)

    # --- Isolation Forest ---
    if _iso_model is not None:
        try:
            score_if = float(-_iso_model.decision_function(X_scaled)[0])
            alerta_if = score_if >= _if_threshold
        except Exception as ex:
            print(f"[WARN] Error en IsolationForest: {ex}")
            score_if = 0.0
            alerta_if = False
    else:
        score_if = 0.0
        alerta_if = False

    # --- XGBoost supervisado ---
    if _xgb_model is not None:
        try:
            prob_ml = float(_xgb_model.predict_proba(X_raw)[0, 1])
        except Exception as ex:
            print(f"[WARN] Error en XGBoost: {ex}")
            prob_ml = 0.0
    else:
        prob_ml = 0.0

    prob_aj = prob_ml

    # --- datos contables ---
    amount = _safe_float(entrada.get("amount"))
    old_org = _safe_float(entrada.get("oldbalanceOrg"))
    new_org = _safe_float(entrada.get("newbalanceOrig"))
    old_dest = _safe_float(entrada.get("oldbalanceDest"))
    new_dest = _safe_float(entrada.get("newbalanceDest"))

    # --- contexto temporal ---
    n_tx_ultima_hora = int(entrada.get("n_tx_ultima_hora", 0) or 0)
    n_tx_mismo_monto_ultima_hora = int(
        entrada.get("n_tx_mismo_monto_ultima_hora", 0) or 0
    )
    n_tx_totales = int(entrada.get("n_tx_totales_usuario", 0) or 0)

    explicaciones: list[str] = []

    # 1) Monto vs saldo
    if old_org > 0:
        ratio = amount / (old_org + 1e-6)
        if ratio >= 4.0:
            explicaciones.append(
                "El monto de la transacción es más de cuatro veces superior al saldo disponible de la cuenta de origen."
            )
            prob_aj = min(1.0, max(prob_aj * 2.0, 0.75))
        elif ratio >= 3.0:
            explicaciones.append(
                "El monto de la transacción es más de tres veces superior al saldo disponible de la cuenta de origen."
            )
            prob_aj = min(1.0, max(prob_aj * 1.5, 0.6))
        elif ratio >= 0.8:
            explicaciones.append(
                "El monto de la transacción consume casi la totalidad del saldo disponible de la cuenta de origen."
            )
        elif ratio >= 0.4:
            explicaciones.append(
                "El monto representa una proporción significativa del saldo de la cuenta de origen."
            )
        else:
            explicaciones.append(
                "El monto representa solo una fracción moderada del saldo de la cuenta de origen."
            )
    else:
        if amount > 0:
            explicaciones.append(
                "Se registra una transacción con monto positivo sin un saldo previo positivo en la cuenta de origen."
            )

    # 2) Sobregiro
    sobregiro = new_org < 0
    if sobregiro:
        explicaciones.append(
            f"La transacción deja la cuenta de origen con saldo negativo (saldo final = {new_org:.2f})."
        )
        prob_aj = min(1.0, max(prob_aj, prob_ml * 1.8, 0.75))

    # 3) Frecuencia en la última hora
    if n_tx_ultima_hora >= 3:
        explicaciones.append(
            "Se han registrado varias transacciones en menos de una hora, lo cual incrementa el riesgo de uso fraudulento de la cuenta."
        )
        prob_aj = min(1.0, max(prob_aj, prob_ml * 1.7, 0.7))

    if n_tx_mismo_monto_ultima_hora >= 2:
        explicaciones.append(
            "Se han realizado tres o más transacciones con el mismo monto en un intervalo muy corto, patrón típico de automatización o prueba de tarjetas."
        )
        prob_aj = min(1.0, max(prob_aj, prob_ml * 1.8, 0.75))

    # 4) Montos altos en primeras transacciones
    if n_tx_totales == 0 and amount >= 5000:
        explicaciones.append(
            "Es una de las primeras transacciones registradas para este usuario y ya involucra un monto elevado, lo cual puede indicar uso indebido de la cuenta."
        )
        prob_aj = min(1.0, max(prob_aj, prob_ml * 1.5, 0.6))

    # 5) Cuenta destino sin saldo previo
    if old_dest == 0 and new_dest > 0 and amount > 0:
        explicaciones.append(
            "La cuenta de destino no presentaba saldo previo y recibe fondos en esta operación."
        )

    # 6) Info general
    explicaciones.append(
        "El sistema analiza el patrón de la operación considerando comportamiento histórico del usuario y de transacciones similares."
    )

    # 7) Resultado Isolation Forest
    if alerta_if:
        explicaciones.append(
            "El detector de anomalías considera que el patrón global de la transacción es atípico."
        )
        prob_aj = min(1.0, max(prob_aj, prob_ml * 1.3, 0.6))
    else:
        explicaciones.append(
            "El detector de anomalías no identifica patrones claramente fuera de lo habitual en esta operación."
        )

    # 8) Nivel de riesgo
    if prob_aj >= 0.80 or (alerta_if and prob_aj >= 0.50) or (
        sobregiro and amount >= abs(old_org) * 1.2
    ):
        riesgo = "ALTO"
    elif prob_aj >= 0.40 or alerta_if or sobregiro:
        riesgo = "MEDIO"
    else:
        riesgo = "BAJO"

    if riesgo == "ALTO":
        explicaciones.insert(
            0,
            f"El sistema detecta una probabilidad ALTA de fraude (alrededor de {prob_aj*100:.1f}%).",
        )
    elif riesgo == "MEDIO":
        explicaciones.insert(
            0,
            f"El sistema identifica un riesgo MODERADO de fraude (alrededor de {prob_aj*100:.1f}%).",
        )
    else:
        explicaciones.insert(
            0,
            f"El sistema estima una probabilidad BAJA de fraude (alrededor de {prob_aj*100:.1f}%).",
        )

    # 9) Recomendaciones
    recomendaciones: list[str] = []
    if riesgo == "ALTO":
        recomendaciones.append(
            "Bloquear temporalmente la transacción y/o la tarjeta asociada hasta completar una verificación manual."
        )
        recomendaciones.append(
            "Contactar al titular por un canal oficial para confirmar la operación."
        )
        recomendaciones.append(
            "Revisar ubicación, comercio y dispositivo desde el cual se originó la transacción."
        )
    elif riesgo == "MEDIO":
        recomendaciones.append(
            "Permitir la transacción con monitoreo reforzado de las siguientes operaciones del cliente."
        )
        recomendaciones.append(
            "Aplicar un segundo factor de autenticación antes de aprobar montos similares."
        )
        recomendaciones.append(
            "Notificar al cliente mediante alerta o notificación push sobre la operación realizada."
        )
    else:
        recomendaciones.append(
            "Aprobar la transacción; los patrones observados son consistentes con el comportamiento normal."
        )
        recomendaciones.append(
            "Mantener monitoreo estándar del cliente sin acciones adicionales."
        )

    justificacion = " ".join(explicaciones)
    recomendacion = " ".join(recomendaciones)

    return {
        "prob_fraude": prob_aj,
        "score_if": score_if,
        "alerta_if": alerta_if,
        "riesgo_final": riesgo,
        "recomendacion": recomendacion,
        "justificacion_resumen": justificacion,
    }

#---------------------CREACIÓN DE TRANSACCIONES---------------------

def crear_transaccion_para_usuario(cedula: str, entrada: dict) -> dict:
    """
    Usa el saldo actual del usuario para construir old/newbalance,
    ejecuta los modelos y actualiza el saldo.
    """
    global _tx_df

    tipo = entrada.get("type", "CASH_OUT")
    amount_val = _safe_float(entrada.get("amount"))

    saldo_actual = _obtener_saldo_usuario(cedula)

    # Regla: si ya está negativo y no es ingreso, bloquear
    if saldo_actual < 0 and tipo != "CASH_IN":
        raise ValueError(
            "La cuenta se encuentra en saldo negativo. "
            "Solo se permiten transacciones de depósito (CASH_IN) hasta regularizar el saldo."
        )

    # Cálculo de saldos
    if tipo == "CASH_IN":
        old_org = saldo_actual
        new_org = saldo_actual + amount_val
    else:
        old_org = saldo_actual
        new_org = saldo_actual - amount_val

    old_dest = 0.0
    new_dest = amount_val

    # Timestamp
    ts_eval = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "timestamp_manual" in entrada and entrada["timestamp_manual"]:
        ts_eval = str(entrada["timestamp_manual"])

    # CONTEXTO: historial reciente del usuario
    n_tx_ultima_hora = 0
    n_tx_mismo_monto_ultima_hora = 0
    n_tx_totales = 0

    try:
        if _tx_df is not None and not _tx_df.empty:
            df_hist = _tx_df[_tx_df["cedula"] == str(cedula)].copy()
            if not df_hist.empty:
                n_tx_totales = len(df_hist)
                df_hist["ts_dt"] = pd.to_datetime(
                    df_hist["timestamp_eval"], errors="coerce"
                )
                ts_actual = pd.to_datetime(ts_eval, errors="coerce")
                if pd.notnull(ts_actual):
                    ventana_inicio = ts_actual - timedelta(hours=1)
                    mask_hora = (df_hist["ts_dt"] >= ventana_inicio) & (
                        df_hist["ts_dt"] <= ts_actual
                    )
                    df_1h = df_hist[mask_hora]
                    n_tx_ultima_hora = len(df_1h)
                    if "Amount" in df_1h.columns:
                        n_tx_mismo_monto_ultima_hora = int(
                            (df_1h["Amount"] == amount_val).sum()
                        )
    except Exception as ex:
        # no romper por un fallo en el contexto
        print(f"[WARN] Error al calcular contexto temporal: {ex}")
        n_tx_ultima_hora = 0
        n_tx_mismo_monto_ultima_hora = 0
        n_tx_totales = 0

    entrada_final = dict(entrada)
    entrada_final["amount"] = amount_val
    entrada_final["oldbalanceOrg"] = old_org
    entrada_final["newbalanceOrig"] = new_org
    entrada_final["oldbalanceDest"] = old_dest
    entrada_final["newbalanceDest"] = new_dest
    entrada_final["n_tx_ultima_hora"] = int(n_tx_ultima_hora)
    entrada_final["n_tx_mismo_monto_ultima_hora"] = int(
        n_tx_mismo_monto_ultima_hora
    )
    entrada_final["n_tx_totales_usuario"] = int(n_tx_totales)

    pred = predecir_fraude_combinado(entrada_final)

    # nuevo ID
    if _tx_df is None or _tx_df.empty:
        next_id = 1
    else:
        next_id = int(_tx_df["tx_id"].max()) + 1

    nueva_fila = {
        "tx_id": next_id,
        "cedula": str(cedula),
        "timestamp_eval": ts_eval,
        "type": tipo,
        "Amount": amount_val,
        "saldo_resultante": new_org,
        "prob_fraude": pred["prob_fraude"],
        "riesgo": pred["riesgo_final"],
        "recomendacion": pred["recomendacion"],
        "justificacion_resumen": pred["justificacion_resumen"],
    }

    if _tx_df is None or _tx_df.empty:
        _tx_df = pd.DataFrame([nueva_fila])
    else:
        _tx_df = pd.concat([_tx_df, pd.DataFrame([nueva_fila])], ignore_index=True)

    _guardar_transacciones()
    _actualizar_saldo_usuario(cedula, new_org)

    return {"tx_id": next_id, "prediccion": pred}


#---------------------FUNCIONES PÚBLICAS---------------------

def inicializar_backend():
    """Carga modelos, usuarios y transacciones."""
    _cargar_modelos()
    _cargar_usuarios()
    _cargar_transacciones()

def validar_password_admin(pwd: str) -> bool:
    return str(pwd) == ADMIN_PASSWORD

def obtener_usuarios() -> pd.DataFrame:
    global _usuarios_df
    if _usuarios_df is None:
        _cargar_usuarios()
    return _usuarios_df.copy()

def crear_usuario(cedula: str, nombre: str) -> bool:
    global _usuarios_df

    cedula = str(cedula).strip()
    nombre = str(nombre).strip()

    if not cedula or not nombre:
        raise ValueError("Debe indicar una cédula y un nombre.")

    if _usuarios_df is None:
        _cargar_usuarios()

    if (_usuarios_df["cedula"] == cedula).any():
        return False

    nueva_fila = {"cedula": cedula, "nombre": nombre, "saldo": 0.0}
    _usuarios_df = pd.concat(
        [_usuarios_df, pd.DataFrame([nueva_fila])], ignore_index=True
    )
    _guardar_usuarios()
    return True

def obtener_resumen_usuario(cedula: str) -> dict:
    global _tx_df
    saldo = _obtener_saldo_usuario(cedula)

    if _tx_df is None or _tx_df.empty:
        return {"saldo_actual": saldo, "total_transacciones": 0, "ultimas": []}

    df_user = _tx_df[_tx_df["cedula"] == str(cedula)].copy()
    if df_user.empty:
        return {"saldo_actual": saldo, "total_transacciones": 0, "ultimas": []}

    df_user = df_user.sort_values("tx_id", ascending=False)
    ultimas = []
    for _, row in df_user.head(5).iterrows():
        ultimas.append(
            {
                "tx_id": int(row["tx_id"]),
                "timestamp": row["timestamp_eval"],
                "tipo": row["type"],
                "monto": _safe_float(row["Amount"]),
                "riesgo": row["riesgo"],
            }
        )

    return {
        "saldo_actual": saldo,
        "total_transacciones": len(df_user),
        "ultimas": ultimas,
    }

def obtener_transacciones_por_usuario(cedula: str) -> pd.DataFrame:
    global _tx_df
    if _tx_df is None or _tx_df.empty:
        return pd.DataFrame(
            columns=[
                "tx_id",
                "cedula",
                "timestamp_eval",
                "type",
                "Amount",
                "saldo_resultante",
                "prob_fraude",
                "riesgo",
                "recomendacion",
                "justificacion_resumen",
            ]
        )
    df = _tx_df[_tx_df["cedula"] == str(cedula)].copy()
    df = df.sort_values("tx_id", ascending=True)
    return df

def obtener_transaccion_por_id(tx_id: int) -> dict | None:
    global _tx_df
    if _tx_df is None or _tx_df.empty:
        return None
    fila = _tx_df[_tx_df["tx_id"] == int(tx_id)]
    if fila.empty:
        return None
    return fila.iloc[0].to_dict()

def eliminar_usuario(cedula: str) -> bool:
    global _usuarios_df, _tx_df

    cedula = str(cedula)

    if _usuarios_df is None:
        _cargar_usuarios()

    if (_usuarios_df["cedula"] == cedula).sum() == 0:
        return False

    _usuarios_df = _usuarios_df[_usuarios_df["cedula"] != cedula]
    _guardar_usuarios()

    if _tx_df is not None and not _tx_df.empty:
        _tx_df = _tx_df[_tx_df["cedula"] != cedula]
        _guardar_transacciones()

    return True

def eliminar_transaccion(tx_id: int) -> bool:
    global _tx_df

    if _tx_df is None or _tx_df.empty:
        return False

    tx_id = int(tx_id)
    if (_tx_df["tx_id"] == tx_id).sum() == 0:
        return False

    _tx_df = _tx_df[_tx_df["tx_id"] != tx_id]
    _guardar_transacciones()
    return True