# ia/preProcesamiento.py
import re

def limpiarTextoBasico(texto: str) -> str:
    """
    Limpieza mínima (por si Integrante 1 no la aplicó).
    Mantén simple para no alterar contenido semántico antes del modelo.
    """
    if not isinstance(texto, str):
        return ""
    t = texto.strip()
    t = re.sub(r"\s+", " ", t)
    return t
