#!/usr/bin/env python3
"""Test del sistema mejorado de sugerencias personalizadas"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ia.iaCore import NLPAnalyzer

def test_sugerencias():
    print("=" * 80)
    print("TEST DE SUGERENCIAS PERSONALIZADAS MEJORADAS")
    print("=" * 80)

    analyzer = NLPAnalyzer()

    casos_prueba = [
        {
            "nombre": "Sobrecarga laboral con urgencia temporal",
            "comentario": "Estoy completamente quemado, tengo demasiado trabajo y los plazos son imposibles de cumplir",
            "resultado_esperado": "Debe mencionar redistribuir tareas, plazos, prioridades"
        },
        {
            "nombre": "Problema de comunicación con jefe",
            "comentario": "Mi jefe nunca me responde, me siento ignorado y no sé qué hacer",
            "resultado_esperado": "Debe mencionar mediar comunicación con liderazgo"
        },
        {
            "nombre": "Falta de herramientas",
            "comentario": "No tengo las herramientas necesarias para hacer mi trabajo, el software es obsoleto",
            "resultado_esperado": "Debe mencionar evaluar herramientas, IT, presupuesto"
        },
        {
            "nombre": "Problema salarial",
            "comentario": "Siento que mi salario no es justo para el trabajo que hago",
            "resultado_esperado": "Debe mencionar compensación, benchmarking salarial"
        },
        {
            "nombre": "Conflicto con equipo",
            "comentario": "No me llevo bien con mis compañeros de equipo, hay mucha tensión",
            "resultado_esperado": "Debe mencionar mediación, team building"
        },
        {
            "nombre": "Necesidad de capacitación",
            "comentario": "Me gustaría aprender nuevas habilidades pero no tengo oportunidades de formación",
            "resultado_esperado": "Debe mencionar plan de desarrollo, cursos, mentoring"
        },
        {
            "nombre": "Comentario muy positivo",
            "comentario": "Estoy muy feliz en mi trabajo, el equipo es excelente y me siento valorado",
            "resultado_esperado": "Debe mencionar documentar prácticas exitosas, reconocimiento"
        },
        {
            "nombre": "Balance vida-trabajo",
            "comentario": "Trabajo demasiadas horas, no tengo tiempo para mi familia",
            "resultado_esperado": "Debe mencionar horarios, desconexión, trabajo remoto"
        }
    ]

    print("\nAnalizando casos de prueba...\n")

    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n{'=' * 80}")
        print(f"CASO {i}: {caso['nombre']}")
        print(f"{'=' * 80}")
        print(f"Comentario: \"{caso['comentario']}\"")

        resultado = analyzer.analyze_comment(
            caso['comentario'],
            {"comentario": caso['comentario']}
        )

        print(f"\nDETECCIÓN:")
        print(f"  Emoción: {resultado['emotion']['label']} ({resultado['emotion']['score']:.3f})")
        print(f"  Estrés: {resultado['stress']['level']}")
        if resultado['categories']:
            print(f"  Categorías:")
            for cat in resultado['categories']:
                print(f"    - {cat['label']}: {cat['score']:.3f}")

        print(f"\nSUGERENCIA PERSONALIZADA:")
        print(f"  {resultado['suggestion']}")

        print(f"\nEsperado: {caso['resultado_esperado']}")
        print(f"{'=' * 80}")

    print(f"\n{'=' * 80}")
    print("TEST COMPLETADO")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_sugerencias()
