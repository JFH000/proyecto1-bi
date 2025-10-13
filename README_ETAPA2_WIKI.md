# Etapa 2: Automatización y Uso de Modelos de Analítica de Textos

## Resumen Ejecutivo

La Etapa 2 implementa un sistema completo de automatización para clasificación de textos ODS mediante **aumentación dirigida**, **API REST** y **demo web**. El objetivo es transformar opiniones ciudadanas en señales tempranas para priorización de políticas públicas.

**Logros principales:**
- Mejora del modelo mediante aumentación de datos sintéticos (+2.3 ptos F1)
- API REST funcional con endpoints de predicción y reentrenamiento
- Demo web intuitiva para usuarios finales
- Sistema containerizado y desplegable

---

## 1. Aumentación de Datos y Mejora del Modelo

### 1.1 Metodología Sin Fuga de Datos

**Problema identificado**: Clase minoritaria ODS 1 (Fin de la pobreza) con bajo rendimiento.

**Solución implementada**:
- **Benchmark**: Modelo Etapa 1 evaluado en `Datos_etapa 2.xlsx` (prueba externa)
- **Aumentación**: 400 textos sintéticos generados con Google Gemini 2.5 Flash
- **Reentrenamiento**: Solo con datos originales + sintéticos (sin usar prueba externa)

### 1.2 Generación de Datos Sintéticos

**Proceso**:
1. **Identificación**: ODS 1 como clase minoritaria
2. **Semillas**: 4-8 textos reales de ODS 1 para estilo
3. **Generación**: 3 tandas de 200 textos cada una
4. **Limpieza**: Eliminación de 500 duplicados, selección de 400 únicos
5. **Etiquetado**: Todos con label=1 (ODS 1)

**Prompt utilizado**:
```
Genera 200 opiniones ciudadanas breves (3-6 oraciones), en español de Colombia,
mapeadas SOLO al ODS 1. >350 caracteres, sin datos personales,
variando contextos (urbano/rural). TODAS diferentes.
```

### 1.3 Resultados Cuantitativos

**Mejoras en prueba externa (Datos_etapa 2.xlsx):**

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| **Accuracy** | 0.9293 | **0.9495** | +2.0 ptos |
| **F1** | 0.9227 | **0.9453** | +2.3 ptos |
| **Precision** | 0.9431 | **0.9484** | +0.5 ptos |
| **Recall** | 0.9133 | **0.9432** | +3.0 ptos |

**Impacto**: Reducción significativa del sesgo hacia clases mayoritarias, especialmente en Recall (+3.0 ptos).

---

## 2. API REST y Automatización

### 2.1 Arquitectura Implementada

**Stack tecnológico**:
- **FastAPI**: Framework web moderno
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI
- **CORS**: Configurado para desarrollo

**Estructura modular**:
```
etapa2/back/
├── api.py              # Endpoints REST
├── predict.py          # Módulo de predicción
├── retrain_service.py  # Servicio de reentrenamiento
├── pipelines.py        # Pipelines ML
└── utils.py            # Utilidades
```

### 2.2 Endpoints Implementados

#### POST /predict
**Funcionalidad**: Clasificación de textos en tiempo real.

```json
// Entrada
{
  "instances": [{"textos": "La salud necesita mejoras"}]
}

// Salida
{
  "predictions": [{
    "label": 3,
    "label_name": "Salud y bienestar",
    "prob": 0.95
  }]
}
```

#### POST /retrain
**Funcionalidad**: Reentrenamiento del modelo con nuevos datos.

```json
// Entrada
{
  "instances": [
    {"textos": "texto sobre pobreza", "labels": 1}
  ],
  "strategy": "merge_all"
}

// Salida
{
  "precision": 0.95,
  "recall": 0.94,
  "f1": 0.945,
  "model_version_path": "retrain_models/model_20251013_142500.pkl"
}
```

#### GET /health
**Funcionalidad**: Monitoreo del servicio y modelo activo.

### 2.3 Estrategias de Reentrenamiento

**Implementadas**:
1. **merge_all**: Combina datos históricos + nuevos (implementada)
2. **reweight**: Oversampling de datos nuevos
3. **online**: Aprendizaje incremental con SGD

**Gestión de modelos**:
- Versionado automático con timestamp
- Metadatos con métricas y configuración
- Persistencia en `retrain_models/`

---

## 3. Demo Web (Frontend)

### 3.1 Funcionalidades Implementadas

**Clasificación de textos**:
- Interfaz intuitiva con textarea
- Validación en tiempo real
- Visualización de resultados con probabilidades
- Loader visual durante procesamiento

