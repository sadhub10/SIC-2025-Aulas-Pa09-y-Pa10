import os
from pathlib import Path

def project_root():
    return Path(__file__).resolve().parents[1]

def read_config(path="config.yaml"):
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)
