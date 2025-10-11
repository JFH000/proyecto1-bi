# etapa2/back/retrain.py
import os, argparse
import pandas as pd
import joblib

from .utils import clean_df
from .pipelines import build_pipeline
from .retrain_service import retrain_from_dataframe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIRST_MODEL_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "first_model.pkl"))

def load_table(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    if ext == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Formato no soportado: {ext}. Use .xlsx/.xls o .csv")

def standardize_columns(df: pd.DataFrame, text_col: str, label_col: str) -> pd.DataFrame:
    df = df.copy()
    if text_col != "textos":
        df.rename(columns={text_col: "textos"}, inplace=True)
    if label_col != "labels":
        df.rename(columns={label_col: "labels"}, inplace=True)
    return df[["textos", "labels"]]

def make_first_model(df: pd.DataFrame, pipeline_name: str = "svc_calibrated", random_state: int = 42):
    # Limpieza para entrenamiento (filtra cortos, etc.)
    df = clean_df(df, use_nltk=True, use_short_text=False)
    X = df["textos"].values
    y = df["labels"].astype(int).values

    pipe = build_pipeline(name=pipeline_name, random_state=random_state)
    pipe.fit(X, y)

    os.makedirs(os.path.dirname(FIRST_MODEL_PATH), exist_ok=True)
    joblib.dump(pipe, FIRST_MODEL_PATH)
    print(f"✅ first_model.pkl guardado en: {FIRST_MODEL_PATH}")

def main():
    ap = argparse.ArgumentParser(description="Generar modelo base o re-entrenar.")
    ap.add_argument("--input", default=os.path.normpath(os.path.join(BASE_DIR, "..", "..", "data", "datos_originales_totales.xlsx")),
                    help="Ruta a .xlsx/.csv con columnas de texto y etiqueta.")
    ap.add_argument("--text-col", default="textos", help="Nombre de la columna de texto en el archivo de entrada.")
    ap.add_argument("--label-col", default="labels", help="Nombre de la columna de etiqueta en el archivo de entrada.")
    ap.add_argument("--pipeline", default="svc_calibrated", choices=["svc_calibrated", "logreg"])
    ap.add_argument("--random-state", type=int, default=42)
    ap.add_argument("--test-size", type=float, default=0.20, help="Solo para --retrain.")
    ap.add_argument("--make-first-model", action="store_true", help="Entrena y guarda etapa2/first_model.pkl")
    ap.add_argument("--retrain", action="store_true", help="Re-entrena y guarda en retrain_models/")
    args = ap.parse_args()

    if not (args.make_first_model or args.retrain):
        ap.error("Debe indicar --make-first-model o --retrain")

    df_raw = load_table(args.input)
    df_std = standardize_columns(df_raw, args.text_col, args.label_col)

    if args.make_first_model:
        make_first_model(df_std, pipeline_name=args.pipeline, random_state=args.random_state)

    if args.retrain:
        metrics, paths = retrain_from_dataframe(
            df_std,
            test_size=args.test_size,
            random_state=args.random_state,
            pipeline_name=args.pipeline,
        )
        print(f"✅ Re-entrenado. Métricas macro: {metrics}")
        print(f"📦 Modelo guardado en: {paths['model_path']}")

if __name__ == "__main__":
    main()
