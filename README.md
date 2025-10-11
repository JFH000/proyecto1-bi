# Backend – Analítica de Textos (Etapa 2)

API REST para clasificación de textos (ODS) con **reentrenamiento** en línea y **versionado** de modelos.
Stack: **FastAPI**, **scikit-learn** (TF-IDF + SVC calibrado), **pandas**, **joblib**, **NLTK**.

## 1) Requisitos

* **Python ≥ 3.9** (probado en 3.9)
* macOS / Linux / Windows
* Conexión a internet **solo la primera vez** (descarga de recursos NLTK)

### Dependencias (requirements.txt)

```txt
fastapi
uvicorn
pydantic>=2
scikit-learn>=1.2
pandas
joblib
nltk
```

> Nota: Si te quedas en scikit-learn < 1.2, el calibrador usa `base_estimator`. El código ya trae compatibilidad para ambas.

## 2) Instalación

Clona el repo y crea un entorno:

```bash
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

Asegura que el paquete sea importable:

```bash
touch etapa2/__init__.py etapa2/back/__init__.py
```

## 3) Estructura relevante

```
proyecto1-bi/
├─ data/
│  ├─ datos_originales_totales.xlsx    # dataset base
│  └─ datos_etapa2.xlsx                # (opcional) dataset adicional
├─ etapa2/
│  ├─ first_model.pkl                  # se genera con retrain.py (make-first-model)
│  ├─ retrain_models/                  # versiones posteriores del modelo
│  │  └─ .gitkeep
│  └─ back/
│     ├─ api.py
│     ├─ predict.py
│     ├─ pipelines.py
│     ├─ retrain_service.py
│     ├─ retrain.py                    # CLI para entrenar/reentrenar desde archivo
│     ├─ last_model.py
│     └─ utils.py
└─ README.md
```

**Esquema de datos esperado**

* Columna de texto: `textos` (str)
* Columna objetivo: `labels` (int: p. ej., 1, 3, 4)

## 4) Generar el modelo base

Desde la raíz del repo:

```bash
# crea first_model.pkl en etapa2/first_model.pkl
python -m etapa2.back.retrain --make-first-model \
  --input data/datos_originales_totales.xlsx \
  --text-col textos --label-col labels \
  --pipeline svc_calibrated
```

> El script limpia duplicados y textos vacíos. Para entrenamiento offline filtra textos < 300 chars.

## 5) Levantar la API

```bash
uvicorn etapa2.back.api:app --reload
```

Pruebas rápidas:

```bash
# salud
curl http://localhost:8000/health

