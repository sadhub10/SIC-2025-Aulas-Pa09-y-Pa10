import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

# Nuevos imports para yfinance y Machine Learning
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

warnings.filterwarnings("ignore")

# --- RUTAS DE ARCHIVOS ---
FINANCIAL_FILE_PATH = "Financial Statements.csv"

# --- PALETA DE COLORES GLOBAL ---
COLOR_PRIMARY = "#1f77b4"
COLOR_SECONDARY = "#ff7f0e"
COLOR_ACCENT = "#2ca02c"
COLOR_HIST = "#1f77b4"
COLOR_PRED = "#ff7f0e"

# ======================================================================
# DICCIONARIO DE DEFINICIONES DE MÉTRICAS
# ======================================================================

METRIC_DEFS = {
    "Revenue": "Ingresos totales obtenidos por la empresa en el periodo (ventas brutas antes de gastos).",
    "Net Income": "Ganancia neta: ingresos menos todos los gastos, impuestos e intereses. Es la utilidad final.",
    "Gross Profit": "Ganancia bruta: ingresos menos el costo directo de los bienes o servicios vendidos.",
    "Gross Margin": "Porcentaje de la ganancia bruta respecto a los ingresos. Mide la eficiencia en la producción o venta.",
    "Net Profit Margin": "Margen neto: porcentaje de la ganancia neta respecto a los ingresos. Mide cuánta utilidad se obtiene de cada unidad de venta.",
    "ROE": "Return on Equity: rentabilidad generada sobre el capital de los accionistas.",
    "ROA": "Return on Assets: rentabilidad generada sobre el total de activos de la empresa.",
    "PE Ratio": "Price to Earnings Ratio: cuántas veces la ganancia anual está pagando el mercado por la acción.",
    "Current Ratio": "Relación entre activos corrientes y pasivos corrientes. Mide la capacidad de pagar obligaciones de corto plazo.",
    "Debt/Equity Ratio": "Relación deuda/capital: indica qué tanto se financia la empresa con deuda frente a capital propio.",
}

# ======================================================================
# FUNCIONES AUXILIARES: CSV ORIGINAL
# ======================================================================

@st.cache_data
def load_and_clean_data(file_path):
    """Carga y limpia el DataFrame completo desde CSV una sola vez."""
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_csv(file_path)
        # Limpiar y estandarizar nombres de columna
        df.columns = df.columns.str.strip()
        df['Company'] = df['Company'].astype(str).str.strip().str.upper()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce', downcast='integer')

        # Calcular Ratios Clave en la carga
        if 'Gross Profit' in df.columns and 'Revenue' in df.columns:
            df['Gross Margin'] = (df['Gross Profit'] / df['Revenue']) * 100

        # Manejar la división por cero para PE Ratio
        if 'Market Cap(in B USD)' in df.columns and 'Net Income' in df.columns:
            df['PE Ratio'] = np.where(
                df['Net Income'] != 0,
                (df['Market Cap(in B USD)'] * 1000) / df['Net Income'],
                np.nan
            )

        return df
    except Exception as e:
        st.error(f"Error al cargar o limpiar los datos: {e}")
        return None


def format_currency(value, decimals=2):
    """Formatea un número grande como moneda (ej: $12.34M)."""
    if pd.isna(value) or value == 0:
        return "-"
    value = float(value)
    if abs(value) >= 1e9:
        return f"${value/1e9:,.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:,.{decimals}f}M"
    else:
        return f"${value:,.{decimals}f}"


def format_percentage(value):
    """Formatea un valor como porcentaje."""
    if pd.isna(value):
        return "-"
    return f"{value:.2f}%"


def procesar_datos_financieros(df_base, empresa_simbolos):
    """Procesa los datos para las empresas seleccionadas (modo CSV)."""
    if df_base is None or not empresa_simbolos:
        return {}

    data_dict = {}

    df_filtered = df_base[df_base['Company'].isin(empresa_simbolos)].copy()

    for empresa in empresa_simbolos:
        df_empresa_hist = df_filtered[df_filtered['Company'] == empresa].sort_values(by='Year').copy()

        if df_empresa_hist.empty:
            continue

        latest_year = df_empresa_hist['Year'].max()
        data_point = df_empresa_hist[df_empresa_hist['Year'] == latest_year].iloc[0].copy().fillna(0)

        data_dict[empresa] = {
            'historial_df': df_empresa_hist,
            'empresa': data_point['Company'],
            'año': latest_year,
            'Revenue': data_point.get('Revenue', 0),
            'Net Income': data_point.get('Net Income', 0),
            'Gross Margin': data_point.get('Gross Margin', 0),
            'Net Margin': data_point.get('Net Profit Margin', 0),
            'ROE': data_point.get('ROE', 0),
            'ROA': data_point.get('ROA', 0),
            'PE Ratio': data_point.get('PE Ratio', 0),
        }

    return data_dict


@st.cache_data
def obtener_datos_para_global(df_base):
    """Calcula métricas medianas de la industria y devuelve el DF con ratios."""
    if df_base is None:
        return None

    required_cols = ['Revenue', 'Net Income', 'Net Profit Margin', 'Gross Margin', 'ROE', 'ROA']
    df = df_base.dropna(subset=required_cols).copy()

    if df.empty:
        return {'Total_Companies': 0, 'Net_Margin_Median': 0, 'df_full': pd.DataFrame()}

    global_metrics = {
        'Revenue_Median': df['Revenue'].median(),
        'Net_Income_Median': df['Net Income'].median(),
        'Gross_Margin_Median': df['Gross Margin'].median(),
        'Net_Margin_Median': df['Net Profit Margin'].median(),
        'ROE_Median': df['ROE'].median(),
        'ROA_Median': df['ROA'].median(),
        'Total_Companies': df['Company'].nunique(),
        'df_full': df
    }

    return global_metrics

# ======================================================================
# NUEVA FUNCIÓN: YFINANCE COMPLETO (LÓGICA MEJORADA)
# ======================================================================

