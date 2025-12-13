from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
import pandas as pd
import numpy as np

# Ruta absoluta al archivo final
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
VECTORIZER_PATH = os.path.join(ROOT_DIR, "src", "models", "saved", "tfidf_vectorizer.pkl")


def _clean_input_text(X):
    """
    Limpia la serie de textos para garantizar que TfidfVectorizer no falle.
    Elimina:
        - NaN reales
        - strings vacíos
        - "nan", "none"
        - objetos no-string
    """
    print(">>> Limpieza interna de X_train para vectorizer...")

    # Convertir todo a string
    X = X.astype(str)

    # Normalizar
    X = X.str.strip()

    # Filtrar valores inválidos
    mask_valid = (
        (X != "") &
        (X.str.lower() != "nan") &
        (X.str.lower() != "none")
    )

    cleaned_X = X[mask_valid]

    print(f">>> Total textos originales: {len(X)}")
    print(f">>> Textos válidos para entrenamiento: {len(cleaned_X)}")
    print(f">>> Textos removidos: {len(X) - len(cleaned_X)}")

    return cleaned_X


def create_vectorizer(X_train):
    """
    Crea y entrena un vectorizador TF-IDF completamente robusto.
    """

    print(">>> [CREATE] Iniciando creación del vectorizador TF-IDF...")

    # Asegurar carpeta
    os.makedirs(os.path.dirname(VECTORIZER_PATH), exist_ok=True)

    # LIMPIAR X_train ANTES DE ENTRENAR (muy importante)
    X_train_clean = _clean_input_text(X_train)

    if len(X_train_clean) == 0:
        raise ValueError("❌ ERROR: X_train quedó vacío después de limpiar. No se puede entrenar TF-IDF.")

    # Crear vectorizador
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1,2),       # puedes modificar
        min_df=2,                # evita ruido
        max_df=0.95              # evita términos demasiado frecuentes
    )

    print(">>> Entrenando vectorizador con", len(X_train_clean), "documentos...")

    # ENTRENARLO ANTES DE GUARDARLO
    vectorizer.fit(X_train_clean)

    print(">>> Guardando vectorizador en:", VECTORIZER_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print("[OK] Vectorizador guardado correctamente.")

    return vectorizer


def load_vectorizer():
    """
    Carga el vectorizador TF-IDF desde disco con debug.
    """
    print(">>> DEBUG: Cargando vectorizador desde:", VECTORIZER_PATH)

    try:
        vec = joblib.load(VECTORIZER_PATH)
        print(">>> DEBUG: Vectorizador cargado correctamente:", type(vec))
        print(">>> DEBUG: Tiene vocabulario?:", hasattr(vec, "vocabulary_"))
        print(">>> DEBUG: Tiene IDF?:", hasattr(vec, "idf_"))
        return vec

    except Exception as e:
        print(">>> ERROR AL CARGAR VECTORIZADOR:", e)
        raise e
