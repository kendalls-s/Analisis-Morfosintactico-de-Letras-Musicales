import pandas as pd
from pathlib import Path

def carga_original():
    """Carga del corpus linguistico original en csv"""
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_PATH = BASE_DIR / "data" / "raw" / "lyrics_dataset.csv"
    return pd.read_csv(DATA_PATH)

def carga_limpios():
    """Carga del corpus linguistico limpio en csv"""
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_PATH = BASE_DIR / "data" / "processed" / "lyrics_clean.csv"
    return pd.read_csv(DATA_PATH)