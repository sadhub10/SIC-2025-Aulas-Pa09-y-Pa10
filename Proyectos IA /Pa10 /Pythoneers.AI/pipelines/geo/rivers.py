import os
import math
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point, box
from shapely.ops import unary_union
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd


def load_rivers(country="Panama"):
    """Descarga o carga los ríos de `country` desde OSM.

    Se subdivide el área en tiles de aproximadamente `OSM_TILE_KM` km y
    se descargan las geometrías en paralelo para acelerar Overpass.
    Se guarda un cache en `data_raw/osm/rivers_{country}.parquet`.
    """
    tags = {"waterway": ["river", "stream", "canal"]}

    # Cache local
    cache_dir = os.path.join("data_raw", "osm")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"rivers_{country.replace(' ', '_')}.parquet")
    force_refresh = False
    if os.path.exists(cache_file) and not force_refresh:
        try:
            cached = gpd.read_parquet(cache_file)
            if not cached.empty:
                return cached
        except Exception:
            pass

    # Geocodificar lugar y construir tiles
    place_gdf = ox.geocode_to_gdf(country)
    if place_gdf is None or place_gdf.empty:
        raise RuntimeError(f"No se pudo geocodificar {country}")
    place_geom = unary_union(place_gdf.geometry)

    tile_km = int(os.getenv("OSM_TILE_KM", "50"))
    max_workers = int(os.getenv("OSM_MAX_WORKERS", "6"))

    step_deg_lat = tile_km / 111.0
    center_lat = place_geom.centroid.y
    step_deg_lon = tile_km / (111.320 * math.cos(math.radians(center_lat)) or 1)

    minx, miny, maxx, maxy = place_geom.bounds
    tiles = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            candidate = box(x, y, x + step_deg_lon, y + step_deg_lat)
            inter = candidate.intersection(place_geom)
            if not inter.is_empty:
                tiles.append(inter)
            y += step_deg_lat
        x += step_deg_lon

    # Si no se generaron tiles (área pequeña), usar llamada directa
    if len(tiles) == 0:
        if hasattr(ox, "geometries_from_place"):
            gdf = ox.geometries_from_place(country, tags)
        elif hasattr(ox, "features_from_place"):
            gdf = ox.features_from_place(country, tags)
        else:
            raise RuntimeError("La versión instalada de osmnx no soporta geometries_from_place ni features_from_place")
    else:
        # Descargar por tile en paralelo
        def _fetch(tile):
            try:
                if hasattr(ox, "geometries_from_polygon"):
                    return ox.geometries_from_polygon(tile, tags)
                elif hasattr(ox, "features_from_polygon"):
                    return ox.features_from_polygon(tile, tags)
                else:
                    return ox.features_from_place(tile.wkt, tags)
            except Exception as e:
                warnings.warn(f"Error fetching tile: {e}")
                return gpd.GeoDataFrame(columns=["geometry"])

        frames = []
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(_fetch, t) for t in tiles]
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    if isinstance(res, gpd.GeoDataFrame) and not res.empty:
                        frames.append(res)
                except Exception as e:
                    warnings.warn(f"Tile fetch failed: {e}")

        if len(frames) == 0:
            gdf = gpd.GeoDataFrame(columns=["geometry"])
        else:
            gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True))

    # Normalizar y asegurar CRS
    if "geometry" not in gdf.columns:
        geom_cols = [c for c in gdf.columns if c.lower() in ("geometry", "geom")] or []
        if geom_cols:
            gdf = gdf.rename(columns={geom_cols[0]: "geometry"})
        else:
            warnings.warn("No se encontró columna de geometría en los datos OSM retornados")
            return gpd.GeoDataFrame(columns=["geometry"]) 

    gdf = gdf[["geometry"]].copy()
    if not isinstance(gdf, gpd.GeoDataFrame):
        gdf = gpd.GeoDataFrame(gdf, geometry="geometry")
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)

    # Guardar cache si es posible
    try:
        gdf.to_parquet(cache_file, index=False)
    except Exception:
        pass

    return gdf


def distance_to_river(lat, lon, rivers_gdf):
    """Distancia en metros al río más cercano.

    Nota: `rivers_gdf` y el punto son esperados en EPSG:4326. Para
    calcular distancias en metros se reproyecta a una CRS métrica
    (UTM) antes de calcular.
    """
    p = Point(lon, lat)

    # Construir GeoSeries para el punto
    pt_gdf = gpd.GeoDataFrame([{"geometry": p}], geometry="geometry", crs="EPSG:4326")

    # Si rivers_gdf no tiene CRS, asumir WGS84
    if rivers_gdf.crs is None:
        rivers_gdf = rivers_gdf.set_crs(epsg=4326)

    # Reproyectar ambos a CRS métrica local (usar UTM basado en punto)
    try:
        utm_crs = ox.projection.project_gdf(pt_gdf).crs
        rivers_proj = rivers_gdf.to_crs(utm_crs)
        pt_proj = pt_gdf.to_crs(utm_crs)
    except Exception:
        # Fallback simple: usar EPSG:3857
        rivers_proj = rivers_gdf.to_crs(epsg=3857)
        pt_proj = pt_gdf.to_crs(epsg=3857)

    distances = rivers_proj.distance(pt_proj.iloc[0].geometry)
    return distances.min()