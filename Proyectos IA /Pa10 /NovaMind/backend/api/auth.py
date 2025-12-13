from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime

from backend.config.database import get_db
from backend.core.coreModels import UsuarioRRHH

router = APIRouter(tags=["Autenticacion"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginPayload(BaseModel):
    usuario: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    usuario: str
    nombre_completo: str
    message: str

@router.post("/login/", response_model=LoginResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioRRHH).filter(
        UsuarioRRHH.usuario == payload.usuario
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    if not pwd_context.verify(payload.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    usuario.last_login = datetime.now()
    db.commit()

    return LoginResponse(
        success=True,
        usuario=usuario.usuario,
        nombre_completo=usuario.nombre_completo or usuario.usuario,
        message="Login exitoso"
    )

@router.post("/crear-usuario/")
def crearUsuario(
    usuario: str,
    password: str,
    nombre_completo: str,
    email: str,
    db: Session = Depends(get_db)
):
    existe = db.query(UsuarioRRHH).filter(UsuarioRRHH.usuario == usuario).first()
    if existe:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    password_hash = pwd_context.hash(password)

    nuevo_usuario = UsuarioRRHH(
        usuario=usuario,
        password_hash=password_hash,
        nombre_completo=nombre_completo,
        email=email,
        activo=True
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {"success": True, "usuario": usuario, "message": "Usuario creado exitosamente"}