@st.cache_data
def yf_get_full_financials(symbol: str):
    """
    Construye un DataFrame financiero completo usando yfinance,
    combinando estado de resultados, balance general y flujo de caja,
    con fallback anual ↔ trimestral y cálculo de métricas extra.
    """
    ticker = yf.Ticker(symbol)

    # Info básica
    info = ticker.info if isinstance(ticker.info, dict) else {}
    company_name = info.get("longName", info.get("shortName", symbol))

    # Estados financieros crudos
    income_stmt = ticker.financials
    income_stmt_q = ticker.quarterly_financials

    balance_sheet = ticker.balance_sheet
    balance_sheet_q = ticker.quarterly_balance_sheet

    cash_flow = ticker.cashflow
    cash_flow_q = ticker.quarterly_cashflow

    use_quarterly = False

    # Si falta algo anual, intentamos con trimestral
    if income_stmt.empty or balance_sheet.empty or cash_flow.empty:
        if not income_stmt_q.empty and not balance_sheet_q.empty and not cash_flow_q.empty:
            income_stmt = income_stmt_q
            balance_sheet = balance_sheet_q
            cash_flow = cash_flow_q
            use_quarterly = True
        else:
            raise ValueError(f"No hay datos financieros anuales ni trimestrales suficientes para {symbol}")

    # Transponer para que las fechas queden como índice
    income_stmt = income_stmt.T.sort_index()
    balance_sheet = balance_sheet.T.sort_index()
    cash_flow = cash_flow.T.sort_index()

    # Fechas comunes u unión de todas
    common_dates = income_stmt.index.intersection(balance_sheet.index).intersection(cash_flow.index)

    if len(common_dates) == 0:
        all_dates = income_stmt.index.union(balance_sheet.index).union(cash_flow.index).sort_values()
        income_stmt = income_stmt.reindex(all_dates)
        balance_sheet = balance_sheet.reindex(all_dates)
        cash_flow = cash_flow.reindex(all_dates)
        dates_to_use = all_dates
    else:
        income_stmt = income_stmt.loc[common_dates]
        balance_sheet = balance_sheet.loc[common_dates]
        cash_flow = cash_flow.loc[common_dates]
        dates_to_use = common_dates

    # Construimos DF base con índice = fechas
    idx = pd.Index(dates_to_use, name="Date")
    df = pd.DataFrame(index=idx)
    df["Date"] = df.index

    # Año y periodo (año o trimestre)
    if use_quarterly:
        df["Year"] = df["Date"].dt.year
        df["Period"] = df["Date"].apply(lambda x: f"Q{x.quarter} {x.year}")
    else:
        df["Year"] = df["Date"].dt.year
        df["Period"] = df["Year"].astype(str)

    # --- Helper tipo "get_value" ---
    def get_value(frame, possible_cols, default=np.nan):
        """Devuelve una Serie alineada con df.index, buscando la primera columna existente y no vacía."""
        if frame is None or frame.empty:
            return pd.Series(default, index=df.index)

        frame2 = frame.copy()
        if not frame2.index.equals(df.index):
            frame2 = frame2.reindex(df.index)

        for col in possible_cols:
            if col in frame2.columns:
                s = frame2[col]
                if not s.isna().all():
                    return s
        return pd.Series(default, index=df.index)

    # =========================
    # ESTADO DE RESULTADOS
    # =========================
    df["Revenue"] = get_value(income_stmt, [
        "Total Revenue", "TotalRevenue", "Revenue", "Sales"
    ])

    df["Cost of Revenue"] = get_value(income_stmt, [
        "Cost Of Revenue", "CostOfRevenue", "Cost Of Goods Sold"
    ])

    df["Gross Profit"] = get_value(income_stmt, [
        "Gross Profit", "GrossProfit"
    ])

    df["Operating Income"] = get_value(income_stmt, [
        "Operating Income", "OperatingIncome", "Operating Profit"
    ])

    df["Net Income"] = get_value(income_stmt, [
        "Net Income", "NetIncome", "Net Income Common Stockholders"
    ])

    df["EBITDA"] = get_value(income_stmt, [
        "EBITDA", "Ebitda", "Normalized EBITDA"
    ])

    df["EBIT"] = get_value(income_stmt, [
        "EBIT", "Ebit", "Operating Income"
    ])

    # Si falta Gross Profit, lo calculamos
    if df["Gross Profit"].isna().all() and df["Revenue"].notna().any():
        df["Gross Profit"] = df["Revenue"] - df["Cost of Revenue"].fillna(0)

    # Si falta EBIT, usamos Operating Income
    if df["EBIT"].isna().all() and df["Operating Income"].notna().any():
        df["EBIT"] = df["Operating Income"]

    # =========================
    # BALANCE GENERAL
    # =========================
    df["Total Assets"] = get_value(balance_sheet, [
        "Total Assets", "TotalAssets"
    ])

    df["Current Assets"] = get_value(balance_sheet, [
        "Current Assets", "CurrentAssets"
    ])

    df["Cash"] = get_value(balance_sheet, [
        "Cash And Cash Equivalents", "Cash", "CashAndCashEquivalents",
        "Cash Cash Equivalents And Short Term Investments"
    ])

    df["Total Liabilities"] = get_value(balance_sheet, [
        "Total Liabilities Net Minority Interest", "Total Liabilities"
    ])

    df["Current Liabilities"] = get_value(balance_sheet, [
        "Current Liabilities", "CurrentLiabilities"
    ])

    df["Total Debt"] = get_value(balance_sheet, [
        "Total Debt", "TotalDebt", "Long Term Debt And Capital Lease Obligation"
    ])

    df["Long Term Debt"] = get_value(balance_sheet, [
        "Long Term Debt", "LongTermDebt"
    ])

    df["Shareholder Equity"] = get_value(balance_sheet, [
        "Total Equity Gross Minority Interest", "Stockholders Equity",
        "Total Stockholder Equity", "Common Stock Equity"
    ])

    # =========================
    # FLUJO DE CAJA
    # =========================
    df["Operating Cash Flow"] = get_value(cash_flow, [
        "Operating Cash Flow", "Total Cash From Operating Activities",
        "Cash Flow From Operating Activities"
    ])

    df["Investing Cash Flow"] = get_value(cash_flow, [
        "Investing Cash Flow", "Total Cash From Investing Activities",
        "Cash Flow From Investing Activities"
    ])

    df["Financing Cash Flow"] = get_value(cash_flow, [
        "Financing Cash Flow", "Total Cash From Financing Activities",
        "Cash Flow From Financing Activities"
    ])

    df["Free Cash Flow"] = get_value(cash_flow, [
        "Free Cash Flow", "FreeCashFlow"
    ])

    df["Capital Expenditure"] = get_value(cash_flow, [
        "Capital Expenditure", "CapitalExpenditure", "Capital Expenditures"
    ])

    # Si falta Free Cash Flow, lo calculamos
    if df["Free Cash Flow"].isna().all() and df["Operating Cash Flow"].notna().any():
        if df["Capital Expenditure"].notna().any():
            df["Free Cash Flow"] = df["Operating Cash Flow"] + df["Capital Expenditure"]
        else:
            df["Free Cash Flow"] = df["Operating Cash Flow"] * 0.7

    # =========================
    # DATOS DE MERCADO
    # =========================
    shares_outstanding = info.get("sharesOutstanding", np.nan)
    current_price = info.get("currentPrice", info.get("regularMarketPrice", np.nan))

    if not np.isnan(shares_outstanding) and not np.isnan(current_price):
        current_market_cap = shares_outstanding * current_price
        df["Market Cap"] = current_market_cap
    else:
        market_cap = info.get("marketCap", np.nan)
        df["Market Cap"] = market_cap

    # =========================
    # MÉTRICAS CALCULADAS
    # =========================
    # Márgenes
    df["Gross Margin %"] = (df["Gross Profit"] / df["Revenue"]) * 100
    df["Operating Margin %"] = (df["Operating Income"] / df["Revenue"]) * 100
    df["Net Profit Margin %"] = (df["Net Income"] / df["Revenue"]) * 100
    df["EBITDA Margin %"] = (df["EBITDA"] / df["Revenue"]) * 100

    # EPS
    if not np.isnan(shares_outstanding) and shares_outstanding > 0:
        df["EPS"] = df["Net Income"] / shares_outstanding
    else:
        df["EPS"] = np.nan

    # Retornos
    df["ROE %"] = (df["Net Income"] / df["Shareholder Equity"]) * 100
    df["ROA %"] = (df["Net Income"] / df["Total Assets"]) * 100

    # ROIC
    denominator = df["Shareholder Equity"].fillna(0) + df["Total Debt"].fillna(0)
    df["ROIC %"] = np.where(denominator != 0, (df["EBIT"] / denominator) * 100, np.nan)

    # Liquidez
    df["Current Ratio"] = df["Current Assets"] / df["Current Liabilities"]
    df["Quick Ratio"] = (df["Current Assets"] - df["Current Assets"] * 0.3) / df["Current Liabilities"]
    df["Cash Ratio"] = df["Cash"] / df["Current Liabilities"]

    # Endeudamiento
    df["Debt to Equity"] = df["Total Debt"] / df["Shareholder Equity"]
    df["Debt to Assets"] = df["Total Debt"] / df["Total Assets"]

    # Valoración
    df["P/E Ratio"] = df["Market Cap"] / df["Net Income"]
    df["P/B Ratio"] = df["Market Cap"] / df["Shareholder Equity"]
    df["EV/EBITDA"] = (df["Market Cap"] + df["Total Debt"].fillna(0) - df["Cash"].fillna(0)) / df["EBITDA"]

    # Crecimientos
    df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
    df["Net Income Growth %"] = df["Net Income"].pct_change() * 100
    df["EPS Growth %"] = df["EPS"].pct_change() * 100
    df["Operating Cash Flow Growth %"] = df["Operating Cash Flow"].pct_change() * 100

    # Limpiar infinitos
    df = df.replace([np.inf, -np.inf], np.nan)

    # Alias de columnas para que encajen con el resto de la app
    if "Net Income" in df.columns:
        df["NetIncome"] = df["Net Income"]
    if "Gross Profit" in df.columns:
        df["GrossProfit"] = df["Gross Profit"]
    if "Gross Margin %" in df.columns:
        df["Gross Margin"] = df["Gross Margin %"]
    if "Net Profit Margin %" in df.columns:
        df["Net Profit Margin"] = df["Net Profit Margin %"]
    if "ROE %" in df.columns:
        df["ROE"] = df["ROE %"]
    if "ROA %" in df.columns:
        df["ROA"] = df["ROA %"]

    # Evitar que 'Date' sea a la vez índice y columna
    df = df.reset_index(drop=True)

    return df, info, company_name, use_quarterly

