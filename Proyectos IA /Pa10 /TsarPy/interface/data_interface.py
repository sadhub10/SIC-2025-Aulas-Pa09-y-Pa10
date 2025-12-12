from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QTextEdit, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
import json
import os

class DataInterface(QWidget):
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

        titulo = QLabel("Visualizar Datos Guardados")
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

        btn_layout = QHBoxLayout()

        self.btn_cargar = QPushButton("Actualizar Datos")
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
        self.btn_cargar.clicked.connect(self.cargar_datos)
        btn_layout.addWidget(self.btn_cargar)

        self.btn_limpiar = QPushButton("Limpiar Datos")
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #C62828;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        self.btn_limpiar.clicked.connect(self.limpiar_datos)
        btn_layout.addWidget(self.btn_limpiar)

        layout.addLayout(btn_layout)

        self.label_info = QLabel("Sin datos cargados")
        self.label_info.setAlignment(Qt.AlignCenter)
        self.label_info.setStyleSheet("""
            font-size: 13px; 
            padding: 12px; 
            color: #424242;
            background-color: white;
            border: 2px solid #BDBDBD;
            border-radius: 3px;
            font-weight: bold;
        """)
        layout.addWidget(self.label_info)

        self.text_datos = QTextEdit()
        self.text_datos.setReadOnly(True)
        self.text_datos.setPlaceholderText("Los datos del archivo data.json aparecerán aquí...")
        self.text_datos.setStyleSheet("""
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
        layout.addWidget(self.text_datos)

        layout.addStretch()
        self.setLayout(layout)

        self.cargar_datos()

    def cargar_datos(self):
        try:
            if not os.path.exists("data.json"):
                self.label_info.setText("El archivo data.json no existe aún")
                self.label_info.setStyleSheet("""
                    font-size: 13px; 
                    padding: 12px; 
                    color: #E65100;
                    background-color: #FFE0B2;
                    border: 2px solid #FF9800;
                    border-radius: 3px;
                    font-weight: bold;
                """)
                self.text_datos.clear()
                self.text_datos.setPlaceholderText("No hay datos guardados. Procese alguna fuente de datos primero.")
                return

            with open("data.json", "r", encoding="utf-8") as f:
                datos = json.load(f)

            if "extracciones" in datos and len(datos["extracciones"]) > 0:
                num_extracciones = len(datos["extracciones"])
                self.label_info.setText(f"Total de extracciones: {num_extracciones}")
                self.label_info.setStyleSheet("""
                    font-size: 13px; 
                    padding: 12px; 
                    color: #1B5E20;
                    background-color: #C8E6C9;
                    border: 2px solid #4CAF50;
                    border-radius: 3px;
                    font-weight: bold;
                """)
            else:
                self.label_info.setText("No hay extracciones registradas")
                self.label_info.setStyleSheet("""
                    font-size: 13px; 
                    padding: 12px; 
                    color: #424242;
                    background-color: white;
                    border: 2px solid #BDBDBD;
                    border-radius: 3px;
                    font-weight: bold;
                """)

            self.text_datos.clear()
            self.text_datos.setPlainText(json.dumps(datos, indent=2, ensure_ascii=False))

        except Exception as e:
            self.label_info.setText("Error al cargar datos")
            self.label_info.setStyleSheet("""
                font-size: 13px; 
                padding: 12px; 
                color: #FFFFFF;
                background-color: #C62828;
                border: 2px solid #B71C1C;
                border-radius: 3px;
                font-weight: bold;
            """)
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")

    def limpiar_datos(self):
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar todos los datos guardados?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if os.path.exists("data.json"):
                    os.remove("data.json")

                self.text_datos.clear()
                self.label_info.setText("Datos eliminados correctamente")
                self.label_info.setStyleSheet("""
                    font-size: 13px; 
                    padding: 12px; 
                    color: #E65100;
                    background-color: #FFE0B2;
                    border: 2px solid #FF9800;
                    border-radius: 3px;
                    font-weight: bold;
                """)
                QMessageBox.information(self, "Éxito", "Todos los datos han sido eliminados correctamente")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar datos: {str(e)}")
