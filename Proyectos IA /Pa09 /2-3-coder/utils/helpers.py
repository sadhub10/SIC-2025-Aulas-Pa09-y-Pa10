import os
import csv
from datetime import datetime
from pathlib import Path

def ensure_records_file(path):
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            f.write('timestamp,source,filename,class,confidence\n')

def append_record(path, source, filename, class_name, confidence):
    ensure_records_file(path)
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, source, filename, class_name, f"{confidence:.4f}"])