**Reentrenamiento**:
- Carga de archivos .xlsx y .json
- Procesamiento automático con SheetJS
- Validación de mínimo 30 registros
- Mapeo automático de columnas
- Visualización de métricas de rendimiento

### 3.2 Diseño y UX

**Características**:
- Tema oscuro profesional
- Diseño responsivo
- Feedback visual (hover, transiciones)
- Validación robusta de entrada
- Manejo de errores descriptivo

**Paleta de colores**:
- Naranja brillante (#FF8000) para botones principales
- Azul brillante (#3E92C2) para elementos secundarios
- Azul suave (#A7DDD9) para títulos
- Negro intenso (#1D1E18) para fondo

### 3.3 Procesamiento de Archivos

**Formatos soportados**:
- **JSON**: Estructura directa
- **Excel**: Mapeo automático de columnas

**Validaciones**:
- Mínimo 30 registros
- Verificación de formato
- Manejo de errores robusto

---

## 4. Containerización y Despliegue

### 4.1 Arquitectura Docker

**Backend Container**:
- Base: Python 3.11-slim
- Puerto: 8000
- Volúmenes: Persistencia de modelos
- Health checks: Monitoreo automático

**Frontend Container**:
- Base: Nginx Alpine
- Puerto: 3001
- Configuración: CORS optimizado

**Orquestación**:
- Docker Compose para gestión
- Red interna para comunicación
- Restart policies automáticas

### 4.2 Instrucciones de Uso

**Desarrollo local**:
```bash
# Backend
uvicorn etapa2.back.api:app --reload --port 8000

# Frontend
python -m http.server 5500
```

**Docker**:
```bash
# Construir y ejecutar
docker-compose up --build -d

# Acceder
# Frontend: http://localhost:3001
```

---

## 5. Caso de Uso y Valor de Negocio

### 5.1 Usuario Objetivo
- Analistas de políticas públicas
- Gestores de programas sociales
- Investigadores en desarrollo social

### 5.2 Proceso de Negocio
1. **Recolección**: Opiniones ciudadanas en canales digitales
2. **Clasificación**: Automatización por ODS
3. **Priorización**: Identificación de áreas críticas
4. **Mejora continua**: Reentrenamiento con feedback

### 5.3 Valor Agregado
- **Automatización**: Reducción de tiempo de clasificación manual
- **Escalabilidad**: Procesamiento de grandes volúmenes
- **Adaptabilidad**: Mejora continua del modelo
- **Trazabilidad**: Versionado y métricas

---

## 6. Trabajo en Equipo

### 6.1 Distribución de Roles
- **Análisis de datos**: Juan Hernández
- **Aumentación de datos**: Juan Hernández
- **Desarrollo de API**: David Elias Fororo Cobos
- **Reentrenamiento de modelos**: David Elias Fororo Cobos
- **Frontend y UX**: Jerónimo A. Pineda Cano
- **Documentación**: Todos

### 6.2 Retos y Aprendizajes
- **Control de fuga de datos**: Metodología rigurosa implementada
- **Calidad de sintéticos**: Optimización de prompts y validación
- **Diseño de API**: Contratos claros y versionado
- **Integración**: Manejo de CORS y comunicación

---

## 7. Evidencia y Resultados

### 7.1 Mejoras Cuantitativas
- **F1 Score**: +2.3 puntos porcentuales
- **Recall**: +3.0 puntos porcentuales (impacto en clase minoritaria)
- **Accuracy**: +2.0 puntos porcentuales
- **Precision**: +0.5 puntos porcentuales

### 7.2 Evidencia Técnica
- **Reproducibilidad**: Código versionado y documentado
- **Metodología**: Sin fuga de datos, evaluación externa
- **Trazabilidad**: Logs completos y versionado de modelos
- **Funcionalidad**: API y demo web operativas

### 7.3 Artefactos Entregables
- **Modelo mejorado**: `first_model.pkl`
- **API REST**: Endpoints funcionales
- **Demo web**: Interfaz intuitiva
- **Containerización**: Despliegue reproducible
- **Documentación**: READMEs técnicos

---

## 8. Conclusión

La Etapa 2 logra exitosamente:

1. **Mejora metodológica**: Aumentación dirigida sin fuga de datos
2. **Automatización completa**: API REST con reentrenamiento
3. **Interfaz accesible**: Demo web funcional
4. **Despliegue reproducible**: Containerización con Docker
5. **Mejoras cuantitativas**: Incremento significativo en métricas

El sistema está listo para uso en producción y puede adaptarse a nuevos datos mediante reentrenamiento controlado, proporcionando una solución escalable para la clasificación automática de opiniones ciudadanas en el contexto de los ODS.
