# Backend - API de Clasificación de Textos ODS

## Descripción

API REST desarrollada en FastAPI para clasificación automática de textos en español según los Objetivos de Desarrollo Sostenible (ODS). El sistema permite tanto la predicción de nuevos textos como el reentrenamiento del modelo con datos adicionales.

## Arquitectura

### Componentes principales

- **api.py**: Punto de entrada de la aplicación FastAPI con endpoints REST
- **predict.py**: Módulo de predicción que carga modelos y procesa textos
- **retrain_service.py**: Servicio de reentrenamiento con múltiples estrategias
- **pipelines.py**: Definición de pipelines de machine learning
- **utils.py**: Utilidades de procesamiento de texto y limpieza
- **data_store.py**: Gestión de almacenamiento de datos de entrenamiento
- **last_model.py**: Gestión de modelos y versionado

### Flujo de datos

1. **Predicción**: Texto → Limpieza → Modelo → Clasificación ODS
2. **Reentrenamiento**: Datos nuevos → Estrategia seleccionada → Modelo actualizado → Métricas

## Endpoints

### GET /health
Verifica el estado del servicio y retorna el modelo activo.

**Respuesta:**
```json
{
  "status": "ok",
  "active_model": "/app/etapa2/retrain_models/model_20251011_142927.pkl"
}
```

### POST /predict
Clasifica uno o más textos según los ODS.

**Entrada:**
```json
{
  "instances": [
    {"textos": "La salud en Colombia necesita mejoras urgentes"}
  ]
}
```

**Salida:**
```json
{
  "predictions": [
    {
      "label": 3,
      "label_name": "Salud y bienestar",
      "prob": 0.95
    }
  ]
}
```

### POST /retrain
Reentrena el modelo con nuevos datos etiquetados.

**Entrada:**
```json
{
  "instances": [
    {"textos": "texto sobre pobreza", "labels": 1},
    {"textos": "texto sobre salud", "labels": 3}
  ],
  "strategy": "merge_all",
  "pipeline": "svc_calibrated"
}
```

**Salida:**
```json
{
  "precision": 0.92,
  "recall": 0.89,
  "f1": 0.90,
  "model_version_path": "etapa2/retrain_models/model_20251013_142500.pkl"
}
```

## Estrategias de Reentrenamiento

### merge_all
Combina todos los datos históricos con los nuevos, elimina duplicados y entrena un modelo completo.

### reweight
Aplica oversampling a los datos nuevos para darles mayor peso en el entrenamiento.

### online
Utiliza aprendizaje incremental con SGD, actualizando el modelo existente sin reentrenar desde cero.

## Pipelines de Machine Learning

### svc_calibrated
Support Vector Classifier con calibración de probabilidades usando CalibratedClassifierCV.

### logreg
Regresión logística con regularización L2.

### sgd_online
Stochastic Gradient Descent para aprendizaje incremental.

## Procesamiento de Texto

### Limpieza automática
- Normalización de caracteres especiales
- Eliminación de stopwords en español
- Tokenización con NLTK
- Filtrado de textos muy cortos (configurable)

### Preprocesamiento
- Vectorización TF-IDF
- Reducción dimensional opcional
- Balanceo de clases

## Gestión de Modelos

### Versionado automático
Los modelos se guardan con timestamp: `model_YYYYMMDD_HHMMSS.pkl`

### Metadatos
Cada modelo incluye archivo de metadatos con:
- Fecha de creación
- Métricas de rendimiento
- Hash MD5 del archivo
- Parámetros de entrenamiento

### Persistencia
- Modelos: `etapa2/retrain_models/`
- Datos de entrenamiento: `training_store.parquet`
- Metadatos: `model_*.meta.json`

## Configuración

### Variables de entorno
- `PYTHONPATH`: Ruta base de la aplicación
- Puerto por defecto: 8000

### CORS
Configurado para permitir todas las conexiones en modo desarrollo.

## Dependencias

### Core
- FastAPI: Framework web
- Pydantic: Validación de datos
- Uvicorn: Servidor ASGI

### Machine Learning
- scikit-learn: Algoritmos ML
- pandas: Manipulación de datos
- numpy: Operaciones numéricas
- joblib: Serialización de modelos

### Procesamiento de texto
- NLTK: Procesamiento de lenguaje natural
- pyarrow: Formato Parquet

### Utilidades
- openpyxl: Lectura de archivos Excel

## Uso programático

### Predicción
```python
from etapa2.back.predict import predict

result = predict("La educación rural necesita más recursos")
print(result[0]["label_name"])  # "Educación de calidad"
```

### Reentrenamiento
```python
from etapa2.back.retrain_service import retrain_from_records

data = [
    {"textos": "nuevo texto", "labels": 1}
]
metrics, paths = retrain_from_records(data, strategy="merge_all")
```

## Monitoreo

### Health checks
El endpoint `/health` permite verificar:
- Estado del servicio
- Modelo activo cargado
- Disponibilidad de la API

### Logs
- Errores de predicción
- Métricas de reentrenamiento
- Carga de modelos

## Limitaciones

- Requiere mínimo 30 instancias para reentrenamiento
- Mínimo 2 clases diferentes en los datos
- Textos deben tener al menos 5 caracteres
- Modelos limitados a clasificación ODS (1, 3, 4)
