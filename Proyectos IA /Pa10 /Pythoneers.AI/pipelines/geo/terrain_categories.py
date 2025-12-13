import math

def classify_terrain(slope_deg):
    if slope_deg is None:
        return "unknown"

    slope_percent = math.tan(math.radians(slope_deg)) * 100

    if slope_percent < 2:
        return "llanura"
    elif slope_percent < 6:
        return "lomereo_suave"
    elif slope_percent < 15:
        return "colinas"
    elif slope_percent < 30:
        return "montanoso"
    else:
        return "muy_montanoso"