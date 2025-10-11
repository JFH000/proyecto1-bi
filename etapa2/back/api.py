# etapa2/back/api.py
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .predict import predict as predict_fn
from .retrain_service import retrain_from_records
from .last_model import get_last_model_path

app = FastAPI(title="ODS Text Analytics API - Etapa 2")

# ===== Esquemas =====
class Instance(BaseModel):
    textos: str = Field(..., min_length=5, description="Texto en español a clasificar")

class LabeledInstance(Instance):
    labels: int = Field(..., description="Etiqueta ODS como entero (p.ej. 1, 3, 4)")

class PredictRequest(BaseModel):
    # En Pydantic v2: usa min_length para listas
    instances: List[Instance] = Field(..., min_length=1)

class PredictItem(BaseModel):
    label: int
    label_name: str
    prob: Optional[float] = None

class PredictResponse(BaseModel):
    predictions: List[PredictItem]

class RetrainRequest(BaseModel):
    instances: List[LabeledInstance] = Field(..., min_length=30)  # 'cantidad relevante' mínima

class RetrainResponse(BaseModel):
    precision: float
    recall: float
    f1: float
    model_version_path: str

# ===== Endpoints =====
@app.get("/health")
def health():
    return {"status": "ok", "active_model": get_last_model_path()}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        preds = predict_fn([it.textos for it in req.instances])
        return {"predictions": preds}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/retrain", response_model=RetrainResponse)
def retrain(req: RetrainRequest):
    try:
        metrics, paths = retrain_from_records([it.model_dump() for it in req.instances])
        return {
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "model_version_path": paths["model_path"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
