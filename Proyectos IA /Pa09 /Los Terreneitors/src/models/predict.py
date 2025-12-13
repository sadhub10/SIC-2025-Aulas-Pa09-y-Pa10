import joblib
import os
from deep_translator import GoogleTranslator
from src.features.vectorizer import load_vectorizer
from src.data.preprocess import clean_text

# ================================
# RUTA ABSOLUTA AL MODELO
# ================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(ROOT_DIR, "src", "models", "saved", "best_model.pkl")


# ================================
# MAPEO DE ETIQUETAS A ESTADOS CLÍNICOS
# ================================
clinical_states = {
    "Anxiety": "Ansiedad",
    "Depression": "Depresión",
    "Normal": "Normal",
    "Stress": "Estrés",
    "Suicidal": "Ideación suicida"
}


# ================================
# TRADUCCIÓN AUTOMÁTICA (ES → EN)
# ================================
def translate_if_needed(text: str):
    """Traduce textos en español al inglés automáticamente."""
    try:
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        return translated
    except Exception:
        # Si falla la traducción, usa el texto original
        return text


# ================================
# PREDICCIÓN PRINCIPAL
# ================================
def predict_text(text: str):
    print("Cargando modelo desde:", MODEL_PATH)

    # Cargar modelo entrenado
    model = joblib.load(MODEL_PATH)

    # Cargar vectorizador TF-IDF
    vectorizer = load_vectorizer()

    # Traducir si no está en inglés
    text_en = translate_if_needed(text)

    # Preprocesar texto traducido
    cleaned = clean_text(text_en)

    # Vectorizar
    vec = vectorizer.transform([cleaned])

    # Predicción bruta (en inglés)
    raw_pred = model.predict(vec)[0]

    # Convertir a estado clínico en español
    clinical_pred = clinical_states.get(raw_pred, raw_pred)

    print(f"Texto original: {text}")
    print(f"Texto traducido: {text_en}")
    print(f"Predicción interna: {raw_pred}")
    print(f"Predicción clínica: {clinical_pred}")

    return clinical_pred