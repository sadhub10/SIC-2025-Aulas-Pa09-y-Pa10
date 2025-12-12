from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.config.database import Base, engine
from backend.core.coreModels import AnalisisComentario

from backend.api.analizarComentario import router as analizarComentarioRouter
from backend.api.analizarLote import router as analizarLoteRouter
from backend.api.manejarHistoricos import router as historicosRouter
from backend.api.alertasAutomaticas import router as alertasRouter
from backend.api.estadisticas import router as estadisticasRouter
from backend.api.auth import router as authRouter

# Crear tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authRouter)
app.include_router(analizarComentarioRouter)
app.include_router(analizarLoteRouter)
app.include_router(historicosRouter)
app.include_router(alertasRouter)
app.include_router(estadisticasRouter)

@app.get("/")
def root():
    return {"name": settings.app_name, "status": "running"}
