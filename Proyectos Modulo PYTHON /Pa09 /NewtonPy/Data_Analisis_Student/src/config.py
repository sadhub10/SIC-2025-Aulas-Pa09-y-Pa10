from pathlib import Path

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]

# Data
RAW_DATA       = BASE_DIR / "data" / "raw" / "dataset.xlsx"
INTERIM_CSV    = BASE_DIR / "data" / "interim" / "dataset_clean.csv"
PROCESSED_CSV  = BASE_DIR / "data" / "processed" / "student_monthly_agg.csv"

# Docs / figuras
MAPPING_FILE   = BASE_DIR / "docs" / "mapping_columns.json"
FIG_DIR        = BASE_DIR / "docs" / "figures"

# Crear carpetas necesarias si no existen
INTERIM_CSV.parent.mkdir(parents=True, exist_ok=True)
PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

