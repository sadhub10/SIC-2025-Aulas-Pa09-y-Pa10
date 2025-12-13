"""
Script de Análisis Exploratorio del Dataset de Salud Mental
Analiza todas las categorías disponibles y sus características
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Configuración de visualización
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)

# ================================
# CARGAR DATASET
# ================================
print("="*70)
print("🔍 ANÁLISIS EXPLORATORIO DEL DATASET DE SALUD MENTAL")
print("="*70)

# Ruta del dataset
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # sube 2 niveles al root del proyecto
DATASET_PATH = BASE_DIR / "data" / "raw" / "mental_health_dataset.csv"

try:
    df = pd.read_csv(DATASET_PATH)
    print(f"\n✅ Dataset cargado correctamente")
    print(f"📦 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
except FileNotFoundError:
    print(f"\n❌ Error: No se encontró el archivo en '{DATASET_PATH}'")
    print("Por favor, verifica la ruta del dataset.")
    exit()

# ================================
# 1. INFORMACIÓN GENERAL
# ================================
print("\n" + "="*70)
print("📋 1. INFORMACIÓN GENERAL DEL DATASET")
print("="*70)

print(f"\n📊 Columnas disponibles:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col} (tipo: {df[col].dtype})")

print(f"\n🔢 Tipos de datos:")
print(df.dtypes)

print(f"\n❓ Valores nulos por columna:")
null_counts = df.isnull().sum()
null_percentages = (df.isnull().sum() / len(df) * 100).round(2)
null_df = pd.DataFrame({
    'Columna': null_counts.index,
    'Nulos': null_counts.values,
    'Porcentaje': null_percentages.values
})
print(null_df.to_string(index=False))

print(f"\n📏 Estadísticas de filas:")
print(f"  Total de filas: {len(df)}")
print(f"  Filas completas (sin nulos): {df.dropna().shape[0]}")
print(f"  Filas con al menos un nulo: {df.isnull().any(axis=1).sum()}")

# ================================
# 2. IDENTIFICAR COLUMNA DE ETIQUETAS
# ================================
print("\n" + "="*70)
print("🏷️ 2. ANÁLISIS DE ETIQUETAS/CATEGORÍAS")
print("="*70)

# Identificar la columna de etiquetas
label_col = None
possible_names = ['status', 'label', 'category', 'class', 'emotion', 'sentiment']

for col in df.columns:
    if col.lower() in possible_names:
        label_col = col
        break

if label_col is None:
    # Mostrar primeras filas para identificar manualmente
    print("\n⚠️ No se identificó automáticamente la columna de etiquetas.")
    print("\n👀 Primeras 5 filas del dataset:")
    print(df.head())

    print("\n🔍 Por favor, indica cuál es la columna de etiquetas:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    exit()

print(f"\n✅ Columna de etiquetas identificada: '{label_col}'")

# ================================
# 3. DISTRIBUCIÓN DE CATEGORÍAS
# ================================
print("\n" + "="*70)
print("📊 3. DISTRIBUCIÓN DE TODAS LAS CATEGORÍAS")
print("="*70)

# Contar categorías
category_counts = df[label_col].value_counts()
category_percentages = (df[label_col].value_counts(normalize=True) * 100).round(2)

print(f"\n📈 Total de categorías únicas: {df[label_col].nunique()}")
print(f"\n🏷️ Categorías encontradas:\n")

# Crear tabla resumen
summary_df = pd.DataFrame({
    'Categoría': category_counts.index,
    'Cantidad': category_counts.values,
    'Porcentaje': category_percentages.values
})
print(summary_df.to_string(index=False))

# Visualización 1: Gráfico de barras
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Subplot 1: Conteo de categorías
ax1 = axes[0, 0]
category_counts.plot(kind='bar', ax=ax1, color='steelblue', edgecolor='black')
ax1.set_title('Distribución de Categorías (Conteo)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Categoría', fontsize=12)
ax1.set_ylabel('Cantidad de Muestras', fontsize=12)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis='y', alpha=0.3)

# Agregar valores en las barras
for i, v in enumerate(category_counts.values):
    ax1.text(i, v + 50, str(v), ha='center', va='bottom', fontweight='bold')

# Subplot 2: Porcentajes
ax2 = axes[0, 1]
category_percentages.plot(kind='bar', ax=ax2, color='coral', edgecolor='black')
ax2.set_title('Distribución de Categorías (Porcentaje)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Categoría', fontsize=12)
ax2.set_ylabel('Porcentaje (%)', fontsize=12)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', alpha=0.3)

# Agregar valores en las barras
for i, v in enumerate(category_percentages.values):
    ax2.text(i, v + 1, f'{v}%', ha='center', va='bottom', fontweight='bold')

# Subplot 3: Pie chart
ax3 = axes[1, 0]
colors = plt.cm.Set3(range(len(category_counts)))
wedges, texts, autotexts = ax3.pie(
    category_counts.values,
    labels=category_counts.index,
    autopct='%1.1f%%',
    colors=colors,
    startangle=90
)
ax3.set_title('Distribución de Categorías (Torta)', fontsize=14, fontweight='bold')

# Subplot 4: Análisis de balance
ax4 = axes[1, 1]
balance_data = pd.DataFrame({
    'Categoría': category_counts.index,
    'Muestras': category_counts.values
})
balance_data['Balance'] = balance_data['Muestras'] / balance_data['Muestras'].max()
colors_balance = ['green' if x > 0.5 else 'orange' if x > 0.2 else 'red' for x in balance_data['Balance']]
ax4.barh(balance_data['Categoría'], balance_data['Balance'], color=colors_balance, edgecolor='black')
ax4.set_title('Balance de Clases (normalizado)', fontsize=14, fontweight='bold')
ax4.set_xlabel('Proporción relativa al máximo', fontsize=12)
ax4.axvline(x=0.5, color='orange', linestyle='--', linewidth=2, label='50% del máximo')
ax4.axvline(x=0.2, color='red', linestyle='--', linewidth=2, label='20% del máximo')
ax4.legend()
ax4.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('dataset_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n💾 Gráfico guardado como 'dataset_analysis.png'")
plt.show()

# ================================
# 4. ANÁLISIS DE DESBALANCE
# ================================
print("\n" + "="*70)
print("⚖️ 4. ANÁLISIS DE BALANCE DE CLASES")
print("="*70)

max_samples = category_counts.max()
min_samples = category_counts.min()
ratio = max_samples / min_samples

print(f"\n📊 Estadísticas de balance:")
print(f"  Clase con más muestras:  {category_counts.idxmax()} ({max_samples} muestras)")
print(f"  Clase con menos muestras: {category_counts.idxmin()} ({min_samples} muestras)")
print(f"  Ratio máximo/mínimo: {ratio:.2f}:1")

if ratio > 10:
    print(f"\n⚠️ ALTO DESBALANCE detectado (ratio > 10:1)")
    print(f"   Recomendación: Considerar técnicas de balanceo (SMOTE, undersampling, etc.)")
elif ratio > 3:
    print(f"\n⚡ DESBALANCE MODERADO detectado (ratio > 3:1)")
    print(f"   Recomendación: Usar class_weight='balanced' en el modelo")
else:
    print(f"\n✅ Dataset relativamente balanceado")

# Identificar clases minoritarias (< 20% del máximo)
minority_threshold = max_samples * 0.2
minority_classes = category_counts[category_counts < minority_threshold]

if len(minority_classes) > 0:
    print(f"\n⚠️ Clases minoritarias (< 20% del máximo):")
    for cat, count in minority_classes.items():
        print(f"  - {cat}: {count} muestras ({count/max_samples*100:.1f}% del máximo)")

# ================================
# 5. ANÁLISIS DE TEXTOS
# ================================
print("\n" + "="*70)
print("📝 5. ANÁLISIS DE TEXTOS")
print("="*70)

# Identificar columna de texto
text_col = None
possible_text_names = ['text', 'statement', 'message', 'content', 'description']

for col in df.columns:
    if col.lower() in possible_text_names:
        text_col = col
        break

if text_col:
    print(f"\n✅ Columna de texto identificada: '{text_col}'")

    # Calcular longitudes
    df['text_length'] = df[text_col].astype(str).apply(len)
    df['word_count'] = df[text_col].astype(str).apply(lambda x: len(x.split()))

    print(f"\n📏 Estadísticas de longitud de textos:")
    print(f"  Longitud promedio (caracteres): {df['text_length'].mean():.1f}")
    print(f"  Longitud mínima: {df['text_length'].min()}")
    print(f"  Longitud máxima: {df['text_length'].max()}")
    print(f"  Mediana: {df['text_length'].median():.1f}")

    print(f"\n📝 Estadísticas de palabras:")
    print(f"  Palabras promedio por texto: {df['word_count'].mean():.1f}")
    print(f"  Palabras mínimas: {df['word_count'].min()}")
    print(f"  Palabras máximas: {df['word_count'].max()}")
    print(f"  Mediana: {df['word_count'].median():.1f}")

    # Longitudes por categoría
    print(f"\n📊 Longitud promedio por categoría:")
    length_by_category = df.groupby(label_col)['text_length'].mean().sort_values(ascending=False)
    for cat, length in length_by_category.items():
        print(f"  {cat:25s}: {length:.1f} caracteres")

    # Visualización de longitudes
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Histograma general
    ax1 = axes[0]
    ax1.hist(df['text_length'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    ax1.set_title('Distribución de Longitud de Textos', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Longitud (caracteres)', fontsize=12)
    ax1.set_ylabel('Frecuencia', fontsize=12)
    ax1.axvline(df['text_length'].mean(), color='red', linestyle='--', linewidth=2, label=f'Media: {df["text_length"].mean():.1f}')
    ax1.axvline(df['text_length'].median(), color='green', linestyle='--', linewidth=2, label=f'Mediana: {df["text_length"].median():.1f}')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Boxplot por categoría
    ax2 = axes[1]
    df.boxplot(column='text_length', by=label_col, ax=ax2)
    ax2.set_title('Longitud de Textos por Categoría', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Categoría', fontsize=12)
    ax2.set_ylabel('Longitud (caracteres)', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    plt.suptitle('')  # Remover título automático

    plt.tight_layout()
    plt.savefig('text_length_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n💾 Gráfico de longitudes guardado como 'text_length_analysis.png'")
    plt.show()

    # Ejemplos de cada categoría
    print(f"\n" + "="*70)
    print("📖 EJEMPLOS DE TEXTOS POR CATEGORÍA (primeros 2 de cada una)")
    print("="*70)

    for category in category_counts.index[:10]:  # Mostrar solo primeras 10 categorías
        print(f"\n🏷️ {category}:")
        examples = df[df[label_col] == category][text_col].head(2)
        for i, text in enumerate(examples, 1):
            text_preview = str(text)[:150] + "..." if len(str(text)) > 150 else str(text)
            print(f"  {i}. {text_preview}")

else:
    print(f"\n⚠️ No se pudo identificar automáticamente la columna de texto")

# ================================
# 6. RECOMENDACIONES
# ================================
print("\n" + "="*70)
print("💡 6. RECOMENDACIONES PARA EL PROYECTO")
print("="*70)

print(f"\n📋 Resumen de categorías encontradas:")
print(f"  Total: {len(category_counts)} categorías")
for i, (cat, count) in enumerate(category_counts.items(), 1):
    print(f"  {i}. {cat:25s} - {count:5d} muestras ({count/len(df)*100:5.2f}%)")

print(f"\n🎯 Opciones para tu proyecto:")

# Categorías negativas
negative_categories = []
positive_categories = []
neutral_categories = []

for cat in category_counts.index:
    cat_lower = cat.lower()
    if any(word in cat_lower for word in ['anxiety', 'depression', 'stress', 'suicidal', 'bipolar', 'personality']):
        negative_categories.append(cat)
    elif any(word in cat_lower for word in ['normal', 'healthy', 'positive']):
        positive_categories.append(cat)
    else:
        neutral_categories.append(cat)

print(f"\n🔴 Categorías NEGATIVAS detectadas ({len(negative_categories)}):")
for cat in negative_categories:
    print(f"  - {cat} ({category_counts[cat]} muestras)")

print(f"\n🟢 Categorías POSITIVAS/NORMALES detectadas ({len(positive_categories)}):")
for cat in positive_categories:
    print(f"  - {cat} ({category_counts[cat]} muestras)")

if len(neutral_categories) > 0:
    print(f"\n🟡 Otras categorías ({len(neutral_categories)}):")
    for cat in neutral_categories:
        print(f"  - {cat} ({category_counts[cat]} muestras)")

print(f"\n📌 SUGERENCIAS:")
print(f"\n  Opción 1️⃣ - Solo estados negativos (proyecto original):")
print(f"    Mantener: {', '.join(negative_categories[:4])}")
total_negative = sum(category_counts[cat] for cat in negative_categories[:4] if cat in category_counts)
print(f"    Total de muestras: {total_negative}")

print(f"\n  Opción 2️⃣ - Incluir estados positivos (RECOMENDADO para balance):")
neg_list = negative_categories[:4] if len(negative_categories) >= 4 else negative_categories
pos_list = positive_categories[:1] if len(positive_categories) >= 1 else []
print(f"    Mantener: {', '.join(neg_list + pos_list)}")
total_balanced = sum(category_counts[cat] for cat in (neg_list + pos_list) if cat in category_counts)
print(f"    Total de muestras: {total_balanced}")
print(f"    Ventaja: Modelo más robusto que distingue entre estados problemáticos y normales")

print(f"\n  Opción 3️⃣ - Binario (Normal vs Problemas):")
print(f"    Clase 1: Normal/Healthy")
print(f"    Clase 2: Cualquier condición negativa")
print(f"    Ventaja: Simplicidad, bueno para screening inicial")

# ================================
# 7. GUARDAR ANÁLISIS
# ================================
print(f"\n" + "="*70)
print("💾 GUARDANDO ANÁLISIS")
print("="*70)

# Guardar CSV con resumen
summary_df.to_csv('dataset_categories_summary.csv', index=False)
print(f"\n✅ Resumen guardado en 'dataset_categories_summary.csv'")

# Guardar reporte completo
with open('dataset_analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write("ANÁLISIS COMPLETO DEL DATASET DE SALUD MENTAL\n")
    f.write("="*70 + "\n\n")
    f.write(f"Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Dataset: {DATASET_PATH}\n")
    f.write(f"Total de muestras: {len(df)}\n")
    f.write(f"Total de categorías: {len(category_counts)}\n\n")
    f.write("DISTRIBUCIÓN DE CATEGORÍAS:\n")
    f.write(summary_df.to_string(index=False))
    f.write("\n\n")
    f.write("CATEGORÍAS NEGATIVAS:\n")
    for cat in negative_categories:
        f.write(f"  - {cat} ({category_counts[cat]} muestras)\n")
    f.write("\n")
    f.write("CATEGORÍAS POSITIVAS/NORMALES:\n")
    for cat in positive_categories:
        f.write(f"  - {cat} ({category_counts[cat]} muestras)\n")

print(f"✅ Reporte completo guardado en 'dataset_analysis_report.txt'")

print(f"\n" + "="*70)
print("🎉 ANÁLISIS COMPLETADO")
print("="*70)
print(f"\n📊 Revisa los archivos generados:")
print(f"  1. dataset_analysis.png")
print(f"  2. text_length_analysis.png")
print(f"  3. dataset_categories_summary.csv")
print(f"  4. dataset_analysis_report.txt")
print(f"\n💡 Siguiente paso: Decide qué categorías mantener y ejecuta clean_and_filter_dataset.py")