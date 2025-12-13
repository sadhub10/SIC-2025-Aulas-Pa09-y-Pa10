from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QFileDialog, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt
import json
import os

from tools.imgocr.img_extraction import extract_text_from_image
from tools.data_extraction import extract_key_values
from config.keywords import keywords_list

class ImageInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.setStyleSheet("""
            QWidget {
                background-color: #515151;
            }
        """)

        titulo = QLabel("Imagen")
        titulo.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #0D47A1;
            padding: 15px;
            background-color: #E3F2FD;
            border-radius: 5px;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.btn_cargar = QPushButton("Cargar Imagen")
        self.btn_cargar.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.btn_cargar.clicked.connect(self.cargar_imagen)
        layout.addWidget(self.btn_cargar)

        self.label_archivo = QLabel("No se ha seleccionado ninguna imagen")
        self.label_archivo.setStyleSheet("""
            font-size: 13px; 
            padding: 10px; 
            color: #424242;
            background-color: white;
            border: 1px solid #BDBDBD;
            border-radius: 3px;
        """)
        self.label_archivo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_archivo)

        self.text_resultado = QTextEdit()
        self.text_resultado.setReadOnly(True)
        self.text_resultado.setPlaceholderText("Los resultados aparecerán aquí...")
        self.text_resultado.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #212121;
                border: 2px solid #BDBDBD;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.text_resultado)

        self.btn_procesar = QPushButton("Procesar y Guardar")
        self.btn_procesar.setStyleSheet("""
            QPushButton {
                background-color: #388E3C;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.btn_procesar.clicked.connect(self.procesar_imagen)
        self.btn_procesar.setEnabled(False)
        layout.addWidget(self.btn_procesar)

        layout.addStretch()
        self.setLayout(layout)

        self.ruta_imagen = None

    def cargar_imagen(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar Imagen", 
            "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )

        if archivo:
            self.ruta_imagen = archivo
            self.label_archivo.setText(f"Imagen: {os.path.basename(archivo)}")
            self.label_archivo.setStyleSheet("""
                font-size: 13px; 
                padding: 10px; 
                color: #1B5E20;
                background-color: #E8F5E9;
                border: 2px solid #4CAF50;
                border-radius: 3px;
                font-weight: bold;
            """)
            self.btn_procesar.setEnabled(True)

    def procesar_imagen(self):
        if not self.ruta_imagen:
            return

        try:
            self.text_resultado.clear()
            self.text_resultado.append("Extrayendo texto de la imagen...\n")
            tokens = extract_text_from_image(self.ruta_imagen)

            if not tokens:
                QMessageBox.warning(self, "Advertencia", "No se pudieron extraer datos de la imagen")
                return

            self.text_resultado.append(f"Tokens extraídos: {len(tokens)}\n")

            datos_extraidos = extract_key_values(tokens, keywords_list)

            self.text_resultado.append("Datos extraídos:\n")
            self.text_resultado.append(json.dumps(datos_extraidos, indent=4, ensure_ascii=False))
            self.text_resultado.append("\n")

            self.guardar_datos(datos_extraidos, "imagen")

            QMessageBox.information(self, "Éxito", "Datos procesados y guardados correctamente")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar imagen: {str(e)}")

    def guardar_datos(self, datos, fuente):
        try:
            if os.path.exists("data.json"):
                with open("data.json", "r", encoding="utf-8") as f:
                    data_actual = json.load(f)
            else:
                data_actual = {}

            if "extracciones" not in data_actual:
                data_actual["extracciones"] = []

            import datetime
            entrada = {
                "fuente": fuente,
                "fecha": datetime.datetime.now().isoformat(),
                "datos": datos
            }

            data_actual["extracciones"].append(entrada)

            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(data_actual, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error al guardar datos: {e}")
