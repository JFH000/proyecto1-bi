import os
import json
import time
import hashlib
from typing import Dict, Any, Tuple, List, Optional

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support

from .pipelines import build_pipeline
from .utils import clean_df

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RETRAIN_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "retrain_models"))
os.makedirs(RETRAIN_DIR, exist_ok=True)

def _save_model_with_metadata(model, metrics: Dict[str, float], extra_meta: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    ts = time.strftime("%Y%m%d_%H%M%S")
    model_path = os.path.join(RETRAIN_DIR, f"model_{ts}.pkl")
    meta_path = os.path.join(RETRAIN_DIR, f"model_{ts}.meta.json")

    joblib.dump(model, model_path)

    # hash MD5 del binario para trazabilidad
    h = hashlib.md5()
    with open(model_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)

    meta = {
        "created_at": ts,
        "model_path": model_path,
        "metrics": metrics,
        "md5": h.hexdigest(),
    }
    if extra_meta:
        meta.update(extra_meta)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return {"model_path": model_path, "meta_path": meta_path}

def retrain_from_dataframe(
    df_all: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
    pipeline_name: str = "svc_calibrated",
    keep_short_texts: bool = True,
) -> Tuple[Dict[str, float], Dict[str, str]]:
    """
    Espera un DataFrame con columnas: 'textos' (str) y 'labels' (int).
    Limpia datos, entrena, evalúa (macro) y persiste modelo + metadatos.
    Devuelve: (metrics, paths)
    """
    # Validación de esquema mínimo
    required = {"textos", "labels"}
    missing = required - set(df_all.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}. Se esperaba {sorted(required)}.")

    # Limpieza básica y tipos
    df = df_all.dropna(subset=["textos", "labels"]).copy()
    df["labels"] = df["labels"].astype(int)

    # Limpieza de texto; para API no filtramos por longitud
    df = clean_df(df, use_nltk=True, use_short_text=keep_short_texts)

    # Necesitamos al menos dos clases
    class_counts = df["labels"].value_counts().to_dict()
    if len(class_counts) < 2:
        raise ValueError("Se requieren al menos 2 clases para reentrenar.")

    X = df["textos"].values
    y = df["labels"].values

    # Estratificación si todas las clases tienen >=2 muestras
    stratify = y if all(c >= 2 for c in class_counts.values()) else None

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    # Pipeline con probabilidades
    pipe = build_pipeline(name=pipeline_name, random_state=random_state)
    pipe.fit(Xtr, ytr)

    # Métricas macro
    yhat = pipe.predict(Xte)
    p, r, f1, _ = precision_recall_fscore_support(
        yte, yhat, average="macro", zero_division=0
    )
    metrics = {"precision": float(p), "recall": float(r), "f1": float(f1)}

    # Persistencia del modelo + metadatos
    paths = _save_model_with_metadata(
        pipe,
        metrics,
        extra_meta={
            "n_total": int(len(df)),
            "n_train": int(len(ytr)),
            "n_test": int(len(yte)),
            "class_distribution": {str(k): int(v) for k, v in class_counts.items()},
            "pipeline": pipeline_name,
            "test_size": test_size,
            "random_state": random_state,
        },
    )

    return metrics, paths

def retrain_from_records(records: List[Dict[str, Any]], **kwargs):
    """
    Útil para la API: recibe lista de dicts con 'textos' y 'labels'.
    """
    df = pd.DataFrame(records)
    return retrain_from_dataframe(df, **kwargs)
