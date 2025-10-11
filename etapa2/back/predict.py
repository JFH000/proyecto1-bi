from typing import List, Union
import numpy as np

from .last_model import get_last_model
from .utils import limpiar_texto

# Ajusta este diccionario a tus clases reales
DICT_ODS = {
    1: "Fin de la pobreza",
    3: "Salud y bienestar",
    4: "Educación de calidad",
}

def _prepare_inputs(texts: Union[str, List[str]]) -> List[str]:
    """
    Devuelve una lista de textos limpiados, sin eliminar filas,
    para preservar cardinalidad y orden requeridos por la API.
    """
    if isinstance(texts, str):
        texts = [texts]
    if not isinstance(texts, (list, tuple)):
        raise TypeError("texts debe ser str o List[str].")
    # Limpieza por elemento (no se eliminan duplicados ni cortos)
    return [limpiar_texto(t if t is not None else "") for t in texts]

def predict(texts: Union[str, List[str]]) -> List[dict]:
    """
    Retorna una lista de dicts con: label, label_name y prob (si disponible).
    Mantiene el mismo orden y número de instancias que la entrada.
    """
    model = get_last_model()
    X = _prepare_inputs(texts)

    y = model.predict(X)

    # Probabilidades si el modelo las expone (p. ej., CalibratedClassifierCV/LogisticRegression)
    proba = None
    if hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(X)
        except Exception:
            proba = None

    out = []
    for i, lbl in enumerate(y):
        try:
            lbl_int = int(lbl)
        except Exception:
            lbl_int = lbl  # por si el modelo devuelve strings

        item = {
            "label": lbl_int,
            "label_name": DICT_ODS.get(lbl_int, str(lbl)),
        }
        if proba is not None:
            item["prob"] = float(np.max(proba[i]))
        else:
            item["prob"] = None  # si tu pipeline no expone predict_proba
        out.append(item)

    return out

if __name__ == "__main__":
    print(predict("La salud en Colombia está mal"))
