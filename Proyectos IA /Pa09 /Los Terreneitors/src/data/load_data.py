import os
import pandas as pd
from sklearn.model_selection import train_test_split

def load_dataset(filename="mental_health_dataset.csv"):
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dataset_path = os.path.join(base_path, "data", "raw", filename)

    print("Cargando dataset desde:", dataset_path)

    df = pd.read_csv(dataset_path)
    df = df.dropna(subset=["statement", "status"])
    return df

def split_data(df, test_size=0.2, random_state=42):
    X = df["clean_text"]
    y = df["status"]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)
