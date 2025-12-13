# core/coreModels.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from backend.config.database import Base


class AnalisisComentario(Base):
    __tablename__ = "analisis_comentarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comentario: Mapped[str] = mapped_column(Text, nullable=False)

    emotion_label: Mapped[str] = mapped_column(String(64))
    emotion_score: Mapped[float] = mapped_column(Float)

    stress_level: Mapped[str] = mapped_column(String(32))
    sent_pos: Mapped[float] = mapped_column(Float, default=0.0)
    sent_neu: Mapped[float] = mapped_column(Float, default=0.0)
    sent_neg: Mapped[float] = mapped_column(Float, default=0.0)

    categories: Mapped[dict] = mapped_column(JSON)
    summary: Mapped[str] = mapped_column(Text)
    suggestion: Mapped[str] = mapped_column(Text)

    departamento: Mapped[str] = mapped_column(String(80), default="")
    equipo: Mapped[str] = mapped_column(String(80), default="")
    fecha: Mapped[str] = mapped_column(String(20), default="")

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

class UsuarioRRHH(Base):
    __tablename__ = "usuarios_rrhh"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    activo: Mapped[bool] = mapped_column(Integer, default=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=True)
