# utils/helpers.py
import csv
from typing import List, Dict

def cargarCSV(ruta: str) -> List[Dict]:
    filas: List[Dict] = []
    with open(ruta, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filas.append(row)
    return filas
