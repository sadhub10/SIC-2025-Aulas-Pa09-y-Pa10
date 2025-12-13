"""
Script para limpiar y filtrar el dataset de salud mental
Mantiene solo 4 categorías: Anxiety, Depression, Stress, Suicidal
"""

import pandas as pd
import os
from pathlib import Path


# ================================
# CONFIGURACIÓN
# ================================
BASE_DIR = Path(__file__).resolve().parents[2]   # sube 2 niveles al root del proyecto
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "mental_health_dataset.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_dataset.csv"

# Categorías que queremos mantener
KEEP_CATEGORIES = ['Anxiety', 'Depression', 'Stress', 'Suicidal']

print("Directorio actual:", os.getcwd())
print("Archivo existe?:", os.path.exists(RAW_DATA_PATH))

# ================================
# FUNCIONES
# ================================
def load_raw_dataset(filepath):
    """Carga el dataset original"""
    print(f"📂 Cargando dataset desde: {filepath}")
    df = pd.read_csv(filepath)
    print(f"   Dimensiones originales: {df.shape}")
    return df


def explore_dataset(df):
    """Muestra información del dataset"""
    print("\n" + "=" * 60)
    print("📊 INFORMACIÓN DEL DATASET ORIGINAL")
    print("=" * 60)

    # Columnas
    print(f"\n📋 Columnas: {list(df.columns)}")

    # Distribución de categorías
    if 'status' in df.columns:
        label_col = 'status'
    elif 'label' in df.columns:
        label_col = 'label'
    else:
        print("⚠️ No se encontró columna de etiquetas")
        return None

    print(f"\n🏷️ Distribución de categorías en '{label_col}':")
    print(df[label_col].value_counts())
    print(f"\n📊 Proporción:")
    print(df[label_col].value_counts(normalize=True).round(3))

    # Valores nulos
    print(f"\n❓ Valores nulos por columna:")
    print(df.isnull().sum())

    return label_col


def filter_categories(df, label_col, keep_categories):
    """Filtra el dataset para mantener solo las categorías deseadas"""
    print("\n" + "=" * 60)
    print("🔍 FILTRANDO CATEGORÍAS")
    print("=" * 60)

    print(f"\n✅ Categorías a mantener: {keep_categories}")

    # Filtrar
    df_filtered = df[df[label_col].isin(keep_categories)].copy()

    print(f"\n📦 Muestras antes del filtrado: {len(df)}")
    print(f"📦 Muestras después del filtrado: {len(df_filtered)}")
    print(f"🗑️ Muestras eliminadas: {len(df) - len(df_filtered)}")

    # Mostrar distribución después del filtrado
    print(f"\n📊 Nueva distribución:")
    print(df_filtered[label_col].value_counts())
    print(f"\n📊 Nueva proporción:")
    print(df_filtered[label_col].value_counts(normalize=True).round(3))

    return df_filtered


def clean_dataset(df, label_col):
    """Limpia el dataset (elimina nulos, duplicados, etc.)"""
    print("\n" + "=" * 60)
    print("🧹 LIMPIANDO DATASET")
    print("=" * 60)

    initial_size = len(df)

    # Eliminar filas con valores nulos en columnas críticas
    text_col = 'statement' if 'statement' in df.columns else 'text'
    critical_cols = [text_col, label_col]

    print(f"\n🗑️ Eliminando valores nulos en: {critical_cols}")
    df_clean = df.dropna(subset=critical_cols).copy()
    null_removed = initial_size - len(df_clean)
    print(f"   Filas eliminadas: {null_removed}")

    # Eliminar duplicados
    print(f"\n🗑️ Eliminando duplicados...")
    before_dedup = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=[text_col]).copy()
    dupl_removed = before_dedup - len(df_clean)
    print(f"   Duplicados eliminados: {dupl_removed}")

    # Eliminar textos muy cortos (menos de 10 caracteres)
    print(f"\n🗑️ Eliminando textos muy cortos (< 10 caracteres)...")
    before_short = len(df_clean)
    df_clean = df_clean[df_clean[text_col].str.len() >= 10].copy()
    short_removed = before_short - len(df_clean)
    print(f"   Textos cortos eliminados: {short_removed}")

    # Resumen
    total_removed = initial_size - len(df_clean)
    print(f"\n📊 RESUMEN DE LIMPIEZA:")
    print(f"   Tamaño inicial:  {initial_size}")
    print(f"   Tamaño final:    {len(df_clean)}")
    print(f"   Total removido:  {total_removed} ({total_removed / initial_size * 100:.1f}%)")

    return df_clean