# ======================================================================
# FUNCIONES AUXILIARES: YFINANCE + ML (TRIMESTRES)
# ======================================================================

@st.cache_data
def yf_get_price_history(ticker: str, period="5y", interval="1mo") -> pd.DataFrame:
    data = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
    data.reset_index(inplace=True)
    return data


@st.cache_data
def yf_get_basic_info(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    info = t.info
    return info if isinstance(info, dict) else {}


def forecast_next_quarters(df_fin: pd.DataFrame, col='Revenue', n_quarters=4):
    """
    Modelo simple de regresión lineal para predecir n_quarters siguientes.
    df_fin debe tener columnas ['Date', col].
    """
    if df_fin is None or df_fin.empty or col not in df_fin.columns:
        return None

    df = df_fin[['Date', col]].dropna().copy()
    if df.empty or len(df) < 4:
        return None

    df = df.sort_values('Date')
    df['t'] = np.arange(len(df))

    X = df[['t']]
    y = df[col]

    model = LinearRegression()
    model.fit(X, y)

    last_t = df['t'].iloc[-1]
    future_ts = np.arange(last_t + 1, last_t + 1 + n_quarters).reshape(-1, 1)
    preds = model.predict(future_ts)

    last_date = df['Date'].iloc[-1]
    future_dates = pd.date_range(
        start=last_date + pd.offsets.QuarterEnd(1),
        periods=n_quarters,
        freq='Q'
    )

    forecast_df = pd.DataFrame({
        'Date': future_dates,
        f'{col}_pred': preds
    })
    return forecast_df


def forecast_next_quarters_models(df_fin: pd.DataFrame, col='Revenue', n_quarters=4, model_names=None):
    """
    Predicciones trimestrales para yfinance con varios modelos.
    df_fin: columnas ['Date', col]
    Retorna: dict {nombre_modelo: DataFrame ['Date', f'{col}_pred']}
    """
    if model_names is None:
        model_names = []

    if df_fin is None or df_fin.empty or col not in df_fin.columns:
        return {}

    df = df_fin[['Date', col]].dropna().copy()
    if df.empty or len(df) < 4:
        return {}

    df = df.sort_values('Date')
    df['t'] = np.arange(len(df))

    X = df[['t']]
    y = df[col]

    last_t = df['t'].iloc[-1]
    future_ts = np.arange(last_t + 1, last_t + 1 + n_quarters).reshape(-1, 1)

    last_date = df['Date'].iloc[-1]
    future_dates = pd.date_range(
        start=last_date + pd.offsets.QuarterEnd(1),
        periods=n_quarters,
        freq='Q'
    )

    results = {}

    for name in model_names:
        if name == "Regresión lineal":
            model = LinearRegression()
        elif name == "Polinómica (grado 2)":
            model = Pipeline([
                ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                ("linreg", LinearRegression())
            ])
        elif name == "Random Forest":
            model = RandomForestRegressor(
                n_estimators=200,
                random_state=42
            )
        else:
            continue

        model.fit(X, y)
        preds = model.predict(future_ts)

        forecast_df = pd.DataFrame({
            'Date': future_dates,
            f'{col}_pred': preds
        })
        results[name] = forecast_df

    return results


def detectar_anomalias(df_fin: pd.DataFrame, col='Revenue'):
    """
    Usa IsolationForest para marcar trimestres anómalos en una métrica dada.
    Añade columna 'Anomaly': -1 = anómalo, 1 = normal.
    """
    if df_fin is None or df_fin.empty or col not in df_fin.columns:
        return None

    df = df_fin[['Date', col]].dropna().copy()
    if len(df) < 8:
        df['Anomaly'] = 1
        return df

    modelo = IsolationForest(contamination=0.15, random_state=42)
    df['Anomaly'] = modelo.fit_predict(df[[col]])
    return df

# ======================================================================
# FUNCIONES AUXILIARES: FEATURES + CLUSTER (YFINANCE)
# ======================================================================

def construir_features_tickers(tickers):
    """
    Construye un DataFrame con features básicos para cada ticker (para clustering).
    """
    rows = []
    for tk in tickers:
        info = yf_get_basic_info(tk)
        if not info:
            continue
        row = {
            'Ticker': tk,
            'MarketCap': info.get('marketCap', np.nan),
            'Beta': info.get('beta', np.nan),
            'PE': info.get('trailingPE', np.nan),
            'ProfitMargin': info.get('profitMargins', np.nan),
            'DividendYield': info.get('dividendYield', np.nan)
        }
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def cluster_tickers(feature_df: pd.DataFrame, n_clusters=3):
    """
    Aplica KMeans a un DataFrame de features numéricos por ticker.
    """
    if feature_df.empty:
        return feature_df, None

    numeric_cols = ['MarketCap', 'Beta', 'PE', 'ProfitMargin', 'DividendYield']
    numeric_cols = [c for c in numeric_cols if c in feature_df.columns]

    df = feature_df.dropna(subset=numeric_cols).copy()
    if df.empty or len(df) < n_clusters:
        feature_df['Cluster'] = np.nan
        return feature_df, None

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[numeric_cols])

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)

    df['Cluster'] = labels
    # merge de vuelta
    feature_df = feature_df.merge(df[['Ticker', 'Cluster']], on='Ticker', how='left')
    return feature_df, km

# ======================================================================
# FUNCIONES AUXILIARES: PREDICCIONES CSV (AÑOS) CON MÚLTIPLES MODELOS
# ======================================================================

def forecast_next_periods_csv_models(df_hist: pd.DataFrame, value_col='Revenue', n_periods=3, model_names=None):
    """
    Predicciones para datos del CSV (por año) usando varios modelos.
    df_hist: DataFrame con columnas ['Year', value_col]
    Retorna: dict {nombre_modelo: DataFrame ['Year', f'{value_col}_pred']}
    """
    if model_names is None:
        model_names = []

    if df_hist is None or df_hist.empty:
        return {}

    if 'Year' not in df_hist.columns or value_col not in df_hist.columns:
        return {}

    df = df_hist[['Year', value_col]].dropna().copy()
    if df.empty or len(df) < 3:
        return {}

    df = df.sort_values('Year')

    X = df[['Year']]
    y = df[value_col]

    last_year = int(df['Year'].max())
    future_years = np.arange(last_year + 1, last_year + 1 + n_periods).reshape(-1, 1)

    results = {}

    for name in model_names:
        if name == "Regresión lineal":
            model = LinearRegression()
        elif name == "Polinómica (grado 2)":
            model = Pipeline([
                ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                ("linreg", LinearRegression())
            ])
        elif name == "Random Forest":
            model = RandomForestRegressor(
                n_estimators=200,
                random_state=42
            )
        else:
            continue  # modelo desconocido

        model.fit(X, y)
        preds = model.predict(future_years)

        forecast_df = pd.DataFrame({
            'Year': future_years.flatten().astype(int),
            f'{value_col}_pred': preds
        })
        results[name] = forecast_df

    return results

# ======================================================================
# FUNCIONES EXTRA: EVALUACIÓN (BACKTESTING) Y TEXTO AUTOMÁTICO
# ======================================================================

