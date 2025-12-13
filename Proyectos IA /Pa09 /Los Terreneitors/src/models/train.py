import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer

from imblearn.over_sampling import SMOTE

from src.data.load_data import load_dataset
from src.data.preprocess import preprocess_series


# ================================
# RUTAS ABSOLUTAS DEL PROYECTO
# ================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SAVE_DIR = os.path.join(ROOT_DIR, "src", "models", "saved")
os.makedirs(SAVE_DIR, exist_ok=True)

MODEL_PATH = os.path.join(SAVE_DIR, "best_model.pkl")
VECTORIZER_PATH = os.path.join(SAVE_DIR, "tfidf_vectorizer.pkl")


# ================================
# ENTRENAMIENTO COMPLETO
# ================================
def train_models():

    print("\n📥 Cargando dataset...")
    df = load_dataset()

    print("🧹 Preprocesando texto...")
    df["clean_text"] = preprocess_series(df["statement"])

    X = df["clean_text"]
    y = df["status"]   # etiqueta clínica

    print("\n✂️ Dividiendo dataset en train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # ================================
    # TF-IDF AVANZADO (BIGRAMAS)
    # ================================
    print("\n🔠 Creando vectorizador TF-IDF (1-2 grams)...")
    vectorizer = TfidfVectorizer(
        max_features=15000,
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.9
    )

    print("🔡 Entrenando vectorizador...")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("💾 Guardando vectorizador en:", VECTORIZER_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    # ================================
    # BALANCEO CON SMOTE
    # ================================
    print("\n📊 Apicando SMOTE para balancear clases...")
    sm = SMOTE(random_state=42)
    X_train_balanced, y_train_balanced = sm.fit_resample(X_train_vec, y_train)

    # ================================
    # ENTRENAMIENTO DEL MODELO SVM
    # ================================
    print("\n🤖 Entrenando modelo SVM con class_weight='balanced'...")
    svm = LinearSVC(class_weight="balanced")

    svm.fit(X_train_balanced, y_train_balanced)

    # ================================
    # EVALUACIÓN
    # ================================
    print("\n📈 Evaluando modelo en test set...\n")
    preds = svm.predict(X_test_vec)

    print("📊 Reporte de clasificación:")
    print(classification_report(y_test, preds))

    # ================================
    # GUARDAR MODELO
    # ================================
    print("\n💾 Guardando modelo en:", MODEL_PATH)
    joblib.dump(svm, MODEL_PATH)

    print("\n✅ Entrenamiento finalizado con éxito.")
    print("Modelo y vectorizador están listos para el dashboard.")


if __name__ == "__main__":
    train_models()
