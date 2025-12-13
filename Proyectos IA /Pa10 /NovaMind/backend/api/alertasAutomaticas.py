# api/alertasAutomaticas.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from backend.config.database import get_db
from backend.core.coreServices import obtenerAlertas
from backend.core.coreModels import AnalisisComentario


router = APIRouter(tags=["Alertas"])

@router.get("/alertas/")
def alertas(
    nivel: str = "alto",
    limite: int = 20,
    departamento: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnalisisComentario).filter(AnalisisComentario.stress_level == nivel)

    if departamento:
        query = query.filter(AnalisisComentario.departamento == departamento)

    rows = query.order_by(AnalisisComentario.id.desc()).limit(limite).all()

    return [
        {
            "id": r.id,
            "comentario": r.comentario,
            "stress_level": r.stress_level,
            "emotion_label": r.emotion_label,
            "categories": r.categories,
            "summary": r.summary,
            "suggestion": r.suggestion,
            "departamento": r.departamento,
            "equipo": r.equipo,
            "fecha": r.fecha
        } for r in rows
    ]

@router.get("/alertas/patrones/")
def detectarPatrones(db: Session = Depends(get_db)):
    total = db.query(func.count(AnalisisComentario.id)).scalar()

    if total == 0:
        return {
            "patrones_detectados": [],
            "mensaje": "No hay datos suficientes"
        }

    stress_alto = db.query(func.count(AnalisisComentario.id)).filter(
        AnalisisComentario.stress_level == "alto"
    ).scalar()

    stress_alto_pct = (stress_alto / total) * 100 if total > 0 else 0

    patrones = []

    if stress_alto_pct > 30:
        patrones.append({
            "tipo": "stress_critico",
            "severidad": "alta",
            "mensaje": f"Nivel crítico de estrés detectado: {stress_alto_pct:.1f}% de comentarios con estrés alto",
            "accion": "Intervención inmediata requerida. Revisar carga laboral y recursos."
        })

    registros_recientes = db.query(AnalisisComentario).order_by(
        AnalisisComentario.id.desc()
    ).limit(20).all()

    stress_reciente = sum(1 for r in registros_recientes if r.stress_level == "alto")
    if stress_reciente > 15:
        patrones.append({
            "tipo": "tendencia_creciente",
            "severidad": "media",
            "mensaje": f"Incremento en comentarios con estrés alto en últimos registros ({stress_reciente}/20)",
            "accion": "Monitorear situación y preparar plan de acción preventivo."
        })

    dept_stress = {}
    for r in db.query(AnalisisComentario).all():
        dept = r.departamento or "Sin departamento"
        if dept not in dept_stress:
            dept_stress[dept] = {"total": 0, "alto": 0}
        dept_stress[dept]["total"] += 1
        if r.stress_level == "alto":
            dept_stress[dept]["alto"] += 1

    for dept, data in dept_stress.items():
        if data["total"] >= 5:
            pct = (data["alto"] / data["total"]) * 100
            if pct > 50:
                patrones.append({
                    "tipo": "departamento_critico",
                    "severidad": "alta",
                    "mensaje": f"Departamento '{dept}' con {pct:.1f}% de estrés alto ({data['alto']}/{data['total']})",
                    "accion": f"Reunión urgente con liderazgo de {dept}. Evaluación de condiciones laborales."
                })

    emociones_negativas = db.query(func.count(AnalisisComentario.id)).filter(
        AnalisisComentario.emotion_label.in_(["anger", "fear", "sadness"])
    ).scalar()

    if emociones_negativas > total * 0.4:
        patrones.append({
            "tipo": "clima_negativo",
            "severidad": "media",
            "mensaje": f"Alta prevalencia de emociones negativas: {emociones_negativas} comentarios",
            "accion": "Implementar espacios de escucha activa y feedback bidireccional."
        })

    comentarios_positivos = db.query(func.count(AnalisisComentario.id)).filter(
        AnalisisComentario.stress_level == "bajo",
        AnalisisComentario.emotion_label.in_(["joy", "happiness", "neutral"])
    ).scalar()

    if comentarios_positivos > total * 0.6:
        patrones.append({
            "tipo": "tendencia_positiva",
            "severidad": "baja",
            "mensaje": f"Ambiente laboral saludable: {comentarios_positivos} comentarios positivos ({(comentarios_positivos/total)*100:.1f}%)",
            "accion": "Documentar y reforzar prácticas actuales. Reconocer liderazgo efectivo."
        })

    if not patrones:
        patrones.append({
            "tipo": "neutral",
            "severidad": "baja",
            "mensaje": "No se detectaron patrones críticos",
            "accion": "Mantener monitoreo regular."
        })

    return {
        "total_comentarios": total,
        "stress_alto_porcentaje": stress_alto_pct,
        "patrones_detectados": patrones
    }

@router.get("/alertas/departamento/{departamento}")
def alertasDepartamento(departamento: str, db: Session = Depends(get_db)):
    registros = db.query(AnalisisComentario).filter(
        AnalisisComentario.departamento == departamento
    ).all()

    total = len(registros)
    if total == 0:
        return {"mensaje": "No hay datos para este departamento"}

    stress_alto = sum(1 for r in registros if r.stress_level == "alto")
    stress_medio = sum(1 for r in registros if r.stress_level == "medio")
    stress_bajo = sum(1 for r in registros if r.stress_level == "bajo")

    categorias = {}
    for r in registros:
        if isinstance(r.categories, list):
            for cat in r.categories:
                label = cat.get("label", "")
                categorias[label] = categorias.get(label, 0) + 1

    top_categorias = sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "departamento": departamento,
        "total": total,
        "stress": {
            "alto": stress_alto,
            "medio": stress_medio,
            "bajo": stress_bajo
        },
        "top_categorias": [{"categoria": c, "count": cnt} for c, cnt in top_categorias],
        "alertas": [{
            "id": r.id,
            "comentario": r.comentario,
            "stress_level": r.stress_level,
            "summary": r.summary,
            "fecha": r.fecha
        } for r in registros if r.stress_level == "alto"][:10]
    }
