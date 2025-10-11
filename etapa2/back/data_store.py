import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "data"))
STORE_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "retrain_models", "training_store.parquet"))

DEFAULT_SOURCES = [
    os.path.join(DATA_DIR, "Datos_proyecto.xlsx"),
    os.path.join(DATA_DIR, "Datos_etapa 2.xlsx"),
]

def _read_any(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    if ext == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Formato no soportado: {ext}")

def load_sources(paths=None) -> pd.DataFrame:
    dfs = []
    for p in (paths or DEFAULT_SOURCES):
        if os.path.isfile(p):
            df = _read_any(p)
            if {"textos", "labels"}.issubset(df.columns):
                dfs.append(df[["textos", "labels"]])
    if not dfs:
        raise FileNotFoundError("No se encontraron fuentes base en data/")
    return pd.concat(dfs, ignore_index=True)

def read_store() -> pd.DataFrame:
    if os.path.isfile(STORE_PATH):
        return pd.read_parquet(STORE_PATH)
    return load_sources()

def write_store(df: pd.DataFrame):
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    df.to_parquet(STORE_PATH, index=False)
