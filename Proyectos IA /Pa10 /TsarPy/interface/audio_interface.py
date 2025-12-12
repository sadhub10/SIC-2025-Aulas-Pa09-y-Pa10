from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import json
import os
from vosk import Model, KaldiRecognizer
import pyaudio

from tools.data_extraction import extract_key_values
from config.keywords import keywords_list

MODEL_PATH = "tools/audio/vosk-model-small-es-0.42"
SAMPLE_RATE = 16000
CHUNK_SIZE = 4096

KEYWORDS_FOR_EXTRACTION = ["sub", "impuesto", "total", "venta"]

grammar = KEYWORDS_FOR_EXTRACTION + [
    "[unk]",
    "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
    "punto", "coma"
]
grammar_json = json.dumps(grammar)

digit_map = {
    "cero": "0", "uno": "1", "dos": "2", "tres": "3", "cuatro": "4",
    "cinco": "5", "seis": "6", "siete": "7", "ocho": "8", "nueve": "9",
    "punto": ".", "coma": "."
}

def format_transcription(result_text: str) -> str:
    split_words = result_text.split()
    formatted_text = ""
    for word in split_words:
        formatted_text += digit_map.get(word, f" {word} ") 
    return formatted_text.strip()

class AudioTranscriptionThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    segment_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        model_path = MODEL_PATH

        if not os.path.exists(model_path):
            self.error.emit(f"Modelo Vosk no encontrado en {model_path}")
            return

        p = None
        stream = None
        full_transcription = []

        try:
            model = Model(model_path)
            recognizer = KaldiRecognizer(model, SAMPLE_RATE)
            recognizer.SetGrammar(grammar_json)

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=SAMPLE_RATE,
                            input=True,
                            frames_per_buffer=CHUNK_SIZE)

            while self._is_running:
                try:
                    data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    if not data:
                        break

                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        result_text = result.get("text", "")

                        if result_text:
                            formatted_text = format_transcription(result_text)
                            self.segment_received.emit(formatted_text)
                            full_transcription.extend(formatted_text.lower().split())
                except Exception:
                    if not self._is_running:
                        break

        except Exception as e:
            self.error.emit(str(e))
            return
        finally:
            if 'recognizer' in locals():
                try:
                    final_result = json.loads(recognizer.FinalResult())
                    if final_result.get("text"):
                        formatted_cleanup = format_transcription(final_result['text'])
                        full_transcription.extend(formatted_cleanup.lower().split())
                except:
                    pass

            if stream and stream.is_active():
                stream.stop_stream()
                stream.close()
            if p:
                p.terminate()

        self.finished.emit(full_transcription)

class AudioInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.thread = None

    def init_ui(self):
        layout = QVBoxLayout()

        self.setStyleSheet("""
            QWidget {
                background-color: #515151;
            }
        """)

        titulo = QLabel("Audio")
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

        self.label_estado = QLabel("Listo para grabar")
        self.label_estado.setAlignment(Qt.AlignCenter)
        self.label_estado.setStyleSheet("""
            font-size: 14px; 
            padding: 12px; 
            color: #424242;
            background-color: white;
            border: 2px solid #BDBDBD;
            border-radius: 3px;
            font-weight: bold;
        """)
        layout.addWidget(self.label_estado)

        self.btn_grabar = QPushButton("Iniciar Grabación")
        self.btn_grabar.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 15px;
                border-radius: 5px;
                font-size: 15px;
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
        self.btn_grabar.clicked.connect(self.toggle_grabacion)
        layout.addWidget(self.btn_grabar)

        self.text_resultado = QTextEdit()
        self.text_resultado.setReadOnly(True)
        self.text_resultado.setPlaceholderText("La transcripción aparecerá aquí...")
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
        self.btn_procesar.clicked.connect(self.procesar_audio)
        self.btn_procesar.setEnabled(False)
        layout.addWidget(self.btn_procesar)

        layout.addStretch()
        self.setLayout(layout)

        self.tokens_audio = []
        self.grabando = False

    def toggle_grabacion(self):
        if not self.grabando:
            self.iniciar_grabacion()
        else:
            self.detener_grabacion()

    def iniciar_grabacion(self):
        self.grabando = True
        self.label_estado.setText("GRABANDO... Hable ahora")
        self.label_estado.setStyleSheet("""
            font-size: 14px; 
            padding: 12px; 
            color: #FFFFFF;
            background-color: #C62828;
            border: 2px solid #B71C1C;
            border-radius: 3px;
            font-weight: bold;
        """)
        self.btn_grabar.setText("Detener Grabación")
        self.btn_grabar.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                padding: 15px;
                border-radius: 5px;
                font-size: 15px;
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
        self.text_resultado.clear()
        self.btn_procesar.setEnabled(False)

        self.thread = AudioTranscriptionThread()
        self.thread.finished.connect(self.on_transcription_finished)
        self.thread.error.connect(self.on_transcription_error)
        self.thread.segment_received.connect(self.on_segment_received)
        self.thread.start()

    def detener_grabacion(self):
        if self.thread:
            self.thread.stop()
            self.label_estado.setText("Deteniendo grabación...")
            self.label_estado.setStyleSheet("""
                font-size: 14px; 
                padding: 12px; 
                color: #424242;
                background-color: #FFF9C4;
                border: 2px solid #FBC02D;
                border-radius: 3px;
                font-weight: bold;
            """)
            self.btn_grabar.setEnabled(False)

    def on_segment_received(self, segment):
        self.text_resultado.append(f"Segmento: {segment}")

    def on_transcription_finished(self, tokens):
        self.grabando = False
        self.tokens_audio = tokens
        self.label_estado.setText("Grabación finalizada correctamente")
        self.label_estado.setStyleSheet("""
            font-size: 14px; 
            padding: 12px; 
            color: #1B5E20;
            background-color: #C8E6C9;
            border: 2px solid #4CAF50;
            border-radius: 3px;
            font-weight: bold;
        """)
        self.btn_grabar.setText("Iniciar Grabación")
        self.btn_grabar.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 15px;
                border-radius: 5px;
                font-size: 15px;
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
        self.btn_grabar.setEnabled(True)

        self.text_resultado.append(f"\nTotal de tokens transcritos: {len(tokens)}\n")

        if tokens:
            self.btn_procesar.setEnabled(True)

    def on_transcription_error(self, error):
        self.grabando = False
        self.label_estado.setText("Error en la grabación")
        self.label_estado.setStyleSheet("""
            font-size: 14px; 
            padding: 12px; 
            color: #FFFFFF;
            background-color: #C62828;
            border: 2px solid #B71C1C;
            border-radius: 3px;
            font-weight: bold;
        """)
        self.btn_grabar.setText("Iniciar Grabación")
        self.btn_grabar.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 15px;
                border-radius: 5px;
                font-size: 15px;
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
        self.btn_grabar.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Error al transcribir audio: {error}")

    def procesar_audio(self):
        if not self.tokens_audio:
            return

        try:
            datos_extraidos = extract_key_values(self.tokens_audio, keywords_list)

            self.text_resultado.append("\nDatos extraídos:\n")
            self.text_resultado.append(json.dumps(datos_extraidos, indent=4, ensure_ascii=False))
            self.text_resultado.append("\n")

            self.guardar_datos(datos_extraidos, "audio")

            QMessageBox.information(self, "Éxito", "Datos procesados y guardados correctamente")
            self.btn_procesar.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar audio: {str(e)}")

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
