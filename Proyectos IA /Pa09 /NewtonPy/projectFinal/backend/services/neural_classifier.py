import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from scipy import stats
from tensorflow.keras.utils import to_categorical
import re
import os

class CSVNeuralClassifier:
    """
    Red Neuronal para clasificar tipos de archivos CSV
    Usa características extraídas del CSV para predecir su categoría
    """
    
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Categorías que puede detectar
        self.categories = ['financial', 'sales', 'hr', 'inventory', 'operations', 'performance']
        
        # Intentar cargar modelo pre-entrenado
        self._load_model()
    
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extrae características numéricas del DataFrame para la red neuronal
        """
        features = []
        
        # 1. Características básicas
        features.append(len(df))  # número de filas
        features.append(len(df.columns))  # número de columnas
        features.append(df.isnull().sum().sum() / (len(df) * len(df.columns)))  # % nulls
        
        # 2. Tipos de datos
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        text_cols = df.select_dtypes(include=['object']).columns
        
        features.append(len(numeric_cols) / len(df.columns))  # % columnas numéricas
        features.append(len(text_cols) / len(df.columns))  # % columnas texto
        
        # 3. Características de columnas numéricas
        if len(numeric_cols) > 0:
            features.append(df[numeric_cols].mean().mean())  # media de medias
            features.append(df[numeric_cols].std().mean())  # media de desviaciones
            features.append(df[numeric_cols].min().min())  # mínimo global
            features.append(df[numeric_cols].max().max())  # máximo global
        else:
            features.extend([0, 0, 0, 0])
        
        # 4. Características de texto (palabras clave)
        columns_text = ' '.join([str(col).lower() for col in df.columns])
        
        # Palabras clave financieras
        financial_keywords = ['price', 'cost', 'expense', 'revenue', 'payment', 'gasto', 'precio', 'pago']
        features.append(sum(1 for kw in financial_keywords if kw in columns_text))
        
        # Palabras clave de ventas
        sales_keywords = ['sales', 'sold', 'customer', 'order', 'ventas', 'cliente', 'pedido']
        features.append(sum(1 for kw in sales_keywords if kw in columns_text))
        
        # Palabras clave de RR.HH.
        hr_keywords = ['employee', 'salary', 'department', 'empleado', 'salario', 'departamento']
        features.append(sum(1 for kw in hr_keywords if kw in columns_text))
        
        # Palabras clave de inventario
        inventory_keywords = ['stock', 'inventory', 'warehouse', 'inventario', 'almacen']
        features.append(sum(1 for kw in inventory_keywords if kw in columns_text))
        
        # Palabras clave de operaciones
        operations_keywords = ['operation', 'process', 'project', 'operacion', 'proceso', 'proyecto']
        features.append(sum(1 for kw in operations_keywords if kw in columns_text))
        
        # Palabras clave de rendimiento
        performance_keywords = ['performance', 'metrics', 'kpi', 'efficiency', 'rendimiento']
        features.append(sum(1 for kw in performance_keywords if kw in columns_text))
        
        # 5. Patrones en los datos
        # Detectar si hay columnas de fecha
        date_keywords = ['date', 'time', 'fecha', 'hora', 'timestamp']
        has_dates = any(kw in columns_text for kw in date_keywords)
        features.append(1 if has_dates else 0)
        
        # Detectar si hay IDs
        id_keywords = ['id', 'code', 'codigo']
        has_ids = any(kw in columns_text for kw in id_keywords)
        features.append(1 if has_ids else 0)
        
        # 6. Distribución de valores únicos
        if len(df.columns) > 0:
            unique_ratios = [df[col].nunique() / len(df) for col in df.columns if len(df) > 0]
            features.append(np.mean(unique_ratios) if unique_ratios else 0)
            features.append(np.std(unique_ratios) if len(unique_ratios) > 1 else 0)
        else:
            features.extend([0, 0])
        
        return np.array(features).reshape(1, -1)
    
    def build_model(self, input_dim, num_classes):
        """Construye la arquitectura de la red neuronal"""
        model = Sequential([
            Dense(64, activation='relu', input_shape=(input_dim,)),
            Dropout(0.5),
            Dense(32, activation='relu'),
            Dense(num_classes, activation='softmax')
        ])
        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        self.model = model
        return model
    
    def train_with_synthetic_data(self, n_samples=1000):
        X = np.random.rand(n_samples, 10)
        y = np.random.randint(0, 6, size=n_samples)

        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        y = to_categorical(y, num_classes=6)

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)

        model = self.build_model(input_dim=X.shape[1], num_classes=6)
        history = model.fit(X_train, y_train,
                            validation_data=(X_val, y_val),
                            epochs=20,
                            batch_size=32,
                            verbose=1)

        os.makedirs("ml_models", exist_ok=True)
        model.save("ml_models/csv_classifier.keras")

        return history
    
    def _generate_synthetic_features(self, category: str) -> np.ndarray:
        """
        Genera características sintéticas para una categoría específica
        """
        features = []
        
        # Características básicas (aleatorias dentro de rangos típicos)
        features.append(np.random.randint(100, 10000))  # filas
        features.append(np.random.randint(5, 30))  # columnas
        features.append(np.random.uniform(0, 0.1))  # % nulls
        
        # % columnas numéricas y texto
        if category in ['financial', 'sales', 'performance']:
            features.append(np.random.uniform(0.4, 0.8))  # más numéricas
            features.append(np.random.uniform(0.2, 0.6))  # menos texto
        else:
            features.append(np.random.uniform(0.2, 0.5))
            features.append(np.random.uniform(0.5, 0.8))
        
        # Estadísticas numéricas
        features.append(np.random.uniform(100, 10000))  # media
        features.append(np.random.uniform(50, 5000))  # std
        features.append(np.random.uniform(0, 100))  # min
        features.append(np.random.uniform(1000, 100000))  # max
        
        # Palabras clave (más frecuentes para su categoría)
        keyword_counts = [0] * 6  # 6 categorías
        category_idx = self.categories.index(category)
        keyword_counts[category_idx] = np.random.randint(2, 8)
        
        # Agregar algo de ruido en otras categorías
        for i in range(6):
            if i != category_idx:
                keyword_counts[i] = np.random.randint(0, 2)
        
        features.extend(keyword_counts)
        
        # Patrones
        features.append(1 if np.random.random() > 0.3 else 0)  # has_dates
        features.append(1 if np.random.random() > 0.5 else 0)  # has_ids
        
        # Distribución de valores únicos
        features.append(np.random.uniform(0.1, 0.9))  # mean unique ratio
        features.append(np.random.uniform(0.05, 0.3))  # std unique ratio
        
        return np.array(features)
    
    def predict(self, df: pd.DataFrame) -> dict:
        """
        Predice la categoría de un CSV usando la red neuronal
        """
        if not self.is_trained:
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'all_probabilities': {},
                'method': 'fallback'
            }
        
        try:
            # Extraer características
            features = self._extract_features(df)
            
            # Normalizar
            features_scaled = self.scaler.transform(features)
            
            # Predecir
            predictions = self.model.predict(features_scaled, verbose=0)
            predicted_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_idx])
            
            # Crear diccionario de probabilidades
            all_probs = {
                category: float(prob) 
                for category, prob in zip(self.categories, predictions[0])
            }
            
            return {
                'category': self.categories[predicted_idx],
                'confidence': confidence,
                'all_probabilities': all_probs,
                'method': 'neural_network'
            }
            
        except Exception as e:
            print(f"Error en predicción: {e}")
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'all_probabilities': {},
                'method': 'error',
                'error': str(e)
            }
    
    def _save_model(self):
        """Guarda el modelo y sus componentes"""
        model_dir = 'ml_models'
        os.makedirs(model_dir, exist_ok=True)
        
        # Guardar modelo de Keras
        self.model.save(os.path.join(model_dir, 'csv_classifier.keras'))
        
        # Guardar scaler
        with open(os.path.join(model_dir, 'scaler.pkl'), 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Guardar metadata
        metadata = {
            'categories': self.categories,
            'is_trained': self.is_trained
        }
        with open(os.path.join(model_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
    
    def _load_model(self):
        """Carga el modelo si existe"""
        model_dir = 'ml_models'
        model_path = os.path.join(model_dir, 'csv_classifier.keras')
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        metadata_path = os.path.join(model_dir, 'metadata.json')
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                self.model = keras.models.load_model(model_path)
                
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        self.categories = metadata.get('categories', self.categories)
                        self.is_trained = metadata.get('is_trained', True)
                
                print("✓ Modelo pre-entrenado cargado exitosamente")
                
            except Exception as e:
                print(f"No se pudo cargar el modelo: {e}")
                self.is_trained = False
