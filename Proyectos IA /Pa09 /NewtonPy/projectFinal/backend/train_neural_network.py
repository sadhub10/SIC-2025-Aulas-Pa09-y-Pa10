#!/usr/bin/env python3
"""
Script para entrenar la red neuronal del clasificador de CSV
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.neural_classifier import CSVNeuralClassifier
import matplotlib.pyplot as plt

def main():

    
    # Crear instancia del clasificador
    classifier = CSVNeuralClassifier()
    
    # Preguntar número de muestras
    try:
        n_samples = int(input("¿Cuántas muestras generar para entrenamiento? [1000]: ") or "1000")
    except ValueError:
        n_samples = 1000
    
    print(f"\nGenerando {n_samples} muestras sintéticas...")
    print("   Categorías: financial, sales, hr, inventory, operations, performance")
    print()
    
    # Entrenar
    history = classifier.train_with_synthetic_data(n_samples=n_samples)
    
    # Mostrar resultados
    print("\n" + "="*60)
    print("ENTRENAMIENTO COMPLETADO")
    print("="*60)
    print(f"Precisión final (train): {history.history['accuracy'][-1]:.2%}")
    print(f"Precisión validación:    {history.history['val_accuracy'][-1]:.2%}")
    print(f"Loss final:              {history.history['loss'][-1]:.4f}")
    print(f"Val loss:                {history.history['val_loss'][-1]:.4f}")
    print()
    print("Modelo guardado en: ml_models/csv_classifier.keras")
    print()
    
    # Graficar resultados (opcional)
    try:
        plot_training = input("\n¿Quieres ver gráficos del entrenamiento? (s/n) [n]: ").lower() == 's'
        
        if plot_training:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Accuracy
            ax1.plot(history.history['accuracy'], label='Train')
            ax1.plot(history.history['val_accuracy'], label='Validation')
            ax1.set_title('Model Accuracy')
            ax1.set_ylabel('Accuracy')
            ax1.set_xlabel('Epoch')
            ax1.legend()
            ax1.grid(True)
            
            # Loss
            ax2.plot(history.history['loss'], label='Train')
            ax2.plot(history.history['val_loss'], label='Validation')
            ax2.set_title('Model Loss')
            ax2.set_ylabel('Loss')
            ax2.set_xlabel('Epoch')
            ax2.legend()
            ax2.grid(True)
            
            plt.tight_layout()
            plt.savefig('training_history.png')
            print("Gráficos guardados en: training_history.png")
            plt.show()
    except:
        pass

if __name__ == '__main__':
    main()
