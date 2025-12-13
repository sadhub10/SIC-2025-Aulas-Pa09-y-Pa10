"""Pydantic model for ETESA daily records."""
from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import datetime


class EtesaRecord(BaseModel):
    date: Optional[datetime] = None
    day: Optional[int] = None
    temp_max_c: Optional[float] = None
    temp_min_c: Optional[float] = None
    temp_avg_c: Optional[float] = None
    rain_daily_mm: Optional[float] = None
    rain_accum_month_mm: Optional[float] = None
    rain_daily_hist_mm: Optional[float] = None
    rain_accum_hist_mm: Optional[float] = None

    @field_validator("day", mode="before")
    def _coerce_day(cls, v):
        if v is None or v == "":
            return None
        try:
            return int(v)
        except Exception:
            return None

    @field_validator("temp_max_c", "temp_min_c", "temp_avg_c", "rain_daily_mm",
                     "rain_accum_month_mm", "rain_daily_hist_mm", "rain_accum_hist_mm",
                     mode="before")
    def _coerce_numeric(cls, v):
        if v is None or v == "":
            return None
        try:
            s = str(v).strip().replace(',', '')
            return float(s)
        except Exception:
            return None

    @field_validator("date", mode="before")
    def _coerce_date(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        # let pandas handle parsing in parse_etesa_csv; accept strings too
        try:
            return datetime.fromisoformat(str(v))
        except Exception:
            return None

    class Config:
        arbitrary_types_allowed = True
