## Sistema de Visión Artificial para Reconocimiento de Objetos Cotidianos

Herramienta simple para detectar objetos con la cámara web usando YOLOv8. Muestra cajas, clase, confianza y FPS en vivo.

## Características
- Funciona en tiempo real con cámara web.
- Modelos incluidos: `yolov8n.pt` (rápido) y `yolov8m.pt` (más preciso).
- Ajustes por CLI: confianza, IoU, tamaño de imagen, dispositivo (`cpu`/`cuda`), salto de frames y modo rápido.
- Auto-detección de GPU si está disponible; si no, usa CPU.

## Requisitos
- Python 3.8+
- Cámara web operativa
- Librerías: `opencv-python`, `ultralytics`.

Instalación rápida:
```bash
pip install opencv-python ultralytics
```

## Archivos principales
- [camara.py](camara.py): script de detección.
- [yolov8n.pt](yolov8n.pt) y [yolov8m.pt](yolov8m.pt): pesos listos para usar.

## Uso básico
Desde la carpeta del proyecto:
```bash
python camara.py
```

## Cómo correrlo paso a paso
1) Clona o descarga este repo en una carpeta local.
2) Instala dependencias (ideal en un entorno virtual):
```bash
pip install opencv-python ultralytics
```
3) Asegúrate de tener los pesos en la raíz: [yolov8n.pt](yolov8n.pt) o [yolov8m.pt](yolov8m.pt).
4) Ejecuta el script (usa este modelo para que la cámara vaya fluida):
```bash
python camara.py --fast
```
5) Presiona Q para salir de la ventana de video.

## Ejemplos rápidos
- Modo rápido: `python camara.py --fast`

## Controles en ventana
- Q: salir

## Problemas comunes
- No abre la cámara: cierra otras apps que la usen o prueba con `cv2.VideoCapture(1)`.


