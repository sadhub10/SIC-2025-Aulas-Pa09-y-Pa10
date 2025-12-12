#!/usr/bin/env python3
"""Script para debuggear el formato de salida de los modelos"""

from transformers import pipeline

print("Testing Spanish NLP models...")
print("=" * 60)

# Test Emotion
print("\n1. Testing EMOTION model (finiteautomata/beto-emotion-analysis)...")
try:
    emotion_pipe = pipeline("text-classification", model="finiteautomata/beto-emotion-analysis", device=-1)
    result = emotion_pipe("Estoy muy contento con mi trabajo")
    print(f"   Raw output: {result}")
    print(f"   Type: {type(result)}")
    if result:
        print(f"   First element: {result[0]}")
        print(f"   Keys: {result[0].keys() if isinstance(result[0], dict) else 'N/A'}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test Sentiment
print("\n2. Testing SENTIMENT model (pysentimiento/robertuito-sentiment-analysis)...")
try:
    sentiment_pipe = pipeline("sentiment-analysis", model="pysentimiento/robertuito-sentiment-analysis", device=-1)
    result = sentiment_pipe("Estoy muy estresado")
    print(f"   Raw output: {result}")
    print(f"   Type: {type(result)}")
    if result:
        print(f"   First element: {result[0]}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("Debug complete!")
