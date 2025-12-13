import time
import argparse
try:
    import cv2
except Exception:
    print("Faltan dependencias. Instala con: pip install -r requirements.txt")
    raise

try:
    from ultralytics import YOLO
except Exception:
    print("La librería 'ultralytics' no está instalada. Instala con: pip install ultralytics")
    raise


def run_object_detector(model_path: str = 'yolov8m.pt', conf: float = 0.45, iou: float = 0.45, imgsz: int = 1280, device: str = None):
    """Ejecuta detección de objetos usando YOLOv8 en la cámara.

    """
    # Auto-detección de device si no se pasa explícitamente
    if device is None:
        try:
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        except Exception:
            device = 'cpu'

    print(f'cargando modelo {model_path} en device={device} (conf={conf}, iou={iou}, imgsz={imgsz})')
    model = YOLO(model_path)

    # Abrir cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError('No se pudo abrir la cámara. Asegúrate de que esté conectada.')

    prev_time = 0
    frame_idx = 0
    last_boxes = []
    last_names = []
    last_confs = []
    last_classes = []

    # Default behaviour: keep showing boxes from last inference until next one
    while True:
        ret, frame = cap.read()
        if not ret:
            print('No se pudo leer frame desde la cámara.')
            break

        frame = cv2.flip(frame, 1)
        display = frame.copy()

        # Decide whether to run inference on this frame: allow caller to change skip via args later
        run_inference = True
        if hasattr(run_object_detector, 'frame_skip') and run_object_detector.frame_skip > 0:
            run_inference = (frame_idx % (run_object_detector.frame_skip + 1) == 0)

        if run_inference:
            try:
                # Ejecutar la inferencia con parámetros (model maneja resize interno)
                results = model(frame, imgsz=imgsz, conf=conf, iou=iou, device=device)[0]

                names = results.names if hasattr(results, 'names') else model.names

                boxes_xyxy = []
                confs = []
                classes = []
                if hasattr(results, 'boxes') and results.boxes is not None and len(results.boxes) > 0:
                    try:
                        boxes_xyxy = results.boxes.xyxy.cpu().numpy()
                        confs = results.boxes.conf.cpu().numpy()
                        classes = results.boxes.cls.cpu().numpy().astype(int)
                    except Exception:
                        for b in results.boxes:
                            try:
                                xy = b.xyxy[0].numpy()
                            except Exception:
                                xy = b.xyxy[0]
                            boxes_xyxy.append(xy)
                            try:
                                confs.append(float(b.conf[0]))
                            except Exception:
                                confs.append(float(b.conf))
                            try:
                                classes.append(int(b.cls[0]))
                            except Exception:
                                classes.append(int(b.cls))

                # Store last detection
                last_boxes = boxes_xyxy
                last_confs = confs
                last_names = names
                last_classes = classes

            except Exception:
                cv2.putText(display, 'Error al ejecutar el detector', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Dibujar cajas (últimas detecciones disponibles)
        try:
            for i, box in enumerate(last_boxes):
                x1, y1, x2, y2 = map(int, box)
                c = last_confs[i] if i < len(last_confs) else 0.0
                cls = last_classes[i] if i < len(last_classes) else -1
                if isinstance(last_names, (list, dict)) and cls >= 0 and cls < len(last_names):
                    label_text = f"{last_names[cls]} {c:.2f}"
                else:
                    label_text = f"{c:.2f}"

                thickness = max(1, int(display.shape[1] / 640))
                cv2.rectangle(display, (x1, y1), (x2, y2), (14, 140, 255), thickness)
                t_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(display, (x1, y1 - t_size[1] - 6), (x1 + t_size[0] + 6, y1), (14, 140, 255), -1)
                cv2.putText(display, label_text, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        except Exception:
            pass

        # FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        cv2.putText(display, f'FPS: {int(fps)}', (10, display.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow('Camara - Detección objetos (preciso)', display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Camara: detección de objetos (modo único, orientado a precisión)')
    parser.add_argument('--model', default='yolov8m.pt', help="Modelo YOLOv8 a usar (ej. 'yolov8n.pt','yolov8m.pt','yolov8l.pt')")
    parser.add_argument('--conf', type=float, default=0.45, help='Umbral de confianza (0-1). Aumenta para mayor precisión.')
    parser.add_argument('--iou', type=float, default=0.45, help='Umbral de IoU para NMS.')
    parser.add_argument('--imgsz', type=int, default=1280, help='Tamaño de imagen para inferencia (mayor -> más preciso y lento).')
    parser.add_argument('--device', default=None, help="'cpu' o 'cuda' (por defecto intenta detectar CUDA)")
    parser.add_argument('--skip', type=int, default=0, help='Número de frames a saltar entre inferencias (0 = todos los frames, 1 = procesar cada 2º frame).')
    parser.add_argument('--fast', action='store_true', help='Modo rápido: usa modelo pequeño y ajustes rápidos por defecto.')
    args = parser.parse_args()

    # Si piden modo rápido, ajustar parámetros para rendimiento
    if args.fast:
        if args.model == 'yolov8m.pt':
            args.model = 'yolov8n.pt'
        if args.imgsz == 1280:
            args.imgsz = 640
        if args.conf == 0.45:
            args.conf = 0.25

    # Attach frame_skip to function so the detector loop can use it
    run_object_detector.frame_skip = max(0, args.skip)

    run_object_detector(model_path=args.model, conf=args.conf, iou=args.iou, imgsz=args.imgsz, device=args.device)