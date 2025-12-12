# api/manejarHistoricos.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from backend.config.database import get_db
from backend.core.coreServices import obtenerHistoricos
from backend.core.coreModels import AnalisisComentario


router = APIRouter(tags=["Historicos"])

@router.get("/historicos/")
def historicos(
    limit: int = 100,
    departamento: Optional[str] = None,
    equipo: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    stress_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnalisisComentario)

    if departamento:
        query = query.filter(AnalisisComentario.departamento == departamento)
    if equipo:
        query = query.filter(AnalisisComentario.equipo == equipo)
    if fecha_inicio:
        query = query.filter(AnalisisComentario.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(AnalisisComentario.fecha <= fecha_fin)
    if stress_level:
        query = query.filter(AnalisisComentario.stress_level == stress_level)

    rows = query.order_by(AnalisisComentario.id.desc()).limit(limit).all()

    return [
        {
            "id": r.id,
            "comentario": r.comentario,
            "emotion_label": r.emotion_label,
            "emotion_score": r.emotion_score,
            "stress_level": r.stress_level,
            "sent_pos": r.sent_pos,
            "sent_neu": r.sent_neu,
            "sent_neg": r.sent_neg,
            "categories": r.categories,
            "summary": r.summary,
            "suggestion": r.suggestion,
            "departamento": r.departamento,
            "equipo": r.equipo,
            "fecha": r.fecha,
            "created_at": str(r.created_at)
        } for r in rows
    ]

@router.get("/historicos/texto/")
def obtenerTextoComentarios(
    departamento: Optional[str] = None,
    limit: int = 500,
    db: Session = Depends(get_db)
):
    query = db.query(AnalisisComentario.comentario)

    if departamento:
        query = query.filter(AnalisisComentario.departamento == departamento)

    rows = query.limit(limit).all()
    return {"comentarios": [r[0] for r in rows if r[0]]}

@router.get("/historicos/categorias/")
def obtenerTodasCategorias(db: Session = Depends(get_db)):
    registros = db.query(AnalisisComentario.categories).all()
    categorias_set = set()

    for r in registros:
        if isinstance(r[0], list):
            for cat in r[0]:
                if isinstance(cat, dict) and "label" in cat:
                    categorias_set.add(cat["label"])

    return {"categorias": sorted(list(categorias_set))}

@router.get("/historicos/departamentos/")
def obtenerDepartamentos(db: Session = Depends(get_db)):
    rows = db.query(AnalisisComentario.departamento).distinct().all()
    return {"departamentos": sorted([r[0] for r in rows if r[0]])}

@router.get("/historicos/equipos/")
def obtenerEquipos(departamento: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AnalisisComentario.equipo).distinct()
    if departamento:
        query = query.filter(AnalisisComentario.departamento == departamento)
    rows = query.all()
    return {"equipos": sorted([r[0] for r in rows if r[0]])}