def evaluar_modelos_csv(df_hist, value_col, model_names):
    """Backtest simple: entrenar en todos menos los 2 últimos años, probar en los 2 últimos."""
    if df_hist is None or df_hist.empty or 'Year' not in df_hist.columns or value_col not in df_hist.columns:
        return None

    df = df_hist[['Year', value_col]].dropna().copy().sort_values('Year')
    if len(df) < 6:
        return None

    X = df[['Year']].values
    y = df[value_col].values

    # últimos 2 años de test
    train_end = len(df) - 2
    X_train, X_test = X[:train_end], X[train_end:]
    y_train, y_test = y[:train_end], y[train_end:]

    rows = []
    for name in model_names:
        if name == "Regresión lineal":
            model = LinearRegression()
        elif name == "Polinómica (grado 2)":
            model = Pipeline([
                ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                ("linreg", LinearRegression())
            ])
        elif name == "Random Forest":
            model = RandomForestRegressor(n_estimators=200, random_state=42)
        else:
            continue

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        try:
            mape = mean_absolute_percentage_error(y_test, y_pred)
        except ValueError:
            mape = np.nan

        rows.append({
            "Modelo": name,
            "MAE": mae,
            "MAPE": mape
        })

    if not rows:
        return None
    return pd.DataFrame(rows)


def evaluar_modelos_yf(df_fin, col, model_names):
    """Backtest para series trimestrales de yfinance."""
    if df_fin is None or df_fin.empty or col not in df_fin.columns:
        return None

    df = df_fin[['Date', col]].dropna().copy().sort_values('Date')
    if len(df) < 8:
        return None

    df['t'] = np.arange(len(df))
    X = df[['t']].values
    y = df[col].values

    # últimos 4 trimestres como test
    train_end = len(df) - 4
    X_train, X_test = X[:train_end], X[train_end:]
    y_train, y_test = y[:train_end], y[train_end:]

    rows = []
    for name in model_names:
        if name == "Regresión lineal":
            model = LinearRegression()
        elif name == "Polinómica (grado 2)":
            model = Pipeline([
                ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                ("linreg", LinearRegression())
            ])
        elif name == "Random Forest":
            model = RandomForestRegressor(n_estimators=200, random_state=42)
        else:
            continue

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        try:
            mape = mean_absolute_percentage_error(y_test, y_pred)
        except ValueError:
            mape = np.nan

        rows.append({
            "Modelo": name,
            "MAE": mae,
            "MAPE": mape
        })

    if not rows:
        return None
    return pd.DataFrame(rows)


def texto_resumen_modelos(df_errores, contexto):
    """Genera texto corto explicando qué modelo fue mejor según MAE."""
    if df_errores is None or df_errores.empty:
        return "No hay suficientes datos históricos para evaluar el desempeño de los modelos."

    best = df_errores.sort_values("MAE").iloc[0]
    modelo = best["Modelo"]
    mae = best["MAE"]

    comentario_extra = ""
    if "Polinómica" in modelo:
        comentario_extra = " Suele ajustarse bien al histórico, pero puede exagerar hacia el futuro."
    elif "Regresión lineal" in modelo:
        comentario_extra = " Tiende a producir tendencias más suaves y estables."
    elif "Random Forest" in modelo:
        comentario_extra = " Captura relaciones no lineales, pero puede comportarse distinto al extrapolar."

    return (
        f"En {contexto}, el modelo con menor error histórico (MAE) es "
        f"{modelo} (≈ {mae:,.2f}).{comentario_extra}"
    )


def evaluar_tendencia_simple(df, x_col, y_col):
    """Devuelve texto sobre la tendencia general (creciente, decreciente, volátil)."""
    dfc = df[[x_col, y_col]].dropna().copy().sort_values(x_col)
    if len(dfc) < 3:
        return "No hay suficientes datos históricos para evaluar la tendencia."

    y = dfc[y_col].to_numpy(dtype=float)

    # Si el eje X son fechas, usamos índices numéricos
    if np.issubdtype(dfc[x_col].dtype, np.datetime64):
        x = np.arange(len(dfc), dtype=float)
    else:
        x = dfc[x_col].to_numpy(dtype=float)

    # pendiente simple con regresión lineal
    X_mat = np.vstack([x, np.ones_like(x)]).T
    m, _ = np.linalg.lstsq(X_mat, y, rcond=None)[0]

    delta = y[-1] - y[0]

    if m > 0 and delta > 0:
        return "La tendencia general es creciente, con niveles más altos en los periodos recientes."
    elif m < 0 and delta < 0:
        return "La tendencia general es decreciente, con niveles más bajos en los periodos recientes."
    else:
        return "La serie muestra un comportamiento volátil, sin una tendencia clara y consistente."


def evaluar_salud_financiera(net_margin, roe, roa):
    """Devuelve texto tipo semáforo según valores de margen neto, ROE y ROA."""
    def badge(valor, bueno, medio):
        if pd.isna(valor):
            return "Sin datos"
        if valor >= bueno:
            return "Fuerte"
        elif valor >= medio:
            return "Aceptable"
        else:
            return "Débil"

    nm_badge = badge(net_margin, bueno=15, medio=5)
    roe_badge = badge(roe, bueno=15, medio=8)
    roa_badge = badge(roa, bueno=8, medio=3)

    return {
        "Margen Neto": (nm_badge, net_margin),
        "ROE": (roe_badge, roe),
        "ROA": (roa_badge, roa)
    }

# INTERFAZ STREAMLIT

