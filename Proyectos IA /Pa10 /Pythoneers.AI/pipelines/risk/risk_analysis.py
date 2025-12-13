import numpy as np

def normalize(x, min_val, max_val):
    return (x - min_val) / (max_val - min_val + 1e-9)


def compute_flood_risk(row):
    """
    Calcula riesgo de inundación según lluvia, pendiente y distancia a ríos.
    """

    rain = row.get("value", 0) if row.get("sensor") == "LLUVIA" else 0
    slope = row.get("slope_deg", 0)
    dist = row.get("distance_to_river_m", 10_000)

    rain_score = normalize(rain, 0, 50)
    slope_score = 1 - normalize(slope, 0, 10)  # entre más plano → mayor riesgo
    dist_score = 1 - normalize(dist, 0, 1000)  # 0–1 km

    risk = 0.5 * rain_score + 0.3 * slope_score + 0.2 * dist_score
    return min(max(risk, 0), 1)


def compute_landslide_risk(row):
    """
    Calcula riesgo de deslizamiento según pendiente, rugosidad y lluvia.
    """
    slope = row.get("slope_deg", 0)
    rough = row.get("roughness_m", 0)
    rain = row.get("value", 0) if row.get("sensor") == "LLUVIA" else 0

    slope_score = normalize(slope, 0, 35)
    rough_score = normalize(rough, 0, 50)
    rain_score = normalize(rain, 0, 50)

    risk = 0.6 * slope_score + 0.2 * rough_score + 0.2 * rain_score
    return min(max(risk, 0), 1)