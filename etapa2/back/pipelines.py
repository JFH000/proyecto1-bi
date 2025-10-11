# etapa2/back/pipelines.py
from typing import Literal
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression

PipelineName = Literal["svc_calibrated", "logreg"]

def build_pipeline(
    name: PipelineName = "svc_calibrated",
    random_state: int = 42,
) -> Pipeline:
    """
    Construye un pipeline TF-IDF + clasificador con soporte de probabilidades.
    - 'svc_calibrated' (default): LinearSVC calibrado con sigmoid (cv=3).
    - 'logreg': LogisticRegression (multiclase) con class_weight='balanced'.

    Devuelve: sklearn.Pipeline con .fit/.predict y, si aplica, .predict_proba
    """

    # TF-IDF: los textos ya llegan limpios desde utils.limpiar_texto; aquí solo vectorizamos.
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),   # unigrams + bigrams
        min_df=2,             # ignora términos extremadamente raros
        max_features=50000,   # límite razonable
        lowercase=False,      # ya convertimos a minúsculas en la limpieza
        strip_accents=None,   # preserva acentos (coherente con limpieza)
    )

    if name == "svc_calibrated":
        base = LinearSVC(
            C=1.0,
            class_weight="balanced",
            random_state=random_state,
        )
        # Compatibilidad con distintas versiones de scikit-learn
        try:
            clf = CalibratedClassifierCV(
                estimator=base,      # >= 1.2
                method="sigmoid",
                cv=3,
            )
        except TypeError:
            clf = CalibratedClassifierCV(
                base_estimator=base, # <= 1.1
                method="sigmoid",
                cv=3,
            )

    return Pipeline([
        ("tfidf", vectorizer),
        ("clf", clf),
    ])