st.set_page_config(
    page_title="Dashboard de Análisis Financiero",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Dashboard de Exploración Financiera")

# --- SIDEBAR: CONFIGURACIÓN GENERAL ---
st.sidebar.title("Configuración de Análisis")

# CAMBIO IMPORTANTE: opciones cortas y fáciles de comparar
modo_fuente = st.sidebar.radio(
    "Fuente de datos",
    ("CSV", "yfinance"),
    index=0
)
st.sidebar.caption("CSV: usa tu archivo histórico. yfinance: descarga datos reales de Yahoo Finance.")

# --- CARGA INICIAL CSV ---
df_base = load_and_clean_data(FINANCIAL_FILE_PATH)

# Variables de control
empresas_seleccionadas = []
datos_empresas = {}
datos_globales = None

# Datos para yfinance
yf_tickers = []
yf_ticker_actual = None
yf_df_fin = None
yf_df_price = None
yf_info = None
yf_company_name = None
yf_use_quarterly = None

# BLOQUE CSV

if modo_fuente == "CSV":
    if df_base is None:
        st.error(f"No se pudo cargar el archivo '{FINANCIAL_FILE_PATH}'. Verifica que esté en la misma carpeta.")
        st.stop()

    company_list = sorted(df_base['Company'].unique().tolist())

    empresas_seleccionadas = st.sidebar.multiselect(
        "Selecciona hasta 2 compañías (CSV):",
        options=company_list,
        default=company_list[:1] if company_list else [],
        max_selections=2
    )
    st.sidebar.caption("Selecciona 1 para análisis individual, 2 para comparación.")

    datos_empresas = procesar_datos_financieros(df_base, empresas_seleccionadas)
    datos_globales = obtener_datos_para_global(df_base)


# BLOQUE YFINANCE
else:  # modo_fuente == "yfinance"
    tickers_input = st.sidebar.text_input(
        "Tickers (separados por coma):",
        value="AAPL, MSFT, TSLA"
    )
    st.sidebar.caption("Ejemplo: AAPL, MSFT, TSLA")

    yf_tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    if yf_tickers:
        yf_ticker_actual = st.sidebar.selectbox("Ticker principal a analizar:", options=yf_tickers)
        period_yf = st.sidebar.selectbox("Periodo de precios:", ["1y", "5y", "10y", "max"], index=1)
        interval_yf = st.sidebar.selectbox("Intervalo:", ["1d", "1wk", "1mo"], index=2)
        st.sidebar.caption("Intervalos más largos suavizan la serie, pero pierdes detalle diario.")

        try:
            yf_df_fin, yf_info, yf_company_name, yf_use_quarterly = yf_get_full_financials(yf_ticker_actual)
            yf_df_price = yf_get_price_history(yf_ticker_actual, period=period_yf, interval=interval_yf)
        except Exception as e:
            st.sidebar.error(f"Error al descargar datos de {yf_ticker_actual}: {e}")
    else:
        st.sidebar.warning("Introduce al menos un ticker para usar yfinance.")

st.markdown("Explora estados financieros históricos (CSV) o datos en vivo con yfinance, con modelos predictivos y análisis automático.")

# --- ESTRUCTURA PRINCIPAL DE PESTAÑAS ---
tab_guia, tab_stats, tab_analisis, tab_comparacion, tab_ml, tab_tecnico = st.tabs([
    "Guía de uso",
    "Estadísticas / Distribución",
    "Análisis Individual",
    "Comparación",
    "Predicciones y ML",
    "Detalles técnicos"
])


# PESTAÑA 0: GUÍA DE USO


with tab_guia:
    st.header("Guía de uso del dashboard")

    st.markdown("""
Este dashboard está pensado para explorar, comparar y proyectar el desempeño financiero de empresas, usando:

- Datos de un archivo CSV (histórico por año).
- Datos en vivo desde yfinance (histórico por periodo y precio de la acción).
- Modelos de Machine Learning sencillos para hacer predicciones y explorar escenarios.

Estructura de pestañas

1. Estadísticas / Distribución  
   Resume el comportamiento global de las variables financieras.

2. Análisis Individual  
   Muestra el perfil detallado de una empresa o ticker:
   - KPIs clave (Revenue, Net Income, ROE, márgenes).
   - Evolución histórica.
   - Salud financiera tipo semáforo.

3. Comparación  
   Compara:
   - Dos compañías del CSV (métricas financieras).
   - Varios tickers de bolsa (evolución del precio).

4. Predicciones y ML  
   Laboratorio de modelos:
   - En CSV: predicciones por año (Revenue y Net Income).
   - En yfinance: predicciones por periodo de la métrica elegida.

5. Detalles técnicos  
   Resume la arquitectura, librerías usadas y modelos de ML que hay detrás del dashboard.
""")


# PESTAÑA 1: ESTADÍSTICAS Y DISTRIBUCIÓN


with tab_stats:
    st.header("Estadística descriptiva y distribución de variables")

    if modo_fuente == "CSV":
        if datos_globales is None or datos_globales.get('df_full', pd.DataFrame()).empty:
            st.warning("No se pudieron procesar los datos globales del CSV.")
        else:
            df_global = datos_globales['df_full'].copy()

            st.markdown("Estadística descriptiva de variables numéricas")

            numerical_cols_stats = df_global.select_dtypes(include=np.number).columns.tolist()
            cols_to_describe = [col for col in numerical_cols_stats if col not in ['Year']]

            stats_df = df_global[cols_to_describe].describe().T[['count', 'mean', 'std', 'min', 'max']].reset_index()
            stats_df.columns = ['Variable', 'Conteo', 'Media', 'Desviación Estándar', 'Mínimo', 'Máximo']

            def format_stat(val):
                if isinstance(val, (int, float)):
                    if abs(val) > 1000:
                        return f"{val:,.0f}"
                    else:
                        return f"{val:.2f}"
                return val

            styled_stats = stats_df.style.format(formatter={
                'Conteo': "{:,.0f}",
                'Media': format_stat,
                'Desviación Estándar': format_stat,
                'Mínimo': format_stat,
                'Máximo': format_stat
            })

            st.dataframe(styled_stats, use_container_width=True, hide_index=True)

            st.write("---")
            st.markdown("Distribución de variables clave")

            numerical_cols_chart = ['Revenue', 'Net Income', 'Gross Profit', 'Net Profit Margin', 'ROE', 'ROA', 'PE Ratio']
            cols_present = [c for c in numerical_cols_chart if c in df_global.columns]
            if cols_present:
                df_chart = df_global[cols_present].copy()
                df_chart = df_chart.clip(lower=df_chart.quantile(0.01), upper=df_chart.quantile(0.99), axis=1)

                col_hist1, col_hist2 = st.columns(2)

                with col_hist1:
                    var_dist1 = st.selectbox("Histograma 1:", df_chart.columns.tolist(), index=0)
                    fig_hist1, ax_hist1 = plt.subplots(figsize=(8, 4))
                    sns.histplot(df_chart[var_dist1].dropna(), bins=30, kde=True, color=COLOR_PRIMARY, ax=ax_hist1)
                    ax_hist1.set_title(f'Distribución de {var_dist1}', fontsize=12)
                    st.pyplot(fig_hist1)

                with col_hist2:
                    idx2 = 1 if len(df_chart.columns) > 1 else 0
                    var_dist2 = st.selectbox("Histograma 2:", df_chart.columns.tolist(), index=idx2)
                    fig_hist2, ax_hist2 = plt.subplots(figsize=(8, 4))
                    sns.histplot(df_chart[var_dist2].dropna(), bins=30, kde=True, color=COLOR_SECONDARY, ax=ax_hist2)
                    ax_hist2.set_title(f'Distribución de {var_dist2}', fontsize=12)
                    st.pyplot(fig_hist2)

    else:  # yfinance
        if yf_df_price is None or yf_df_price.empty or yf_ticker_actual is None:
            st.info("Configura un ticker en el sidebar para ver estadísticas con yfinance.")
        else:
            st.subheader(f"Estadísticas del precio de {yf_ticker_actual}")

            desc = yf_df_price[['Close']].describe().T
            st.dataframe(desc, use_container_width=True)

            st.write("---")
            st.markdown("Histograma del precio de cierre")

            fig_p, ax_p = plt.subplots(figsize=(8, 4))
            sns.histplot(yf_df_price['Close'].dropna(), bins=30, kde=True, color=COLOR_PRIMARY, ax=ax_p)
            ax_p.set_title(f"Distribución del precio de cierre - {yf_ticker_actual}")
            st.pyplot(fig_p)


# PESTAÑA 2: ANÁLISIS INDIVIDUAL


with tab_analisis:
    st.header("Análisis detallado y evolución")

    if modo_fuente == "CSV":
        if not empresas_seleccionadas:
            st.info("Selecciona al menos una compañía en la barra lateral.")
        elif datos_empresas:
            empresa_actual = empresas_seleccionadas[0]
            data = datos_empresas.get(empresa_actual)

            if data:
                st.subheader(f"Reporte clave: {data['empresa']} - Año {data['año']}")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Revenue", format_currency(data['Revenue'], 0))
                with col2:
                    st.metric("Net Income", format_currency(data['Net Income'], 0))
                with col3:
                    st.metric("Margen Neto", format_percentage(data['Net Margin']))
                with col4:
                    st.metric("ROE", format_percentage(data['ROE']))

                # Salud financiera tipo semáforo
                st.markdown("Salud financiera (semáforo)")
                health = evaluar_salud_financiera(data['Net Margin'], data['ROE'], data['ROA'])
                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    badge, val = health["Margen Neto"]
                    st.markdown(f"**Margen Neto**: {badge}<br/>Valor: {format_percentage(val)}", unsafe_allow_html=True)
                with col_h2:
                    badge, val = health["ROE"]
                    st.markdown(f"**ROE**: {badge}<br/>Valor: {format_percentage(val)}", unsafe_allow_html=True)
                with col_h3:
                    badge, val = health["ROA"]
                    st.markdown(f"**ROA**: {badge}<br/>Valor: {format_percentage(val)}", unsafe_allow_html=True)

                # Comparación contra mediana del dataset
                if datos_globales is not None and datos_globales.get('df_full', None) is not None:
                    st.markdown("Comparación contra la mediana del dataset (CSV)")
                    gm = datos_globales
                    comp_rows = [
                        ("Revenue", data['Revenue'], gm['Revenue_Median']),
                        ("Net Income", data['Net Income'], gm['Net_Income_Median']),
                        ("Gross Margin", data['Gross Margin'], gm['Gross_Margin_Median']),
                        ("Net Profit Margin", data['Net Margin'], gm['Net_Margin_Median']),
                        ("ROE", data['ROE'], gm['ROE_Median']),
                        ("ROA", data['ROA'], gm['ROA_Median']),
                    ]
                    comp_df = pd.DataFrame(comp_rows, columns=["Métrica", "Empresa", "Mediana dataset"])
                    st.dataframe(comp_df, use_container_width=True)

                st.markdown("Explicación de métricas")
                metric_to_explain = st.selectbox(
                    "Selecciona una métrica para ver qué significa:",
                    list(METRIC_DEFS.keys())
                )
                st.info(METRIC_DEFS.get(metric_to_explain, "Sin definición disponible."))

                st.write("---")
                st.markdown("Evolución de ingresos y ganancias (histórico)")

                df_hist = data['historial_df'].copy()

                fig, ax = plt.subplots(figsize=(10, 5))
                if 'Revenue' in df_hist.columns:
                    ax.plot(df_hist['Year'], df_hist['Revenue'], marker='o', label='Revenue', color=COLOR_HIST)
                    ax.set_ylabel('Revenue', color=COLOR_HIST)
                    ax.tick_params(axis='y', labelcolor=COLOR_HIST)

                ax2 = ax.twinx()
                if 'Net Income' in df_hist.columns:
                    ax2.plot(df_hist['Year'], df_hist['Net Income'], marker='s', label='Net Income', color=COLOR_SECONDARY)
                    ax2.set_ylabel('Net Income', color=COLOR_SECONDARY)
                    ax2.tick_params(axis='y', labelcolor=COLOR_SECONDARY)

                ax.set_title(f"Tendencia financiera de {data['empresa']}")
                ax.set_xlabel('Año')
                ax.grid(True, linestyle='--', alpha=0.6)

                lines, labels = ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc='upper left')

                st.pyplot(fig)

                # Conclusión automática simple
                st.markdown("Conclusión automática sobre la tendencia")
                if 'Revenue' in df_hist.columns:
                    txt_rev = evaluar_tendencia_simple(df_hist, 'Year', 'Revenue')
                    st.markdown(f"- Revenue: {txt_rev}")
                if 'Net Income' in df_hist.columns:
                    txt_ni = evaluar_tendencia_simple(df_hist, 'Year', 'Net Income')
                    st.markdown(f"- Net Income: {txt_ni}")

    else:  # yfinance
        if yf_ticker_actual is None or yf_df_price is None or yf_df_price.empty:
            st.info("Selecciona un ticker y un periodo en la barra lateral.")
        else:
            st.subheader(f"Análisis para {yf_ticker_actual}")

            col1, col2, col3 = st.columns(3)
            nombre = yf_company_name or (yf_info.get('longName', yf_ticker_actual) if yf_info else yf_ticker_actual)
            sector = yf_info.get('sector', 'N/A') if yf_info else 'N/A'
            precio_act = yf_info.get('currentPrice', np.nan) if yf_info else np.nan
            market_cap = yf_info.get('marketCap', np.nan) if yf_info else np.nan

            with col1:
                st.metric("Nombre", nombre)
            with col2:
                st.metric("Sector", sector)
            with col3:
                st.metric("Precio actual", f"{precio_act}" if not pd.isna(precio_act) else "N/A")

            st.write(f"Market Cap: {format_currency(market_cap, 0) if not pd.isna(market_cap) else 'N/A'}")

            st.markdown("Explicación de métricas")
            metric_to_explain = st.selectbox(
                "Selecciona una métrica para ver qué significa:",
                list(METRIC_DEFS.keys()),
                key="metric_explainer_yf"
            )
            st.info(METRIC_DEFS.get(metric_to_explain, "Sin definición disponible."))

            st.write("---")
            st.markdown("Evolución de precio")

            fig_p, ax_p = plt.subplots(figsize=(10, 4))
            ax_p.plot(yf_df_price['Date'], yf_df_price['Close'], color=COLOR_PRIMARY)
            ax_p.set_title(f"Precio de cierre - {yf_ticker_actual}")
            ax_p.set_xlabel("Fecha")
            ax_p.set_ylabel("Precio de cierre")
            ax_p.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig_p)

            # Conclusión automática simple para el precio
            st.markdown("Conclusión automática sobre la tendencia de precio")
            txt_price = evaluar_tendencia_simple(yf_df_price, 'Date', 'Close')
            st.markdown(f"- Precio de la acción: {txt_price}")

            st.write("---")
            st.markdown("Estados financieros (yfinance)")

            if yf_df_fin is None or yf_df_fin.empty:
                st.info("No se encontraron estados financieros disponibles para este ticker.")
            else:
                st.dataframe(yf_df_fin, use_container_width=True)


