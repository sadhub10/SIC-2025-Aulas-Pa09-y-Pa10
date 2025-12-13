from pydantic import BaseModel, Field
from pydantic import field_validator, ValidationInfo
from typing import List, Dict, Optional
from datetime import datetime
import re


class StationData(BaseModel):
    latitud: Optional[float]
    longitud: Optional[float]
    nombre: str
    sensor_valor: Optional[str] = None
    sensor_fecha: Optional[datetime] = None
    numero_estacion: str
    sensor_valor_sin_format: Optional[float] = None
    adicionales: List = Field(default_factory=list)

    @field_validator("latitud", "longitud", mode="before")
    def _parse_coord(cls, v):
        if v is None or v == "":
            return None
        try:
            return float(v)
        except Exception:
            return None

    @field_validator("sensor_fecha", mode="before")
    def _parse_fecha(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        s = str(v).strip()
        # Try common formats used in the payload
        formats = ["%d/%m/%Y %I:%M %p", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        # Fallback to dateutil if available
        try:
            from dateutil import parser

            return parser.parse(s)
        except Exception:
            return None

    @field_validator("sensor_valor_sin_format", mode="after")
    def _parse_sensor_valor_sin_format(cls, v, info: ValidationInfo):
        # If already provided, try to cast
        if v is not None and v != "":
            try:
                return float(v)
            except Exception:
                pass

        sval = info.data.get("sensor_valor") if info and getattr(info, "data", None) is not None else None
        if not sval:
            return None
        # Extraer número de la cadena (soporta ints y floats, con signo)
        m = re.search(r"[-+]?[0-9]*\.?[0-9]+", str(sval))
        if m:
            try:
                return float(m.group())
            except Exception:
                return None
        return None


class EstacionesModel(BaseModel):
    estaciones: Dict[str, StationData]