def standardize_columns(df):
    """Estandariza los nombres de las columnas"""
    print("\n" + "=" * 60)
    print("📝 ESTANDARIZANDO NOMBRES DE COLUMNAS")
    print("=" * 60)

    # Mapeo de nombres
    column_mapping = {
        'statement': 'text',
        'status': 'label'
    }

    df_standard = df.copy()

    for old_name, new_name in column_mapping.items():
        if old_name in df_standard.columns:
            df_standard = df_standard.rename(columns={old_name: new_name})
            print(f"   '{old_name}' → '{new_name}'")

    # Mantener solo columnas necesarias
    required_cols = ['text', 'label']
    df_standard = df_standard[required_cols].copy()

    print(f"\n✅ Columnas finales: {list(df_standard.columns)}")

    return df_standard


def save_processed_dataset(df, output_path):
    """Guarda el dataset procesado"""
    print("\n" + "=" * 60)
    print("💾 GUARDANDO DATASET PROCESADO")
    print("=" * 60)

    # Crear directorio si no existe
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # Guardar
    df.to_csv(output_path, index=False)
    print(f"\n✅ Dataset guardado en: {output_path}")
    print(f"   Dimensiones: {df.shape}")
    print(f"   Columnas: {list(df.columns)}")


def show_sample_data(df, n=5):
    """Muestra muestras del dataset procesado"""
    print("\n" + "=" * 60)
    print(f"👀 MUESTRA DEL DATASET PROCESADO (primeras {n} filas)")
    print("=" * 60)

    for idx, row in df.head(n).iterrows():
        text_preview = row['text'][:80] + "..." if len(row['text']) > 80 else row['text']
        print(f"\n{idx + 1}. Texto: {text_preview}")
        print(f"   Etiqueta: {row['label']}")


# ================================
# FUNCIÓN PRINCIPAL
# ================================
def main():
    """Función principal del script"""
    print("=" * 60)
    print("🧠 LIMPIEZA Y FILTRADO DEL DATASET DE SALUD MENTAL")
    print("=" * 60)

    # 1. Cargar dataset original
    df = load_raw_dataset(RAW_DATA_PATH)

    # 2. Explorar dataset
    label_col = explore_dataset(df)

    if label_col is None:
        print("❌ Error: No se pudo identificar la columna de etiquetas")
        return

    # 3. Filtrar categorías
    df_filtered = filter_categories(df, label_col, KEEP_CATEGORIES)

    # 4. Limpiar dataset
    df_clean = clean_dataset(df_filtered, label_col)

    # 5. Estandarizar nombres de columnas
    df_final = standardize_columns(df_clean)

    # 6. Mostrar muestra
    show_sample_data(df_final)

    # 7. Guardar dataset procesado
    save_processed_dataset(df_final, PROCESSED_DATA_PATH)

    # 8. Estadísticas finales
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 60)
    print(f"\n✅ Dataset listo para usar!")
    print(f"   Total de muestras: {len(df_final)}")
    print(f"   Categorías: {KEEP_CATEGORIES}")
    print(f"\n📋 Distribución final:")
    print(df_final['label'].value_counts())
    print(f"\n📊 Proporción final:")
    print(df_final['label'].value_counts(normalize=True).round(3))

    print("\n" + "=" * 60)
    print("🎉 ¡PROCESO COMPLETADO CON ÉXITO!")
    print("=" * 60)
    print(f"\n📍 Siguiente paso: Ejecutar el notebook '02_text_preprocessing.ipynb'")
    print(f"   para preprocesar los textos y crear 'cleaned_dataset.csv'")


# ================================
# EJECUTAR SCRIPT
# ================================
if __name__ == "__main__":
    main()