# PESTAÑA 3: COMPARACIÓN


with tab_comparacion:
    st.header("Comparación de compañías o tickers")

    if modo_fuente == "CSV":
        if len(empresas_seleccionadas) < 2 or not datos_empresas:
            st.info("Selecciona dos compañías en la barra lateral para comparar en modo CSV.")
        else:
            comp1, comp2 = empresas_seleccionadas[0], empresas_seleccionadas[1]
            data1 = datos_empresas.get(comp1)
            data2 = datos_empresas.get(comp2)

            if data1 and data2:
                st.subheader(f"Comparativa: {comp1} vs {comp2}")

                st.markdown("Métricas del último año reportado")

                comparison_metrics = {
                    'Métrica': ['Revenue', 'Net Income', 'Margen Neto (%)', 'ROE (%)', 'ROA (%)', 'P/E Ratio'],
                    comp1: [data1['Revenue'], data1['Net Income'], data1['Net Margin'], data1['ROE'], data1['ROA'], data1['PE Ratio']],
                    comp2: [data2['Revenue'], data2['Net Income'], data2['Net Margin'], data2['ROE'], data2['ROA'], data2['PE Ratio']]
                }

                df_comp = pd.DataFrame(comparison_metrics)

                def format_metric_comp(row, col_name):
                    value = row[col_name]
                    if 'Margen' in row['Métrica'] or '%' in row['Métrica']:
                        return format_percentage(value)
                    elif 'P/E' in row['Métrica']:
                        return f"{value:.1f}x" if value != 0 else '-'
                    else:
                        return format_currency(value, 1)

                df_comp[comp1] = df_comp.apply(lambda row: format_metric_comp(row, comp1), axis=1)
                df_comp[comp2] = df_comp.apply(lambda row: format_metric_comp(row, comp2), axis=1)

                st.dataframe(df_comp.set_index('Métrica'), use_container_width=True)

                st.write("---")
                st.markdown("Evolución del Revenue")

                df_combined_hist = pd.concat([
                    data1['historial_df'][['Year', 'Revenue', 'Company']],
                    data2['historial_df'][['Year', 'Revenue', 'Company']]
                ])

                fig_rev, ax_rev = plt.subplots(figsize=(10, 5))
                sns.lineplot(data=df_combined_hist, x='Year', y='Revenue', hue='Company', marker='o',
                             palette=[COLOR_PRIMARY, COLOR_SECONDARY], ax=ax_rev)
                ax_rev.set_title("Evolución de ingresos (Revenue)")
                ax_rev.set_ylabel("Revenue")
                ax_rev.set_xlabel("Año")
                ax_rev.grid(True, linestyle='--', alpha=0.6)
                st.pyplot(fig_rev)

    else:  # yfinance
        if not yf_tickers:
            st.info("Introduce al menos dos tickers en el sidebar para comparar.")
        elif len(yf_tickers) < 2:
            st.info("Introduce al menos dos tickers para comparación con yfinance.")
        else:
            st.subheader("Comparación de precio entre tickers (yfinance)")

            period_comp = st.selectbox("Periodo para comparación de precios:", ["1y", "5y", "10y", "max"], index=0)
            interval_comp = st.selectbox("Intervalo:", ["1d", "1wk", "1mo"], index=2, key="interval_comp")

            price_dfs = []
            for tk in yf_tickers:
                try:
                    df_tk = yf_get_price_history(tk, period=period_comp, interval=interval_comp)
                    if not df_tk.empty:
                        df_tk = df_tk[['Date', 'Close']].copy()
                        df_tk['Ticker'] = tk
                        price_dfs.append(df_tk)
                except Exception:
                    continue

            if not price_dfs:
                st.warning("No se pudieron descargar datos de precio para los tickers.")
            else:
                df_prices_all = pd.concat(price_dfs, ignore_index=True)
                df_prices_all = df_prices_all[['Date', 'Close', 'Ticker']].copy()

                fig_c, ax_c = plt.subplots(figsize=(10, 5))
                for tk, df_tk in df_prices_all.groupby('Ticker'):
                    ax_c.plot(df_tk['Date'], df_tk['Close'], label=tk)
                ax_c.set_title("Evolución del precio de cierre por ticker")
                ax_c.set_xlabel("Fecha")
                ax_c.set_ylabel("Precio de cierre")
                ax_c.grid(True, linestyle='--', alpha=0.5)
                ax_c.legend()
                st.pyplot(fig_c)

