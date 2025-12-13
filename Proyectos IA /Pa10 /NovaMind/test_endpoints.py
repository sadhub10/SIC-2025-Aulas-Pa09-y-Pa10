#!/usr/bin/env python3
"""Test completo de todos los endpoints del backend"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print(f"{'=' * 80}\n")

def test_root():
    print_section("1. TEST: Endpoint Root (/)")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_analizar_lote():
    print_section("2. TEST: Analizar Lote (/analizar-lote/)")

    datos = [
        {
            "comentario": "Estoy muy feliz con mi trabajo, excelente ambiente",
            "departamento": "TI",
            "equipo": "Backend",
            "fecha": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "comentario": "Me siento muy estresado, demasiado trabajo",
            "departamento": "Ventas",
            "equipo": "Comercial",
            "fecha": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "comentario": "Mi salario no es justo",
            "departamento": "Marketing",
            "equipo": "Digital",
            "fecha": datetime.now().strftime("%Y-%m-%d")
        }
    ]

    try:
        response = requests.post(
            f"{BASE_URL}/analizar-lote/",
            json={"datos": datos},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Procesados: {result.get('procesados', 0)}")
        print(f"Guardados: {result.get('guardados', 0)}")
        return response.status_code == 200 and result.get('guardados', 0) > 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_historicos():
    print_section("3. TEST: Obtener Históricos (/historicos/)")
    try:
        response = requests.get(f"{BASE_URL}/historicos/?limit=5")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Registros obtenidos: {len(result)}")
        if len(result) > 0:
            print(f"\nÚltimo registro:")
            last = result[0]
            print(f"  ID: {last.get('id')}")
            print(f"  Comentario: {last.get('comentario', '')[:50]}...")
            print(f"  Emoción: {last.get('emotion_label')}")
            print(f"  Estrés: {last.get('stress_level')}")
            print(f"  Sugerencia: {last.get('suggestion', '')[:60]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_alertas():
    print_section("4. TEST: Sistema de Alertas (/alertas/)")
    try:
        response = requests.get(f"{BASE_URL}/alertas/?nivel=alto&limite=5")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Alertas de nivel alto: {len(result)}")
        if len(result) > 0:
            print(f"\nPrimera alerta:")
            alert = result[0]
            print(f"  ID: {alert.get('id')}")
            print(f"  Comentario: {alert.get('comentario', '')[:50]}...")
            print(f"  Estrés: {alert.get('stress_level')}")
            print(f"  Sugerencia: {alert.get('suggestion', '')[:60]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_patrones():
    print_section("5. TEST: Detección de Patrones (/alertas/patrones/)")
    try:
        response = requests.get(f"{BASE_URL}/alertas/patrones/")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Total comentarios: {result.get('total_comentarios', 0)}")
        print(f"% Estrés alto: {result.get('stress_alto_porcentaje', 0):.1f}%")
        print(f"\nPatrones detectados: {len(result.get('patrones_detectados', []))}")
        for i, patron in enumerate(result.get('patrones_detectados', [])[:3], 1):
            print(f"\n  {i}. {patron.get('tipo')} ({patron.get('severidad')})")
            print(f"     {patron.get('mensaje')}")
            print(f"     Acción: {patron.get('accion', '')[:70]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_estadisticas():
    print_section("6. TEST: Estadísticas (/estadisticas/)")
    try:
        response = requests.get(f"{BASE_URL}/estadisticas/")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"\nEstadísticas Generales:")
        print(f"  Total registros: {result.get('total', 0)}")

        stress = result.get('stress_distribution', {})
        print(f"\nDistribución de Estrés:")
        print(f"  Alto: {stress.get('alto', 0)}")
        print(f"  Medio: {stress.get('medio', 0)}")
        print(f"  Bajo: {stress.get('bajo', 0)}")

        emotions = result.get('top_emotions', [])
        print(f"\nTop Emociones:")
        for emo in emotions[:3]:
            print(f"  {emo.get('emotion')}: {emo.get('count')}")

        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def run_tests():
    print("\n" + "=" * 80)
    print("INICIANDO TESTS DE ENDPOINTS DEL BACKEND")
    print("=" * 80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Asegúrate de que el backend esté corriendo: uvicorn main:app --reload")

    results = {
        "Root": test_root(),
        "Analizar Lote": test_analizar_lote(),
        "Históricos": test_historicos(),
        "Alertas": test_alertas(),
        "Patrones": test_patrones(),
        "Estadísticas": test_estadisticas()
    }

    print_section("RESUMEN DE TESTS")
    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests pasaron")

    if passed == total:
        print("\n🎉 ¡TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE!")
    else:
        print(f"\n⚠️  {total - passed} endpoint(s) fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    run_tests()
