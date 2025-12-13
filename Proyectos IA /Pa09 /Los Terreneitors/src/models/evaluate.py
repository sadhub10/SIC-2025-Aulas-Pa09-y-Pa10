import joblib
from sklearn.metrics import classification_report, confusion_matrix
from src.features.vectorizer import load_vectorizer
from src.data.load_data import load_dataset, split_data
from src.data.preprocess import preprocess_series

def evaluate():
    df = load_dataset()
    df["clean_text"] = preprocess_series(df["text"])

    X_train, X_test, y_train, y_test = split_data(df)

    vectorizer = load_vectorizer()
    X_test_vec = vectorizer.transform(X_test)

    model = joblib.load("saved/best_model.pkl")

    preds = model.predict(X_test_vec)

    print("\n--- Reporte ---")
    print(classification_report(y_test, preds))

    print("\n--- Matriz de Confusión ---")
    print(confusion_matrix(y_test, preds))

if __name__ == "__main__":
    evaluate()
