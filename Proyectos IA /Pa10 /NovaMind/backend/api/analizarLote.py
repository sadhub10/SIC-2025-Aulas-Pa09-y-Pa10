# backend/api/analizarLote.py
from fastapi import APIRouter, Depends
from backend.config.database import get_db
from backend.core.coreServices import guardarAnalisis

router = APIRouter(
    prefix="/analizar",
    tags=["Análisis"]
)

@router.post("/lote")
def analizar_lote(data: list, db=Depends(get_db)):
    procesados = 0

    for fila in data:
        comentario = fila.get("comentario")
        if not comentario:
            continue

        meta = {
            "departamento": fila.get("departamento"),
            "equipo": fila.get("equipo"),
            "fecha": fila.get("fecha")
        }

        guardarAnalisis(db, comentario, meta)
        procesados += 1

    return {
        "success": True,
        "procesados": procesados,
        "guardados": procesados
    }
