import pandas as pd

# cargo el dataset
df = pd.read_csv("data/dataset_unificado_normalizado.csv")

# veifico las columnas antes de eliminar
print(df.columns)

#columna mal escrita
df = df.drop(columns=["provinia"])

# Confirmo
print(df.columns)

# guardo el nuevo dataset sin la columna 'provinia'
df.to_csv("data/dataset_homicidios.csv", index=False, encoding="utf-8")
