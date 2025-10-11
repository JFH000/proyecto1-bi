# etapa2/back/last_model.py
import os
import glob
import joblib

# carpetas relativas a /etapa2/back
BACK_DIR = os.path.dirname(os.path.abspath(__file__))
FIRST_MODEL = os.path.normpath(os.path.join(BACK_DIR, "..", "first_model.pkl"))
RETRAIN_DIR = os.path.normpath(os.path.join(BACK_DIR, "..", "retrain_models"))

def get_last_model_path() -> str:
    os.makedirs(RETRAIN_DIR, exist_ok=True)
    # solo modelos .pkl (ignora .gitkeep y otros)
    candidates = sorted(
        glob.glob(os.path.join(RETRAIN_DIR, "*.pkl")),
        key=os.path.getctime
    )
    return candidates[-1] if candidates else FIRST_MODEL

def get_last_model():
    path = get_last_model_path()
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"No se encontró un modelo en '{path}'. "
            "Asegura 'etapa2/first_model.pkl' o genera uno en 'etapa2/retrain_models/'."
        )
    return joblib.load(path)

if __name__ == "__main__":
    # smoke test opcional
    m = get_last_model()
    print("Modelo cargado:", type(m))
