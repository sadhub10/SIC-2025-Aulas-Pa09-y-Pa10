import math
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from pipelines.geo.elevation import get_elevation

# Distancia aproximada entre grados de lat/lon en Panamá
DEG_DIST = 111_000  # metros aproximados

def get_terrain_features(lat, lon, step_deg=0.001):
    """
    Calcula slope, aspect, gradient y roughness
    usando elevaciones alrededor del punto.
    """

    # Elevación central
    c = get_elevation(lat, lon)

    # Elevaciones alrededor
    n = get_elevation(lat + step_deg, lon)
    s = get_elevation(lat - step_deg, lon)
    e = get_elevation(lat, lon + step_deg)
    w = get_elevation(lat, lon - step_deg)

    # Si falta un dato → no calculamos nada
    if None in (c, n, s, e, w):
        return {
            "slope_deg": None,
            "aspect_deg": None,
            "roughness_m": None,
            "gradient": None,
        }

    # Diferencias
    dz_dx = (e - w) / (2 * step_deg * DEG_DIST)
    dz_dy = (n - s) / (2 * step_deg * DEG_DIST)

    # ------- SLOPE -------
    slope_rad = math.atan(math.sqrt(dz_dx**2 + dz_dy**2))
    slope_deg = math.degrees(slope_rad)

    # ------- ASPECT -------
    aspect_rad = math.atan2(dz_dy, -dz_dx)
    aspect_deg = math.degrees(aspect_rad)
    if aspect_deg < 0:
        aspect_deg += 360

    # ------- ROUGHNESS -------
    roughness = max(n, s, e, w, c) - min(n, s, e, w, c)

    # ------- GRADIENT -------
    gradient = math.sqrt(dz_dx**2 + dz_dy**2)

    return {
        "slope_deg": slope_deg,
        "aspect_deg": aspect_deg,
        "roughness_m": roughness,
        "gradient": gradient
    }


def enrich_with_terrain(df):
    """Agrega múltiples columnas derivadas de elevación."""
    rows = [None] * len(df)

    # Simple cache para evitar recalcular para coordenadas idénticas (redondeadas)
    cache = {}

    def _worker(idx, lat, lon):
        key = (round(float(lat), 6), round(float(lon), 6))
        if key in cache:
            return idx, cache[key]
        try:
            feat = get_terrain_features(lat, lon)
        except Exception as e:
            print(f"[WARN] Error calculando terrain features para fila {idx}: {e}")
            feat = {"slope_deg": None, "aspect_deg": None, "roughness_m": None, "gradient": None}
        cache[key] = feat
        return idx, feat

    max_workers = int(os.getenv("TERRAIN_MAX_WORKERS", "8"))
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = []
        for idx, row in enumerate(df.itertuples(index=False, name=None)):
            try:
                # assume lat is first/second? safer to use column names
                lat = row[df.columns.get_loc("lat")]
                lon = row[df.columns.get_loc("lon")]
            except Exception:
                # fallback to dict-like access
                lat = df.iloc[idx]["lat"]
                lon = df.iloc[idx]["lon"]
            futures.append(ex.submit(_worker, idx, lat, lon))

        for fut in as_completed(futures):
            idx, feat = fut.result()
            rows[idx] = feat

    terrain_df = pd.DataFrame(rows)

    return pd.concat([df.reset_index(drop=True), terrain_df], axis=1)