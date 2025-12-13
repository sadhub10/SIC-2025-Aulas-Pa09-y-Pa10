import os
import time
import json
import requests
import pandas as pd

CACHE_FILE = "data_cache/elevation_cache.json"
os.makedirs("data_cache", exist_ok=True)

API_URL = "https://api.open-elevation.com/api/v1/lookup"


# -------------------------
#   CACHE LOAD/SAVE
# -------------------------
def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


# -------------------------
#   API REQUEST
# -------------------------
def fetch_elevation(lat, lon, retries=3):
    """Hace una solicitud a OpenElevation con reintentos."""
    for attempt in range(retries):
        try:
            url = f"{API_URL}?locations={lat},{lon}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data["results"][0]["elevation"]

        except Exception:
            time.sleep(1)

    return None  # No se pudo obtener


# -------------------------
#   MAIN FUNCTION
# -------------------------
def get_elevation(lat, lon):
    """Retorna elevación usando cache si existe."""
    cache = load_cache()
    key = f"{lat},{lon}"

    if key in cache:
        return cache[key]

    elevation = fetch_elevation(lat, lon)
    cache[key] = elevation
    save_cache(cache)
    return elevation


# -------------------------
#   BULK APPLY TO DATAFRAME
# -------------------------
def enrich_with_elevation(df: pd.DataFrame):
    """Agrega columna 'elevation_m' al dataframe maestro."""
    if not {"lat", "lon"}.issubset(df.columns):
        print("[ELEVATION] No hay lat/lon, no se puede enriquecer.")
        return df

    unique_pairs = df[["lat", "lon"]].drop_duplicates()

    print(f"[ELEVATION] Calculando elevación para {len(unique_pairs)} coordenadas únicas...")

    cache = load_cache()

    # Crear diccionario de resultados
    elev_map = {}

    for _, row in unique_pairs.iterrows():
        lat, lon = row["lat"], row["lon"]
        key = f"{lat},{lon}"

        if key in cache:
            elev_map[key] = cache[key]
            continue

        elev = fetch_elevation(lat, lon)
        cache[key] = elev
        elev_map[key] = elev
        print(f"[OK] {key} -> {elev} m")

        save_cache(cache)
        time.sleep(0.2)  # Respetar tasa de requests

    # Combinar elevación al dataframe
    df["elevation_m"] = df.apply(lambda r: elev_map.get(f"{r['lat']},{r['lon']}"), axis=1)

    print("[ELEVATION] Elevación agregada al dataframe.")

    return df