# predicción
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"instances":[{"textos":"La salud en Colombia está mal"}]}'
```

## 6) Endpoints

### `GET /health`

Retorna estado y ruta del modelo activo.

**Respuesta**

```json
{ "status": "ok", "active_model": "etapa2/first_model.pkl" }
```

### `POST /predict`

Predice una o varias instancias manteniendo **orden** y **cardinalidad**.

**Request**

```json
{
  "instances": [
    { "textos": "La salud en Colombia está mal" },
    { "textos": "Urge mejorar la educación rural" }
  ]
}
```

**Response**

```json
{
  "predictions": [
    { "label": 3, "label_name": "Salud y bienestar", "prob": 0.87 },
    { "label": 4, "label_name": "Educación de calidad", "prob": 0.76 }
  ]
}
```

> `prob` requiere pipeline con probabilidades (ya configurado con **SVC calibrado**).

### `POST /retrain`

Reentrena con un lote **etiquetado** y versiona el modelo.
Para la API **NO** se filtran textos cortos (el usuario suele enviar frases breves).

**Request (mín. 30 instancias recomendado)**

```json
{
  "instances": [
    { "textos": "texto sobre pobreza 1", "labels": 1 },
    { "textos": "texto sobre salud 1", "labels": 3 },
    { "textos": "texto sobre educación 1", "labels": 4 }
  ]
}
```

**Response**

```json
{
  "precision": 0.85,
  "recall": 0.83,
  "f1": 0.84,
  "model_version_path": "etapa2/retrain_models/model_YYYYmmdd_HHMMSS.pkl"
}
```

Tras reentrenar, `/health` debe apuntar a la **nueva versión**.

## 7) Conectar con el Front

### (A) Front minimalista (HTML + JS)

Guarda como `frontend.html` y abre en el navegador (requiere CORS abierto, ver nota abajo):

```html
<!doctype html>
<html>
  <body>
    <h3>Clasificar textos</h3>
    <textarea id="txt" rows="4" cols="60">La salud en Colombia está mal</textarea><br>
    <button id="btn">Predecir</button>
    <pre id="out"></pre>

    <script>
      const API = "http://localhost:8000";
      document.getElementById("btn").onclick = async () => {
        const textos = document.getElementById("txt").value
          .split("\n").filter(Boolean).map(t => ({ textos: t }));
        const res = await fetch(`${API}/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ instances: textos })
        });
        document.getElementById("out").textContent = JSON.stringify(await res.json(), null, 2);
      };
    </script>
  </body>
</html>
```

### (B) Next.js / React (TypeScript)

```ts
// services/api.ts
export type PredictItem = { label: number; label_name: string; prob?: number | null };
export async function predict(texts: string[], baseUrl = "http://localhost:8000") {
  const body = { instances: texts.map((t) => ({ textos: t })) };
  const res = await fetch(`${baseUrl}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as { predictions: PredictItem[] };
}

export async function retrain(instances: { textos: string; labels: number }[], baseUrl = "http://localhost:8000") {
  const res = await fetch(`${baseUrl}/retrain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ instances }),
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json(); // { precision, recall, f1, model_version_path }
}
```

```tsx
// components/Classifier.tsx
"use client";
import React from "react";
import { predict, retrain } from "@/services/api";

export default function Classifier() {
  const [input, setInput] = React.useState("La salud en Colombia está mal");
  const [out, setOut] = React.useState<any>(null);

  return (
    <div>
      <textarea value={input} onChange={(e) => setInput(e.target.value)} rows={4} className="w-full" />
      <div className="flex gap-2 mt-2">
        <button onClick={async () => setOut(await predict(input.split("\n").filter(Boolean)))}>Predecir</button>
        <button onClick={async () => {
          const items = [
            { textos: "texto sobre pobreza", labels: 1 },
            { textos: "texto sobre salud", labels: 3 },
            { textos: "texto sobre educación", labels: 4 },
            // agrega más para llegar a ~30
          ];
          setOut(await retrain(items));
        }}>Reentrenar</button>
      </div>
      <pre className="mt-4">{out ? JSON.stringify(out, null, 2) : null}</pre>
    </div>
  );
}
```

### CORS (si llamas la API desde otro origen)

Añade esto al inicio de `api.py`:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringe a tus dominios en prod
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 8) CLI para reentrenar desde archivo (opcional)

```bash
# reentrenar con archivo completo
python -m etapa2.back.retrain --retrain \
  --input data/datos_etapa2.xlsx \
  --text-col textos --label-col labels \
  --pipeline svc_calibrated --test-size 0.2
```

## 9) Estrategias de reentrenamiento (resumen para el informe)

1. **Completo acumulativo (implementado en la API)**
   Concatena datos nuevos al histórico y entrena desde cero. +Robusto; −Más costo.

2. **Incremental (`partial_fit`)**
   Actualiza pesos sin reiniciar. +Rápido; −Riesgo de olvido catastrófico y soporte limitado.

3. **Warm-start / recalibración**
   Reentrena iniciando de coeficientes previos y/o recalibra probabilidades. +Conserva conocimiento; −Más complejo.

## 10) Solución de problemas

* **`ModuleNotFoundError: utils` / imports relativos**
  Asegura `etapa2/__init__.py` y `etapa2/back/__init__.py` y ejecuta con `python -m ...`.

* **`punkt_tab` / NLTK**
  La primera ejecución descarga recursos; si falla, `utils.py` usa `preserve_line=True` y **fallback** con `split()`.

* **`CalibratedClassifierCV(..., base_estimator=...)`**
  En scikit-learn ≥ 1.2 usa `estimator=...`. El código trae `try/except` para ambas.

* **Probabilidad `null`**
  Asegura pipeline `svc_calibrated` o `logreg` (ambos exponen `predict_proba`).

---

## 11) Notas finales

* El API **respeta el esquema del CSV**: keys `textos` y `labels` (int) en JSON.
* El selector de modelo carga siempre la **última versión** si existe (`etapa2/retrain_models/*.pkl`); si no, usa `etapa2/first_model.pkl`.
* Versionado: cada reentreno guarda `model_YYYYmmdd_HHMMSS.pkl` y un `.meta.json` con métricas y hash.

¡Listo! Con esto puedes levantar el back, re-entrenar y conectarlo a un front en minutos.
