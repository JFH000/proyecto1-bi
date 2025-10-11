# etapa2/back/retrain_service.py
import os, json, time, hashlib
from typing import Dict, Any, Tuple, List, Optional, Literal
import joblib, pandas as pd, numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support
from .pipelines import build_pipeline
from .utils import clean_df
from .data_store import read_store, write_store

Strategy = Literal["merge_all", "reweight", "online"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RETRAIN_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "retrain_models"))
TEST_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "data", "Datos de prueba_proyecto.xlsx"))
os.makedirs(RETRAIN_DIR, exist_ok=True)

def _load_test() -> Optional[pd.DataFrame]:
    if os.path.isfile(TEST_PATH):
        df = pd.read_excel(TEST_PATH)
        if {"textos", "labels"}.issubset(df.columns):
            return df[["textos", "labels"]].dropna().copy()
    return None

def _save_model_with_metadata(model, metrics: Dict[str, float], extra_meta: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    ts = time.strftime("%Y%m%d_%H%M%S")
    model_path = os.path.join(RETRAIN_DIR, f"model_{ts}.pkl")
    meta_path  = os.path.join(RETRAIN_DIR, f"model_{ts}.meta.json")
    joblib.dump(model, model_path)
    h = hashlib.md5()
    with open(model_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    meta = {"created_at": ts, "model_path": model_path, "metrics": metrics, "md5": h.hexdigest()}
    if extra_meta: meta.update(extra_meta)
    with open(meta_path, "w", encoding="utf-8") as f: json.dump(meta, f, ensure_ascii=False, indent=2)
    return {"model_path": model_path, "meta_path": meta_path}

def _evaluate(pipe, Xte, yte) -> Dict[str, float]:
    yhat = pipe.predict(Xte)
    p, r, f1, _ = precision_recall_fscore_support(yte, yhat, average="macro", zero_division=0)
    return {"precision": float(p), "recall": float(r), "f1": float(f1)}

def retrain_from_dataframe(
    df_new: pd.DataFrame,
    strategy: Strategy = "merge_all",
    random_state: int = 42,
    pipeline_name: str = "svc_calibrated",
    test_size: float = 0.20,
) -> Tuple[Dict[str, float], Dict[str, str]]:

    required = {"textos", "labels"}
    if not required.issubset(df_new.columns):
        raise ValueError("retrain_from_dataframe espera columnas ['textos','labels'].")

    # Limpieza (no filtramos por longitud en reentrenamiento)
    df_new = clean_df(df_new.dropna(subset=["textos", "labels"]).copy(), use_nltk=True, use_short_text=True)
    if df_new.empty:
        raise ValueError("No hay datos nuevos válidos para reentrenar.")

    # Dataset canónico acumulado
    df_store = read_store()
    df_store = clean_df(df_store.dropna(subset=["textos","labels"]).copy(), use_nltk=True, use_short_text=True)

    # Test fijo si existe; si no, se hará split estratificado
    df_test_fixed = _load_test()
    X_fixed, y_fixed = (df_test_fixed["textos"], df_test_fixed["labels"]) if df_test_fixed is not None else (None, None)

    extra_meta = {"strategy": strategy, "pipeline": pipeline_name, "n_new": int(len(df_new))}

    # ---- Estrategias ----
    if strategy == "merge_all":
        df_all = pd.concat([df_store, df_new], ignore_index=True).drop_duplicates(subset=["textos"])
        write_store(df_all)  # persistimos el “conocimiento”
        X = df_all["textos"].values
        y = df_all["labels"].astype(int).values
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=random_state,
                                             stratify=y if (pd.Series(y).value_counts()>=2).all() else None)
        pipe = build_pipeline(name=pipeline_name, random_state=random_state)
        pipe.fit(Xtr, ytr)
        metrics = _evaluate(pipe, X_fixed if X_fixed is not None else Xte,
                                  y_fixed if y_fixed is not None else yte)
        paths = _save_model_with_metadata(pipe, metrics, extra_meta | {"n_total": int(len(df_all))})
        return metrics, paths

    if strategy == "reweight":
        # 1) Unión histórica + nuevo (dedup) y persistir store limpio
        df_all = pd.concat([df_store, df_new], ignore_index=True).drop_duplicates(subset=["textos"])
        write_store(df_all)

        # 2) Crear dataset de entrenamiento con oversampling de lo nuevo (p.ej., k=2)
        k = 2
        df_train = pd.concat([df_all, *([df_new] * (k-1))], ignore_index=True)

        # 3) Split y entrenamiento
        X = df_train["textos"].values
        y = df_train["labels"].astype(int).values
        Xtr, Xte, ytr, yte = train_test_split(
            X, y, test_size=test_size, random_state=random_state,
            stratify=y if (pd.Series(y).value_counts() >= 2).all() else None
        )

        pipe = build_pipeline(name=pipeline_name, random_state=random_state)
        pipe.fit(Xtr, ytr)  # sin sample_weight (CalibratedSVC suele ignorarlo)

        # 4) Evaluación (test fijo si existe)
        metrics = _evaluate(pipe, X_fixed if X_fixed is not None else Xte,
                                y_fixed if y_fixed is not None else yte)

        paths = _save_model_with_metadata(
            pipe, metrics,
            extra_meta | {"n_total": int(len(df_all)), "oversample_k": k}
        )
        return metrics, paths


    if strategy == "online":
        # 1) Inicializa con el store para fijar las clases
        X0 = df_store["textos"].astype(str).values
        y0 = df_store["labels"].astype(int).values

        pipe = build_pipeline(name="sgd_online", random_state=random_state)
        pipe.fit(X0, y0)

        # 2) Actualiza con el lote nuevo
        Xn = df_new["textos"].astype(str).values
        yn = df_new["labels"].astype(int).values
        pipe.partial_fit(Xn, yn)

        # 3) Evalúa
        if df_test_fixed is not None:
            Xt = df_test_fixed["textos"].astype(str).values
            yt = df_test_fixed["labels"].astype(int).values
            metrics = _evaluate(pipe, Xt, yt)
        else:
            # fallback: holdout sobre store
            Xtr, Xte, ytr, yte = train_test_split(
                X0, y0, test_size=test_size, random_state=random_state,
                stratify=y0 if (pd.Series(y0).value_counts() >= 2).all() else None
            )
            metrics = _evaluate(pipe, Xte, yte)

        paths = _save_model_with_metadata(
            pipe, metrics, extra_meta | {"n_total": int(len(df_store))}
        )
        return metrics, paths


def retrain_from_records(records: List[Dict[str, Any]], **kwargs):
    df = pd.DataFrame(records)
    return retrain_from_dataframe(df, **kwargs)
