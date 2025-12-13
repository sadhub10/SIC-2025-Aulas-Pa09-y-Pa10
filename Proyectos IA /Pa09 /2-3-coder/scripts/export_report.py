import pandas as pd
import sys
from pathlib import Path

def aggregate(csv_path):
    df = pd.read_csv(csv_path)
    counts = df['class'].value_counts().reset_index()
    counts.columns = ['class', 'count']
    return counts

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python export_report.py path/to/records.csv')
        sys.exit(1)
    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print('CSV not found:', csv_path)
        sys.exit(1)
    print(aggregate(csv_path).to_csv(index=False))
