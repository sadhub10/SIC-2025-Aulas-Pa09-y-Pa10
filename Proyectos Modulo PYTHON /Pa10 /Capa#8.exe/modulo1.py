"""
Módulo 1 _ Red de Transporte (actualizado)
Define la infraestructura estática del sistema MOVILIDAD 4.0
con las rutas correctas y nombres oficiales actualizados.
"""

# --- PARADAS (referenciales, pueden ajustarse más adelante) ---
PARADAS = {
    "T149_1": {"nombre": "San Isidro", "coordenadas": (0, 0)},
    "T149_2": {"nombre": "Corredor Norte", "coordenadas": (0, 0)},
    "T149_3": {"nombre": "Terminal de Albrook", "coordenadas": (0, 0)},

    "A096_1": {"nombre": "Metro Villa Zaita", "coordenadas": (0, 0)},
    "A096_2": {"nombre": "Vía Panamá Norte", "coordenadas": (0, 0)},
    "A096_3": {"nombre": "Metro Cerro Viento", "coordenadas": (0, 0)},

    "M100_1": {"nombre": "Av. Ricardo J. Alfaro", "coordenadas": (0, 0)},
    "M100_2": {"nombre": "Calidonia", "coordenadas": (0, 0)},
    "M100_3": {"nombre": "Terminal de Albrook", "coordenadas": (0, 0)},

    "C918_1": {"nombre": "Zona Pago 5 de Mayo", "coordenadas": (0, 0)},
    "C918_2": {"nombre": "Av. Ricardo J. Alfaro", "coordenadas": (0, 0)},
    "C918_3": {"nombre": "Av. La Paz", "coordenadas": (0, 0)},
    "C918_4": {"nombre": "Transístmica", "coordenadas": (0, 0)},

    "C898_1": {"nombre": "Paitilla", "coordenadas": (0, 0)},
    "C898_2": {"nombre": "Plaza Edison", "coordenadas": (0, 0)},
    "C898_3": {"nombre": "Vía Brasil", "coordenadas": (0, 0)},
}

# --- RUTAS PRINCIPALES (coinciden con imágenes en /imgRutas) ---
RUTAS = {
    "T149": {
        "nombre": "San Isidro - Corredor Norte - Albrook (Ida)",
        "paradas": [
            {"id": "T149_1", "orden": 1, "tiempo_transcurso": 6},
            {"id": "T149_2", "orden": 2, "tiempo_transcurso": 7},
            {"id": "T149_3", "orden": 3, "tiempo_transcurso": None}
        ],
        "frecuencia": 45,
        "tiempo_espera_base": 4
    },
    "A096": {
        "nombre": "Metro Villa Zaita - Vía Panamá Norte - Metro Cerro Viento (Ida)",
        "paradas": [
            {"id": "A096_1", "orden": 1, "tiempo_transcurso": 8},
            {"id": "A096_2", "orden": 2, "tiempo_transcurso": 7},
            {"id": "A096_3", "orden": 3, "tiempo_transcurso": None}
        ],
        "frecuencia": 40,
        "tiempo_espera_base": 3
    },
    "M100": {
        "nombre": "Av. Ricardo J. Alfaro - Calidonia - Albrook (Ida)",
        "paradas": [
            {"id": "M100_1", "orden": 1, "tiempo_transcurso": 5},
            {"id": "M100_2", "orden": 2, "tiempo_transcurso": 6},
            {"id": "M100_3", "orden": 3, "tiempo_transcurso": None}
        ],
        "frecuencia": 35,
        "tiempo_espera_base": 3
    },
    "C918": {
        "nombre": "ZP 5 de Mayo - Av. Ricardo J. Alfaro - Av. La Paz - Transístmica (Ida)",
        "paradas": [
            {"id": "C918_1", "orden": 1, "tiempo_transcurso": 5},
            {"id": "C918_2", "orden": 2, "tiempo_transcurso": 6},
            {"id": "C918_3", "orden": 3, "tiempo_transcurso": 5},
            {"id": "C918_4", "orden": 4, "tiempo_transcurso": None}
        ],
        "frecuencia": 30,
        "tiempo_espera_base": 3
    },
    "C898": {
        "nombre": "Paitilla - Plaza Edison - Vía Brasil (Ida)",
        "paradas": [
            {"id": "C898_1", "orden": 1, "tiempo_transcurso": 4},
            {"id": "C898_2", "orden": 2, "tiempo_transcurso": 5},
            {"id": "C898_3", "orden": 3, "tiempo_transcurso": None}
        ],
        "frecuencia": 25,
        "tiempo_espera_base": 2
    }
}

# --- FLOTA ---
FLOTA_AUTOBUSES = [f"Bus_{i:02d}" for i in range(1, 11)]

# --- FUNCIÓN AUXILIAR ---
def mostrar_ruta(ruta_id: str):
    """Imprime las paradas y tiempos de una ruta."""
    if ruta_id not in RUTAS:
        print("Ruta no encontrada.")
        return
    ruta = RUTAS[ruta_id]
    print(f"\nRuta: {ruta['nombre']}")
    print("Secuencia de paradas:")
    for parada in ruta["paradas"]:
        nombre = PARADAS[parada["id"]]["nombre"]
        t = parada["tiempo_transcurso"]
        tiempo = f"{t} min" if t is not None else "—"
        print(f"  {parada['orden']:>2}. {nombre:<35} {tiempo}")

if __name__ == "__main__":
    for r in RUTAS:
        mostrar_ruta(r)