# PESTAÑA 4: PREDICCIONES Y ML

with tab_ml:
    st.header("Predicciones y funcionalidades de ML")

    if modo_fuente == "CSV":
        st.subheader("Predicciones basadas en CSV (por año)")

        if not empresas_seleccionadas:
            st.info("Selecciona al menos una compañía en el sidebar para generar predicciones con el CSV.")
        elif not datos_empresas:
            st.warning("No se pudieron procesar los datos de las compañías seleccionadas.")
        else:
            empresa_csv = st.selectbox(
                "Empresa para predicción (CSV):",
                options=empresas_seleccionadas
            )

            data_csv = datos_empresas.get(empresa_csv)
            if not data_csv:
                st.warning("No se encontraron datos para la empresa seleccionada.")
            else:
                df_hist_csv = data_csv['historial_df'].copy()

                st.markdown(f"Histórico de {empresa_csv} (desde CSV):")
                st.dataframe(df_hist_csv, use_container_width=True)

                # Parámetros de predicción
                st.markdown("Parámetros de predicción (CSV)")
                n_years = st.slider("Años a predecir:", min_value=1, max_value=10, value=3)

                modelos_disponibles = ["Regresión lineal", "Polinómica (grado 2)", "Random Forest"]
                modelos_seleccionados = st.multiselect(
                    "Modelos a utilizar:",
                    modelos_disponibles,
                    default=["Regresión lineal", "Polinómica (grado 2)"]
                )

                if not modelos_seleccionados:
                    st.info("Selecciona al menos un modelo para generar predicciones.")
                else:
                    col_csv1, col_csv2 = st.columns(2)

                    # Predicción de Revenue
                    with col_csv1:
                        if 'Revenue' in df_hist_csv.columns:
                            st.markdown("Forecast de Revenue")
                            results_rev = forecast_next_periods_csv_models(
                                df_hist_csv,
                                value_col='Revenue',
                                n_periods=n_years,
                                model_names=modelos_seleccionados
                            )

                            if not results_rev:
                                st.info("No hay suficientes datos de Revenue para generar predicciones.")
                            else:
                                merged_rev = None
                                for name, fdf in results_rev.items():
                                    temp = fdf.copy()
                                    temp = temp.rename(columns={f'Revenue_pred': f'Revenue_pred_{name}'})
                                    merged_rev = temp if merged_rev is None else merged_rev.merge(temp, on='Year', how='outer')

                                st.dataframe(merged_rev.sort_values('Year'), use_container_width=True)

                                fig_csv_rev, ax_csv_rev = plt.subplots(figsize=(8, 4))
                                ax_csv_rev.plot(df_hist_csv['Year'], df_hist_csv['Revenue'], marker='o', label='Histórico', color=COLOR_HIST)

                                for name, fdf in results_rev.items():
                                    ax_csv_rev.plot(
                                        fdf['Year'],
                                        fdf['Revenue_pred'],
                                        marker='o',
                                        linestyle='--',
                                        label=f'Predicción - {name}'
                                    )

                                ax_csv_rev.set_title(f"Revenue histórico y predicciones ({n_years} años)")
                                ax_csv_rev.set_xlabel("Año")
                                ax_csv_rev.set_ylabel("Revenue")
                                ax_csv_rev.grid(True, linestyle='--', alpha=0.6)
                                ax_csv_rev.legend()
                                st.pyplot(fig_csv_rev)

                                # Backtesting para Revenue
                                st.markdown("Desempeño histórico de los modelos (Revenue)")
                                errores_rev = evaluar_modelos_csv(df_hist_csv, "Revenue", modelos_seleccionados)
                                if errores_rev is not None:
                                    st.dataframe(errores_rev, use_container_width=True)
                                    st.markdown(texto_resumen_modelos(errores_rev, "Revenue (CSV)"))
                                else:
                                    st.info("No hay suficientes datos para evaluar el desempeño histórico en Revenue.")
                        else:
                            st.info("El CSV no tiene la columna 'Revenue' para esta empresa.")

                    # Predicción de Net Income
                    with col_csv2:
                        if 'Net Income' in df_hist_csv.columns:
                            st.markdown("Forecast de Net Income")
                            results_ni = forecast_next_periods_csv_models(
                                df_hist_csv,
                                value_col='Net Income',
                                n_periods=n_years,
                                model_names=modelos_seleccionados
                            )

                            if not results_ni:
                                st.info("No hay suficientes datos de Net Income para generar predicciones.")
                            else:
                                merged_ni = None
                                for name, fdf in results_ni.items():
                                    temp = fdf.copy()
                                    temp = temp.rename(columns={f'Net Income_pred': f'Net Income_pred_{name}'})
                                    merged_ni = temp if merged_ni is None else merged_ni.merge(temp, on='Year', how='outer')

                                st.dataframe(merged_ni.sort_values('Year'), use_container_width=True)

                                fig_csv_ni, ax_csv_ni = plt.subplots(figsize=(8, 4))
                                ax_csv_ni.plot(df_hist_csv['Year'], df_hist_csv['Net Income'], marker='o', label='Histórico', color=COLOR_HIST)

                                for name, fdf in results_ni.items():
                                    ax_csv_ni.plot(
                                        fdf['Year'],
                                        fdf['Net Income_pred'],
                                        marker='o',
                                        linestyle='--',
                                        label=f'Predicción - {name}'
                                    )

                                ax_csv_ni.set_title(f"Net Income histórico y predicciones ({n_years} años)")
                                ax_csv_ni.set_xlabel("Año")
                                ax_csv_ni.set_ylabel("Net Income")
                                ax_csv_ni.grid(True, linestyle='--', alpha=0.6)
                                ax_csv_ni.legend()
                                st.pyplot(fig_csv_ni)

                                # Backtesting para Net Income
                                st.markdown("Desempeño histórico de los modelos (Net Income)")
                                errores_ni = evaluar_modelos_csv(df_hist_csv, "Net Income", modelos_seleccionados)
                                if errores_ni is not None:
                                    st.dataframe(errores_ni, use_container_width=True)
                                    st.markdown(texto_resumen_modelos(errores_ni, "Net Income (CSV)"))
                                else:
                                    st.info("No hay suficientes datos para evaluar el desempeño histórico en Net Income.")
                        else:
                            st.info("El CSV no tiene la columna 'Net Income' para esta empresa.")

    else:  # yfinance
        if yf_ticker_actual is None or yf_df_fin is None or yf_df_fin.empty:
            st.info("Selecciona un ticker que tenga estados financieros para usar las predicciones.")
        else:
            st.subheader(f"Predicciones para {yf_ticker_actual} (periodos según disponibilidad)")

            st.markdown("Parámetros de predicción (yfinance)")
            # Métricas disponibles desde yfinance
            posibles_metricas = []
            for c in ['Revenue', 'NetIncome', 'GrossProfit']:
                if yf_df_fin is not None and c in yf_df_fin.columns:
                    posibles_metricas.append(c)

            for c in ['Operating Cash Flow', 'Free Cash Flow']:
                if yf_df_fin is not None and c in yf_df_fin.columns:
                    posibles_metricas.append(c)

            if not posibles_metricas:
                st.info("No hay métricas financieras disponibles para este ticker.")
            else:
                metric_yf = st.selectbox("Métrica a predecir:", posibles_metricas)
                n_quarters = st.slider("Periodos a predecir:", min_value=1, max_value=12, value=4)

                modelos_disponibles_yf = ["Regresión lineal", "Polinómica (grado 2)", "Random Forest"]
                modelos_yf = st.multiselect(
                    "Modelos a utilizar (yfinance):",
                    modelos_disponibles_yf,
                    default=["Regresión lineal", "Polinómica (grado 2)"]
                )

                if not modelos_yf:
                    st.info("Selecciona al menos un modelo para generar predicciones.")
                else:
                    st.markdown(f"Forecast de {metric_yf} (yfinance)")

                    results_yf = forecast_next_quarters_models(
                        yf_df_fin,
                        col=metric_yf,
                        n_quarters=n_quarters,
                        model_names=modelos_yf
                    )

                    if not results_yf:
                        st.info("No hay suficientes datos históricos para generar predicciones con yfinance.")
                    else:
                        # Tabla combinada
                        merged_yf = None
                        for name, fdf in results_yf.items():
                            temp = fdf.copy()
                            temp = temp.rename(columns={f'{metric_yf}_pred': f'{metric_yf}_pred_{name}'})
                            merged_yf = temp if merged_yf is None else merged_yf.merge(temp, on='Date', how='outer')

                        st.dataframe(merged_yf.sort_values('Date'), use_container_width=True)

                        # Gráfico
                        fig_yf, ax_yf = plt.subplots(figsize=(9, 4))
                        # histórico
                        df_hist_yf = yf_df_fin[['Date', metric_yf]].dropna().sort_values('Date')
                        ax_yf.plot(df_hist_yf['Date'], df_hist_yf[metric_yf], marker='o', label='Histórico', color=COLOR_HIST)

                        for name, fdf in results_yf.items():
                            ax_yf.plot(
                                fdf['Date'],
                                fdf[f'{metric_yf}_pred'],
                                marker='o',
                                linestyle='--',
                                label=f'Predicción - {name}'
                            )

                        ax_yf.set_title(f"{metric_yf} histórico y predicciones ({n_quarters} periodos)")
                        ax_yf.set_xlabel("Fecha")
                        ax_yf.set_ylabel(metric_yf)
                        ax_yf.grid(True, linestyle='--', alpha=0.6)
                        ax_yf.legend()
                        st.pyplot(fig_yf)

                        # Backtesting para la métrica elegida
                        st.markdown(f"Desempeño histórico de los modelos ({metric_yf})")
                        errores_yf = evaluar_modelos_yf(yf_df_fin, metric_yf, modelos_yf)
                        if errores_yf is not None:
                            st.dataframe(errores_yf, use_container_width=True)
                            st.markdown(texto_resumen_modelos(errores_yf, f"{metric_yf} (yfinance)"))
                        else:
                            st.info("No hay suficientes datos para evaluar el desempeño histórico en esta métrica.")

            st.write("---")
            st.subheader("Detección de anomalías en Revenue")

            if 'Revenue' in (yf_df_fin.columns if yf_df_fin is not None else []):
                df_anom = detectar_anomalias(yf_df_fin, col='Revenue')
                if df_anom is not None:
                    st.dataframe(df_anom, use_container_width=True)

                    fig_an, ax_an = plt.subplots(figsize=(8, 4))
                    ax_an.plot(df_anom['Date'], df_anom['Revenue'], label='Revenue', color=COLOR_PRIMARY)
                    anom_points = df_anom[df_anom['Anomaly'] == -1]
                    if not anom_points.empty:
                        ax_an.scatter(anom_points['Date'], anom_points['Revenue'], color='red', label='Anómalo')
                    ax_an.set_title("Anomalías en Revenue por periodo")
                    ax_an.legend()
                    st.pyplot(fig_an)
                else:
                    st.info("No se pudo calcular anomalías.")
            else:
                st.info("No hay columna 'Revenue' para analizar anomalías.")

            st.write("---")
            st.subheader("Clustering básico de tickers")

            if not yf_tickers or len(yf_tickers) < 2:
                st.info("Introduce al menos dos tickers en el sidebar para aplicar clustering.")
            else:
                features_df = construir_features_tickers(yf_tickers)
                if features_df.empty:
                    st.info("No se pudieron construir features suficientes para los tickers.")
                else:
                    n_clusters = st.slider("Número de clusters:", min_value=2, max_value=min(5, len(features_df)), value=3)
                    clustered_df, km_model = cluster_tickers(features_df, n_clusters=n_clusters)

                    st.markdown("Tickers con asignación de cluster:")
                    st.dataframe(clustered_df, use_container_width=True)

                    numeric_cols = ['MarketCap', 'PE']
                    numeric_cols = [c for c in numeric_cols if c in clustered_df.columns]

                    if len(numeric_cols) == 2 and 'Cluster' in clustered_df.columns:
                        st.markdown(f"Gráfico de clusters usando {numeric_cols[0]} en X y {numeric_cols[1]} en Y:")

                        df_plot = clustered_df.dropna(subset=[numeric_cols[0], numeric_cols[1], 'Cluster']).copy()

                        if df_plot.empty:
                            st.info("No hay suficientes datos válidos para graficar los clusters.")
                        else:
                            st.scatter_chart(
                                df_plot,
                                x=numeric_cols[0],
                                y=numeric_cols[1],
                                color='Cluster'
                            )
                    else:
                        st.info("No hay suficientes columnas numéricas para mostrar un scatter de clusters.")


