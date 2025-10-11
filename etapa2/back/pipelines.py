from typing import Literal, Optional
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.utils.class_weight import compute_sample_weight
import numpy as np

PipelineName = Literal["svc_calibrated", "logreg", "sgd_online"]

class OnlineSGDPipeline:
    """Incremental: HashingVectorizer + SGDClassifier(log_loss) con pesos balanceados por muestra."""
    def __init__(self, random_state: int = 42):
        self.vec = HashingVectorizer(n_features=2**20, alternate_sign=False, norm="l2")
        # OJO: sin class_weight="balanced"
        self.clf = SGDClassifier(loss="log_loss", random_state=random_state)
        self.classes_ = None

    def fit(self, X, y):
        y = np.asarray(y, dtype=int)
        self.classes_ = np.unique(y)
        Xv = self.vec.transform(list(X))
        w = compute_sample_weight("balanced", y)
        self.clf.partial_fit(Xv, y, classes=self.classes_, sample_weight=w)
        return self

    def partial_fit(self, X, y, classes=None):
        y = np.asarray(y, dtype=int)
        if self.classes_ is None:
            self.classes_ = np.unique(y)
        Xv = self.vec.transform(list(X))
        w = compute_sample_weight("balanced", y)
        self.clf.partial_fit(Xv, y, classes=self.classes_, sample_weight=w)
        return self

    def predict(self, X):
        return self.clf.predict(self.vec.transform(list(X)))

    def predict_proba(self, X):
        return self.clf.predict_proba(self.vec.transform(list(X)))

def build_pipeline(name: PipelineName = "svc_calibrated", random_state: int = 42):
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=50000,
        lowercase=False,
        strip_accents=None,
    )

    if name == "svc_calibrated":
        base = LinearSVC(C=1.0, class_weight="balanced", random_state=random_state)
        try:
            clf = CalibratedClassifierCV(estimator=base, method="sigmoid", cv=3)
        except TypeError:
            clf = CalibratedClassifierCV(base_estimator=base, method="sigmoid", cv=3)
        return Pipeline([("tfidf", vectorizer), ("clf", clf)])

    if name == "logreg":
        clf = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=random_state,
            solver="lbfgs",
            multi_class="auto",
        )
        return Pipeline([("tfidf", vectorizer), ("clf", clf)])

    if name == "sgd_online":
        return OnlineSGDPipeline(random_state=random_state)

    raise ValueError(f"Pipeline no soportado: {name}")
