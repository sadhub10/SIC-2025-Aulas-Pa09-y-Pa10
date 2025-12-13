# outlier_detection.py

import pandas as pd
import numpy as np

def detect_outliers(df, method="zscore", threshold=3):
    """
    Detecta outliers basado en:
    - zscore
    - IQR
    - métodos rolling futuros
    """

    df = df.copy()

    if method == "zscore":
        df["zscore"] = (
            df["value"] - df["value"].mean()
        ) / df["value"].std()

        df["is_outlier"] = df["zscore"].abs() > threshold

    elif method == "iqr":
        q1 = df["value"].quantile(0.25)
        q3 = df["value"].quantile(0.75)
        iqr = q3 - q1

        df["is_outlier"] = (df["value"] < (q1 - 1.5 * iqr)) | \
                           (df["value"] > (q3 + 1.5 * iqr))

    return df