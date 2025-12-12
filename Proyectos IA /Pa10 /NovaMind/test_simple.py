#!/usr/bin/env python3
"""Test rápido solo de emoción y sentimiento"""

from transformers import pipeline

print("=" * 60)
print("TEST RÁPIDO - EMOCIÓN Y SENTIMIENTO")
print("=" * 60)

comentarios = [
    "Estoy muy contento con mi trabajo, el equipo es excelente",
    "Me siento muy estresado, tengo demasiado trabajo",
    "La comunicación con mi jefe es muy mala"
]

# Cargar modelos
print("\nCargando modelos...")
emotion_pipe = pipeline("text-classification", model="finiteautomata/beto-emotion-analysis", device=-1)
sentiment_pipe = pipeline("sentiment-analysis", model="pysentimiento/robertuito-sentiment-analysis", device=-1)
print("Modelos cargados!\n")

for i, texto in enumerate(comentarios, 1):
    print(f"\n{i}. Texto: {texto}")

    # Emoción
    emo = emotion_pipe(texto)[0]
    print(f"   Emoción: {emo['label']} ({emo['score']:.3f})")

    # Sentimiento
    sent = sentiment_pipe(texto)[0]
    label = sent['label']
    score = sent['score']

    # Mapear a nivel de estrés
    if label == "NEG":
        estres = "alto"
    elif label == "POS":
        estres = "bajo"
    else:
        estres = "medio"

    print(f"   Sentimiento: {label} ({score:.3f}) -> Estrés: {estres}")

print("\n" + "=" * 60)
print("TEST COMPLETADO!")
print("=" * 60)