# PESTAÑA 5: DETALLES TÉCNICOS


with tab_tecnico:
    st.header("Detalles técnicos del proyecto")

    st.markdown("""
Tecnologías utilizadas

- Python como lenguaje principal.
- Streamlit para la interfaz web interactiva.
- Pandas y NumPy para el manejo y transformación de datos.
- Matplotlib y Seaborn para gráficos.
- yfinance para descargar datos financieros reales desde Yahoo Finance.
- scikit-learn para modelos de Machine Learning:
  - Regresión lineal
  - Regresión polinómica (Pipeline con PolynomialFeatures + LinearRegression)
  - RandomForestRegressor
  - IsolationForest para detección de anomalías
  - KMeans para clustering de tickers
  - StandardScaler para normalización de features en el clustering

Arquitectura general

1. Carga de datos  
   - CSV: se lee un archivo local con estados financieros anuales.  
   - yfinance: se descargan automáticamente datos de:
     - Estados financieros (anuales o trimestrales).
     - Historial de precios.

2. Procesamiento y limpieza  
   - Estandarización de nombres de columna.
   - Cálculo de ratios financieros (Gross Margin, PE Ratio, etc.).
   - Cálculo de estadísticas globales (medianas por métrica).

3. Visualización  
   - Dashboards con:
     - Estadísticas descriptivas.
     - Evoluciones históricas (series temporales).
     - Comparaciones entre compañías y tickers.

4. Módulo de ML / IA  
   - Forecast de métricas (Revenue, Net Income, etc.) tanto para:
     - CSV (por año)
     - yfinance (por periodo)
   - Comparación entre modelos:
     - Se generan predicciones para varios años o trimestres.
     - Se realiza backtesting con una parte del histórico.
     - Se calculan métricas de error (MAE, MAPE).

5. Interpretabilidad  
   - Explicaciones textuales de cada métrica.
   - Semáforos de salud financiera.
   - Conclusiones automáticas sobre tendencia.
   - Resúmenes sobre qué modelo parece comportarse mejor.

Objetivo del proyecto

Este proyecto demuestra:

- Uso combinado de:
  - Fuentes de datos estáticas (CSV) y dinámicas (yfinance).
  - Técnicas clásicas de análisis financiero con herramientas de ciencia de datos.
- Integración de modelos de Machine Learning de forma visual, interpretada y con una evaluación cuantitativa mínima mediante backtesting.
""")
