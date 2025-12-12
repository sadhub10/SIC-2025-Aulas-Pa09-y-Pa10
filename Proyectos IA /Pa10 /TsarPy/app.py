import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from interface.img_interface import ImageInterface
from interface.doc_interface import DocumentInterface
from interface.audio_interface import AudioInterface
from interface.data_interface import DataInterface

class OptiMaxApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("OptiMax - Sistema de Extracción de Datos")
        self.setMinimumSize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        panel_izquierdo = self.crear_panel_izquierdo()
        main_layout.addWidget(panel_izquierdo, 1)

        self.stack_contenido = QStackedWidget()
        self.stack_contenido.setStyleSheet("background-color: white;")

        self.imagen_interface = ImageInterface()
        self.documento_interface = DocumentInterface()
        self.audio_interface = AudioInterface()
        self.datos_interface = DataInterface()

        self.stack_contenido.addWidget(self.imagen_interface)
        self.stack_contenido.addWidget(self.documento_interface)
        self.stack_contenido.addWidget(self.audio_interface)
        self.stack_contenido.addWidget(self.datos_interface)

        main_layout.addWidget(self.stack_contenido, 4)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #E3F2FD;
            }
        """)

    def crear_panel_izquierdo(self):
        panel = QWidget()
        panel.setMaximumWidth(250)
        panel.setStyleSheet("""
            QWidget {
                background-color: #1976D2;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        titulo = QLabel("OptiMax")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                background-color: #0D47A1;
                color: white;
                font-size: 32px;
                font-weight: bold;
                padding: 30px;
                letter-spacing: 2px;
            }
        """)
        layout.addWidget(titulo)

        subtitulo = QLabel("Sistema de Extracción")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("""
            QLabel {
                background-color: #1565C0;
                color: white;
                font-size: 13px;
                padding: 12px;
                font-weight: bold;
            }
        """)
        layout.addWidget(subtitulo)

        layout.addSpacing(20)

        seccion_fuentes = QLabel("FUENTES DE DATOS")
        seccion_fuentes.setAlignment(Qt.AlignCenter)
        seccion_fuentes.setStyleSheet("""
            QLabel {
                color: #E3F2FD;
                font-size: 12px;
                font-weight: bold;
                padding: 15px 10px 10px 10px;
                letter-spacing: 1px;
            }
        """)
        layout.addWidget(seccion_fuentes)

        self.btn_imagen = self.crear_boton_menu("Imagen", 0)
        layout.addWidget(self.btn_imagen)

        self.btn_documento = self.crear_boton_menu("Documento", 1)
        layout.addWidget(self.btn_documento)

        self.btn_audio = self.crear_boton_menu("Audio", 2)
        layout.addWidget(self.btn_audio)

        layout.addSpacing(20)

        seccion_visualizacion = QLabel("VISUALIZACIÓN")
        seccion_visualizacion.setAlignment(Qt.AlignCenter)
        seccion_visualizacion.setStyleSheet("""
            QLabel {
                color: #E3F2FD;
                font-size: 12px;
                font-weight: bold;
                padding: 15px 10px 10px 10px;
                letter-spacing: 1px;
            }
        """)
        layout.addWidget(seccion_visualizacion)

        self.btn_datos = self.crear_boton_menu("Datos Guardados", 3)
        layout.addWidget(self.btn_datos)

        layout.addStretch()

        footer = QLabel("v1.0")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                color: #64B5F6;
                font-size: 10px;
                padding: 15px;
            }
        """)
        layout.addWidget(footer)

        panel.setLayout(layout)
        return panel

    def crear_boton_menu(self, texto, indice):
        btn = QPushButton(texto)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 15px 20px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn.clicked.connect(lambda checked, idx=indice: self.cambiar_vista(idx))
        return btn

    def cambiar_vista(self, indice):
        self.stack_contenido.setCurrentIndex(indice)

        if indice == 3:
            self.datos_interface.cargar_datos()

def main():
    # Fix para Wayland en Arch Linux
    os.environ['QT_QPA_PLATFORM'] = 'wayland'
    os.environ['QT_QPA_PLATFORMTHEME'] = 'qt5ct'

    # Si hay problemas con Wayland, usar XWayland
    if 'WAYLAND_DISPLAY' in os.environ:
        try:
            app = QApplication(sys.argv)
        except Exception:
            os.environ['QT_QPA_PLATFORM'] = 'xcb'
            app = QApplication(sys.argv)
    else:
        app = QApplication(sys.argv)

    font = QFont("Arial", 10)
    app.setFont(font)

    ventana = OptiMaxApp()
    ventana.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
