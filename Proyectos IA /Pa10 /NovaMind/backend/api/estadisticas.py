from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from backend.config.database import get_db
from backend.core.coreModels import AnalisisComentario

router = APIRouter(tags=["Estadisticas"])

@router.get("/estadisticas/")
def obtenerEstadisticas(
    departamento: Optional[str] = None,
    equipo: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
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

    registros = query.all()
    total = len(registros)

    if total == 0:
        return {
            "total": 0,
            "stress": {"alto": 0, "medio": 0, "bajo": 0},
            "emociones": {},
            "sentimiento_promedio": {"positivo": 0, "neutral": 0, "negativo": 0},
            "categorias_principales": []
        }

    stress_counts = {"alto": 0, "medio": 0, "bajo": 0}
    emo_counts = {}
    sent_sum = {"pos": 0.0, "neu": 0.0, "neg": 0.0}
    cat_counts = {}

    for r in registros:
        stress_counts[r.stress_level] = stress_counts.get(r.stress_level, 0) + 1
        emo_counts[r.emotion_label] = emo_counts.get(r.emotion_label, 0) + 1
        sent_sum["pos"] += r.sent_pos
        sent_sum["neu"] += r.sent_neu
        sent_sum["neg"] += r.sent_neg

        if isinstance(r.categories, list):
            for cat in r.categories:
                label = cat.get("label", "")
                cat_counts[label] = cat_counts.get(label, 0) + 1

    categorias_ord = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total": total,
        "stress": stress_counts,
        "emociones": emo_counts,
        "sentimiento_promedio": {
            "positivo": sent_sum["pos"] / total,
            "neutral": sent_sum["neu"] / total,
            "negativo": sent_sum["neg"] / total
        },
        "categorias_principales": [{"categoria": c, "count": cnt} for c, cnt in categorias_ord]
    }

@router.get("/estadisticas/departamentos/")
def estadisticasPorDepartamento(db: Session = Depends(get_db)):
    registros = db.query(AnalisisComentario).all()
    dept_data = {}

    for r in registros:
        dept = r.departamento or "Sin departamento"
        if dept not in dept_data:
            dept_data[dept] = {
                "total": 0,
                "stress_alto": 0,
                "stress_medio": 0,
                "stress_bajo": 0,
                "emociones": {}
            }

        dept_data[dept]["total"] += 1
        if r.stress_level == "alto":
            dept_data[dept]["stress_alto"] += 1
        elif r.stress_level == "medio":
            dept_data[dept]["stress_medio"] += 1
        else:
            dept_data[dept]["stress_bajo"] += 1

        emo = r.emotion_label
        dept_data[dept]["emociones"][emo] = dept_data[dept]["emociones"].get(emo, 0) + 1

    return dept_data

@router.get("/estadisticas/equipos/")
def estadisticasPorEquipo(departamento: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AnalisisComentario)
    if departamento:
        query = query.filter(AnalisisComentario.departamento == departamento)

    registros = query.all()
    equipo_data = {}

    for r in registros:
        eq = r.equipo or "Sin equipo"
        if eq not in equipo_data:
            equipo_data[eq] = {
                "total": 0,
                "stress_alto": 0,
                "departamento": r.departamento
            }

        equipo_data[eq]["total"] += 1
        if r.stress_level == "alto":
            equipo_data[eq]["stress_alto"] += 1

    return equipo_data

@router.get("/estadisticas/tendencias/")
def obtenerTendencias(
    dias: int = 30,
    departamento: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnalisisComentario)
    if departamento:
        query = query.filter(AnalisisComentario.departamento == departamento)

    registros = query.order_by(AnalisisComentario.fecha).all()

    fechas_data = {}
    for r in registros:
        fecha = r.fecha or "Sin fecha"
        if fecha not in fechas_data:
            fechas_data[fecha] = {
                "total": 0,
                "stress_alto": 0,
                "stress_medio": 0,
                "stress_bajo": 0
            }

        fechas_data[fecha]["total"] += 1
        if r.stress_level == "alto":
            fechas_data[fecha]["stress_alto"] += 1
        elif r.stress_level == "medio":
            fechas_data[fecha]["stress_medio"] += 1
        else:
            fechas_data[fecha]["stress_bajo"] += 1

    return fechas_data
