#!/usr/bin/env python3
"""Script de prueba para verificar el análisis de comentarios en español"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ia.iaCore import NLPAnalyzer
import json

def test_analisis():
    print("=" * 60)
    print("PRUEBA DE ANÁLISIS CON TRANSFORMERS EN ESPAÑOL")
    print("=" * 60)

    analyzer = NLPAnalyzer()

    comentarios_prueba = [
        {
            "comentario": "Estoy muy contento con mi trabajo, el equipo es excelente y me siento valorado",
            "departamento": "TI",
            "equipo": "Backend",
            "fecha": "2025-12-10"
        },
        {
            "comentario": "Me siento muy estresado, tengo demasiado trabajo y no tengo tiempo para nada",
            "departamento": "Ventas",
            "equipo": "Comercial",
            "fecha": "2025-12-10"
        },
        {
            "comentario": "La comunicación con mi jefe es muy mala, nunca responde mis mensajes",
            "departamento": "Marketing",
            "equipo": "Digital",
            "fecha": "2025-12-10"
        }
    ]

    print("\nAnalizando comentarios...\n")

    for i, comentario in enumerate(comentarios_prueba, 1):
        print(f"\n{'=' * 60}")
        print(f"COMENTARIO {i}")
        print(f"{'=' * 60}")
        print(f"Texto: {comentario['comentario']}")
        print(f"Departamento: {comentario['departamento']}")
        print(f"Equipo: {comentario['equipo']}")

        try:
            resultado = analyzer.analyze_comment(
                comentario['comentario'],
                {
                    "comentario": comentario['comentario'],
                    "departamento": comentario['departamento'],
                    "equipo": comentario['equipo'],
                    "fecha": comentario['fecha']
                }
            )

            print(f"\nRESULTADOS:")
            print(f"  Emoción: {resultado['emotion']['label']} (score: {resultado['emotion']['score']:.3f})")
            print(f"  Estrés: {resultado['stress']['level']}")
            print(f"  Sentimiento: POS={resultado['stress']['sentiment_dist'].get('positive', 0):.3f}, "
                  f"NEU={resultado['stress']['sentiment_dist'].get('neutral', 0):.3f}, "
                  f"NEG={resultado['stress']['sentiment_dist'].get('negative', 0):.3f}")

            if resultado['categories']:
                print(f"  Categorías:")
                for cat in resultado['categories']:
                    print(f"    - {cat['label']}: {cat['score']:.3f}")
            else:
                print(f"  Categorías: Ninguna detectada")

            print(f"  Resumen: {resultado['summary']}")
            print(f"  Sugerencia RRHH: {resultado['suggestion']}")

            # Verificar que todos los campos estén presentes
            campos_requeridos = ['emotion', 'stress', 'categories', 'summary', 'suggestion']
            campos_ok = all(campo in resultado for campo in campos_requeridos)

            if campos_ok:
                print(f"\n✓ TODOS LOS CAMPOS ESTÁN PRESENTES")
            else:
                print(f"\n✗ FALTAN CAMPOS")

        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 60}")
    print("PRUEBA COMPLETADA")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    test_analisis()
