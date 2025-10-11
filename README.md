# Backend – Analítica de Textos (Etapa 2)

API REST para clasificar textos ODS y **reentrenar** el modelo.

## 1) Requisitos

* Python ≥ 3.9
* macOS / Linux / Windows
* Internet solo la primera vez (descargas NLTK)

**Instalación**

```bash
python -m venv .venv
# Win: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
# Si usas Parquet para el store:
pip install -U pyarrow openpyxl
# Asegura imports relativos:
touch etapa2/__init__.py etapa2/back/__init__.py
```

## 2) Levantar la API

```bash
uvicorn etapa2.back.api:app --reload --port 8000
```

**Smoke test**

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" \
  -d '{"instances":[{"textos":"La salud en Colombia está mal"}]}'
```

> Si no existe un modelo entrenado, genera uno base (opcional):

```bash
python -m etapa2.back.retrain --make-first-model \
  --input data/datos_originales_totales.xlsx \
  --text-col textos --label-col labels \
  --pipeline svc_calibrated
```

## 3) Endpoints mínimos

### `POST /predict`

Entrada:

```json
{ "instances": [ { "textos": "La salud en Colombia está mal" } ] }
```

Salida:

```json
{ "predictions": [ { "label": 3, "label_name": "Salud y bienestar", "prob": 0.99 } ] }
```

### `POST /retrain`

* Requiere **≥ 30** registros y **≥ 2 clases**.
  Entrada (ejemplo):

```json
{
  "instances": [
    { "textos": "texto sobre pobreza", "labels": 1 },
    { "textos": "texto sobre salud",   "labels": 3 },
    { "textos": "texto sobre educación","labels": 4 }
  ]
}
```

Salida:

```json
{ "precision": 0.98, "recall": 0.98, "f1": 0.98, "model_version_path": "etapa2/retrain_models/model_YYYYMMDD_HHMMSS.pkl" }
```

> Estrategias opcionales: `strategy: "merge_all" | "reweight" | "online"` y `pipeline: "svc_calibrated" | "logreg" | "sgd_online"`.
> Si no especificas, usa `merge_all` + `svc_calibrated`.

## 4) Probar rápido (cURL)

```bash
# salud
curl -s http://127.0.0.1:8000/health

# predicción
curl -s -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" \
  -d '{"instances":[{"textos":"Urge mejorar la educación rural"}]}'

# reentrenamiento (lee payload_retrain.json con ≥30 filas)
curl -s -X POST http://127.0.0.1:8000/retrain -H "Content-Type: application/json" \
  -d @payload_retrain.json
```

## 5) Conectar con el front actual

Archivos del front: `index.html`, `styles.css`, `script.js`.

1. **Edita la URL de la API** en `script.js`:

   ```js
   const API_URL = "http://127.0.0.1:8000";
   ```
2. **Sirve el front** (opción simple):

   ```bash
   # en la carpeta del front
   python -m http.server 5500
   # abre http://127.0.0.1:5500 en el navegador
   ```

   > La API ya viene con **CORS permitido** (modo demo).
3. **Clasificar**: escribe un texto y pulsa “Clasificar texto”.
4. **Reentrenar**: carga un **.xlsx** o **.json** con columnas mapeables a:

   * `textos` (o `Texto`, `Comentario`)
   * `labels` enteros (o `ODS`, `Clasificacion`)
     Deben ser **≥ 30** filas y **≥ 2** clases. Pulsa “Reentrenar modelo”.

**Ejemplo .json para reentrenar**

```json
[
  { "textos": "la pobreza extrema debe reducirse", "labels": 1 },
  { "textos": "mejoras urgentes en hospitales",    "labels": 3 },
  { "textos": "acceso a educación de calidad",     "labels": 4 }
]
```

## 6) Problemas comunes (rápidas)

* **Parquet**: instala `pyarrow` o usa fallback CSV (si está implementado).
* **NLTK**: la primera corrida descarga recursos; si falla, el backend usa *fallback*.
* **422 / 400 en `/retrain`**: revisa que haya **≥ 30** filas y **≥ 2** clases.
* **CORS**: ya habilitado “*” en demo; en producción restrínge `allow_origins`.

---