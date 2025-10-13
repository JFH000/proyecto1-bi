# Proyecto 1 - Analítica de Textos ODS

Sistema de clasificación automática de opiniones ciudadanas según los Objetivos de Desarrollo Sostenible (ODS) mediante machine learning.

## Características

- **Clasificación automática** de textos en español por ODS (1, 3, 4)
- **API REST** con endpoints de predicción y reentrenamiento
- **Demo web** intuitiva para usuarios finales
- **Aumentación de datos** sintéticos para mejorar rendimiento
- **Containerización** con Docker para despliegue fácil

## Uso Rápido

### Con Docker (Recomendado)
```bash
# Construir y ejecutar
docker-compose up --build -d

# Acceder
# Frontend: http://localhost:3001
```

### Desarrollo Local
```bash
# Backend
uvicorn etapa2.back.api:app --reload --port 8000

# Frontend
cd etapa2/front
python -m http.server 5500
```

## Endpoints Principales

- `POST /predict` - Clasificar textos
- `POST /retrain` - Reentrenar modelo
- `GET /health` - Estado del servicio

## Estructura del Proyecto

```
proyecto1-bi/
├── etapa1/              # Modelo base y análisis inicial
├── etapa2/              # API y demo web
│   ├── back/           # Backend FastAPI
│   ├── front/          # Frontend web
│   └── retrain_models/ # Modelos reentrenados
├── data/               # Datasets
└── docs/              # Documentación
```

## Documentación

- [Wiki Etapa 2](README_ETAPA2_WIKI.md) - Documentación completa
- [README Backend](etapa2/back/README.md) - Documentación técnica API
- [README Frontend](etapa2/front/README.md) - Documentación interfaz web

## Requisitos

- Python ≥ 3.9
- Docker (opcional)
- Navegador web moderno

## Equipo

- **Análisis y aumentación de datos**: Juan Hernández
- **Desarrollo API y reentrenamiento**: David Elias Fororo Cobos  
- **Frontend y UX**: Jerónimo A. Pineda Cano
