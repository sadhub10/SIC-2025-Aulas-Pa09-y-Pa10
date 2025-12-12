import requests
from typing import Optional, Dict, Any, List

BASE_URL = "http://127.0.0.1:8000"

def analizarComentarioIndividual(comentario: str, meta: Optional[Dict] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/analizar-comentario/"
    payload = {
        "comentario": comentario,
        "meta": meta or {}
    }
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def analizarLoteCSV(datos: List[Dict[str, Any]]) -> Dict[str, Any]:
    url = f"{BASE_URL}/analizar-lote/"
    payload = {"datos": datos}
    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()
    return response.json()

def obtenerHistoricos(
    limit: int = 100,
    departamento: Optional[str] = None,
    equipo: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    stress_level: Optional[str] = None
) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/historicos/"
    params = {"limit": limit}
    if departamento:
        params["departamento"] = departamento
    if equipo:
        params["equipo"] = equipo
    if fecha_inicio:
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        params["fecha_fin"] = fecha_fin
    if stress_level:
        params["stress_level"] = stress_level

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerAlertas(nivel: str = "alto", limite: int = 20, departamento: Optional[str] = None) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/alertas/"
    params = {"nivel": nivel, "limite": limite}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerEstadisticas(
    departamento: Optional[str] = None,
    equipo: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
) -> Dict[str, Any]:
    url = f"{BASE_URL}/estadisticas/"
    params = {}
    if departamento:
        params["departamento"] = departamento
    if equipo:
        params["equipo"] = equipo
    if fecha_inicio:
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        params["fecha_fin"] = fecha_fin

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerEstadisticasDepartamentos() -> Dict[str, Any]:
    url = f"{BASE_URL}/estadisticas/departamentos/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerEstadisticasEquipos(departamento: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/estadisticas/equipos/"
    params = {}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerTendencias(dias: int = 30, departamento: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/estadisticas/tendencias/"
    params = {"dias": dias}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerPatrones() -> Dict[str, Any]:
    url = f"{BASE_URL}/alertas/patrones/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerAlertasDepartamento(departamento: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/alertas/departamento/{departamento}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerTextoComentarios(departamento: Optional[str] = None, limit: int = 500) -> List[str]:
    url = f"{BASE_URL}/historicos/texto/"
    params = {"limit": limit}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("comentarios", [])

def obtenerDepartamentos() -> List[str]:
    url = f"{BASE_URL}/historicos/departamentos/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json().get("departamentos", [])

def obtenerEquipos(departamento: Optional[str] = None) -> List[str]:
    url = f"{BASE_URL}/historicos/equipos/"
    params = {}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("equipos", [])

def verificarConexion() -> bool:
    try:
        url = f"{BASE_URL}/"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def login(usuario: str, password: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/login/"
    payload = {"usuario": usuario, "password": password}
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
