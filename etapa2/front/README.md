# Frontend - Interfaz de Usuario para Clasificación ODS

## Descripción

Interfaz web estática desarrollada en HTML, CSS y JavaScript para interactuar con la API de clasificación de textos ODS. Permite a los usuarios clasificar textos individuales y reentrenar el modelo con nuevos datos.

## Arquitectura

### Componentes principales

- **index.html**: Estructura HTML principal de la aplicación
- **styles.css**: Estilos CSS con tema oscuro y diseño responsivo
- **script.js**: Lógica JavaScript para comunicación con la API
- **logo.png**: Imagen del logo del proyecto

### Flujo de interacción

1. **Clasificación**: Usuario ingresa texto → Validación → Llamada API → Mostrar resultado
2. **Reentrenamiento**: Usuario sube archivo → Procesamiento → Validación → Llamada API → Mostrar métricas

## Funcionalidades

### Clasificación de Textos

#### Interfaz
- Textarea para entrada de texto con placeholder de ejemplo
- Botón "Clasificar texto" para procesar la entrada
- Área de resultados que muestra predicción y probabilidad
- Loader visual durante el procesamiento

#### Proceso
1. Validación de texto no vacío
2. Llamada POST a `/predict` con el texto
3. Visualización del resultado con:
   - Nombre del ODS predicho
   - Número del ODS
   - Probabilidad de confianza

### Reentrenamiento del Modelo

#### Interfaz
- Input de archivo que acepta formatos .xlsx y .json
- Botón "Reentrenar modelo" para procesar el archivo
- Validación visual de archivos seleccionados
- Loader visual durante el procesamiento

#### Proceso
1. Validación de archivo seleccionado
2. Procesamiento del archivo según formato:
   - **JSON**: Parsing directo del contenido
   - **XLSX**: Conversión usando biblioteca SheetJS
3. Mapeo de columnas a formato requerido
4. Validación de mínimo 30 registros
5. Llamada POST a `/retrain` con los datos
6. Visualización de métricas de rendimiento

## Diseño y Estilo

### Paleta de colores
- **Naranja brillante**: #FF8000 (botones principales, acentos)
- **Azul brillante**: #3E92C2 (elementos secundarios)
- **Azul suave**: #A7DDD9 (títulos, texto destacado)
- **Negro intenso**: #1D1E18 (fondo principal)
- **Gris claro**: #F5F6F8 (texto principal)

### Características visuales
- Tema oscuro con contraste optimizado
- Diseño centrado con contenedor de ancho máximo 700px
- Efectos hover en botones y elementos interactivos
- Transiciones suaves para mejor experiencia de usuario
- Diseño responsivo para diferentes tamaños de pantalla
- Loader animado con spinner personalizado

### Componentes de interfaz
- **Container principal**: Fondo oscuro con bordes redondeados y sombra
- **Textarea**: Estilo personalizado con focus states
- **Botones**: Diseño consistente con efectos de elevación
- **Área de resultados**: Panel destacado con borde de acento
- **Input de archivo**: Zona de arrastre visual con efectos hover
- **Loader overlay**: Pantalla de carga con animación de spinner

## Comunicación con la API

### Configuración de URL
```javascript
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? "http://127.0.0.1:8000"  // Desarrollo local
  : "http://backend:8000";   // Docker
```

### Endpoints utilizados

#### POST /predict
```javascript
const response = await fetch(`${API_URL}/predict`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ instances: [{ textos: texto }] })
});
```

#### POST /retrain
```javascript
const response = await fetch(`${API_URL}/retrain`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ instances: data })
});
```

## Procesamiento de Archivos

### Formatos soportados

#### JSON
Estructura esperada:
```json
[
  { "textos": "texto sobre pobreza", "labels": 1 },
  { "textos": "texto sobre salud", "labels": 3 }
]
```

#### Excel (.xlsx)
Columnas mapeables:
- `textos`, `Texto`, `Comentario` → Campo de texto
- `labels`, `ODS`, `Clasificacion` → Campo de etiqueta

### Validaciones
- Mínimo 30 registros para reentrenamiento
- Validación de formato de archivo
- Verificación de columnas requeridas
- Manejo de errores de parsing

## Manejo de Errores

### Clasificación
- Validación de texto vacío
- Manejo de errores de red
- Mensajes de error descriptivos
- Logging detallado en consola

### Reentrenamiento
- Validación de archivo seleccionado
- Verificación de formato de datos
- Manejo de errores de API
- Feedback visual de progreso

## Dependencias Externas

### SheetJS (XLSX)
- CDN: `https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js`
- Funcionalidad: Lectura de archivos Excel
- Uso: Conversión de hojas de cálculo a JSON

## Características Técnicas

### JavaScript
- ES6+ con async/await
- Fetch API para comunicación HTTP
- Manejo de promesas y errores
- Validación de entrada del usuario
- Logging detallado para debugging
- Funciones de loader para feedback visual

### CSS
- Flexbox para layout
- CSS Grid para componentes complejos
- Variables CSS para consistencia
- Media queries para responsividad
- Animaciones CSS para loader
- Estados hover y focus personalizados

### HTML
- Estructura semántica
- Accesibilidad básica
- Meta tags para viewport
- Prevención de envío de formularios
- Overlay de loader con z-index alto

## Configuración de Servidor

### Nginx (Docker)
- Configuración personalizada para servir archivos estáticos
- Headers CORS configurados
- Redirección de rutas a index.html
- Compresión y cache headers

### Desarrollo local
- Servidor HTTP simple (Python, Node.js, etc.)
- CORS habilitado en el backend
- Proxy opcional para desarrollo

## Limitaciones

- Requiere JavaScript habilitado
- Dependiente de la disponibilidad de la API
- Limitado a formatos JSON y Excel
- Sin persistencia local de datos
- Validación básica de entrada

## Mejoras Futuras

- Drag & drop para archivos
- Visualización de progreso de reentrenamiento
- Historial de predicciones
- Exportación de resultados
- Modo offline básico
- Validación más robusta de archivos
- Mejores mensajes de error
- Soporte para más formatos de archivo
