"""Parser para CSVs proporcionados por ETESA (ej. tablas diarias de temperatura/lluvia)."""
from typing import Optional, Union
import pandas as pd


SPANISH_COL_MAP = {
    "Día": "day",
    "Temperaturas (°C) Máxima": "temp_max_c",
    "Temperaturas (°C) Mínima": "temp_min_c",
    "Temperaturas (°C) Promedio": "temp_avg_c",
    "Lluvia Diaria mm (litros/m²) Mes Actual": "rain_daily_mm",
    "Lluvia Diaria mm (litros/m²) Acum. Actual": "rain_accum_month_mm",
    "Lluvia Diaria mm (litros/m²) Promedio Histórico": "rain_daily_hist_mm",
    "Lluvia Diaria mm (litros/m²) Acum. Promedio Histórico": "rain_accum_hist_mm",
}


def _coerce_numeric(x):
    try:
        if pd.isna(x):
            return None
        # Remove common thousand separators and whitespace
        s = str(x).strip().replace(',', '')
        # Empty strings -> None
        if s == '':
            return None
        return float(s)
    except Exception:
        return None


def parse_etesa_csv(source: Union[str, pd.DataFrame], year: Optional[int] = None, month: Optional[int] = None, validate: bool = False) -> Optional[pd.DataFrame]:
    """Parses an ETESA CSV file (or DataFrame) and returns a cleaned DataFrame.

    - `source` can be a filepath or a pandas DataFrame already loaded.
    - If `year` and `month` are provided, a `date` column will be created from `day`.

    The parser will drop footer rows such as 'Promedio', 'Extremo', 'Total Mensual'.
    """
    if isinstance(source, pd.DataFrame):
        df = source.copy()
    else:
        try:
            df = pd.read_csv(source)
        except Exception:
            # Try with latin-1 encoding (common for Spanish CSVs)
            df = pd.read_csv(source, encoding='latin-1')

    # Normalize column names by exact match with map keys
    # If headers contain BOM or odd whitespace, strip names
    df.columns = [c.strip() for c in df.columns]

    # Drop fully empty columns
    df = df.loc[:, df.columns.notna()]

    # Map known Spanish headers to internal names
    mapped_cols = {}
    for c in df.columns:
        if c in SPANISH_COL_MAP:
            mapped_cols[c] = SPANISH_COL_MAP[c]

    df = df.rename(columns=mapped_cols)

    # If 'day' not present but first column is day-like, try to rename
    if 'day' not in df.columns and df.columns.size > 0:
        first_col = df.columns[0]
        if first_col.lower() in ('día', 'dia', 'd'):
            df = df.rename(columns={first_col: 'day'})

    # Remove footer rows: those where 'day' is non-numeric or equals known summary labels
    if 'day' in df.columns:
        def _is_data_row(v):
            try:
                # Accept integers (1..31)
                int(str(v))
                return True
            except Exception:
                return False

        df = df[df['day'].apply(_is_data_row)].copy()
        df['day'] = df['day'].astype(int)
    else:
        # If no day column, try to infer rows with numeric temperature values
        # Keep rows where at least one of the numeric columns is present
        numeric_cols = [c for c in ['temp_avg_c', 'temp_max_c', 'temp_min_c', 'rain_daily_mm'] if c in df.columns]
        if not numeric_cols:
            return None
        df = df[df[numeric_cols].notna().any(axis=1)].copy()

    # Coerce numeric columns
    for col in ['temp_max_c', 'temp_min_c', 'temp_avg_c', 'rain_daily_mm', 'rain_accum_month_mm', 'rain_daily_hist_mm', 'rain_accum_hist_mm']:
        if col in df.columns:
            df[col] = df[col].apply(_coerce_numeric)

    # If year and month provided, create a date column
    if year is not None and month is not None and 'day' in df.columns:
        df['date'] = pd.to_datetime(dict(year=year, month=month, day=df['day']), errors='coerce')

    # Optional validation: return (df, models) when validate=True
    if validate:
        try:
            from pipelines.etesa.models import EtesaRecord
        except Exception:
            EtesaRecord = None

        models = []
        if EtesaRecord is not None:
            for _, row in df.iterrows():
                data = row.to_dict()
                # model_validate accepts dicts directly (Pydantic v2)
                try:
                    m = EtesaRecord.model_validate(data)
                except Exception:
                    # on validation failure, still append a partial model via safe init
                    try:
                        m = EtesaRecord(**data)
                    except Exception:
                        m = None
                models.append(m)

        return df.reset_index(drop=True), models

    # Reorder to a sensible schema
    cols_order = []
    if 'date' in df.columns:
        cols_order.append('date')
    if 'day' in df.columns:
        cols_order.append('day')
    for c in ['temp_max_c', 'temp_min_c', 'temp_avg_c', 'rain_daily_mm', 'rain_accum_month_mm', 'rain_daily_hist_mm', 'rain_accum_hist_mm']:
        if c in df.columns:
            cols_order.append(c)

    # Preserve any other columns as well
    remaining = [c for c in df.columns if c not in cols_order]
    df = df[cols_order + remaining] if cols_order else df

    return df.reset_index(drop=True)
# parse_csv.py

import pandas as pd

def parse_etesa_csv(csv_file):
    """Lee el CSV limpio de ETESA y lo convierte a DataFrame estándar."""
    try:
        df = pd.read_csv(csv_file)

        # Estandarizar columnas
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

        if "día" in df.columns:
            df.rename(columns={"día": "day"}, inplace=True)

        return df

    except Exception as e:
        print("[ERROR] Falló lectura/parsing CSV:", csv_file, e)
        return None