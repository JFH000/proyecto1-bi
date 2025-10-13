# 🐳 Instrucciones para Docker - Aplicación ODS

## 📋 Requisitos previos

- Docker instalado
- Docker Compose instalado

## 🚀 Cómo ejecutar la aplicación

### 1. Construir y ejecutar con Docker Compose

```bash
# Construir las imágenes y ejecutar los contenedores
docker-compose up --build

# O en modo detached (en segundo plano)
docker-compose up --build -d
```

### 2. Acceder a la aplicación

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

### 3. Verificar que todo funciona

```bash
# Verificar estado de los contenedores
docker-compose ps

# Ver logs del backend
docker-compose logs backend

# Ver logs del frontend
docker-compose logs frontend
```

## 🔧 Comandos útiles

### Parar la aplicación
```bash
docker-compose down
```

### Reconstruir solo el backend
```bash
docker-compose up --build backend
```

### Reconstruir solo el frontend
```bash
docker-compose up --build frontend
```

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Ejecutar comandos dentro del contenedor
```bash
# Acceder al contenedor del backend
docker-compose exec backend bash

# Acceder al contenedor del frontend
docker-compose exec frontend sh
```

## 🌐 Acceso desde otros computadores

Para acceder desde otros computadores en la misma red:

1. **Encuentra tu IP local**:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. **Modifica el docker-compose.yml** para exponer en todas las interfaces:
   ```yaml
   ports:
     - "0.0.0.0:3001:80"  # Frontend
     - "0.0.0.0:8000:8000"  # Backend
   ```

3. **Accede desde otros computadores**:
   - Frontend: `http://TU_IP:3001`
   - Backend: `http://TU_IP:8000`

## 📁 Estructura de archivos Docker

```
proyecto1-bi/
├── Dockerfile.backend      # Imagen del backend FastAPI
├── Dockerfile.frontend     # Imagen del frontend Nginx
├── docker-compose.yml      # Orquestación de servicios
├── .dockerignore          # Archivos a ignorar en Docker
└── DOCKER_INSTRUCTIONS.md # Este archivo
```

## 🐛 Solución de problemas

### Error de puerto ocupado
```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Cambiar puertos en docker-compose.yml si es necesario
```

### Error de permisos (Linux/Mac)
```bash
sudo docker-compose up --build
```

### Limpiar contenedores e imágenes
```bash
# Parar y eliminar contenedores
docker-compose down

# Eliminar imágenes
docker-compose down --rmi all

# Limpiar todo (¡cuidado!)
docker system prune -a
```

### Verificar conectividad entre contenedores
```bash
# Desde el frontend, probar conexión al backend
docker-compose exec frontend wget -qO- http://backend:8000/health
```

## 📊 Monitoreo

### Ver uso de recursos
```bash
docker stats
```

### Ver logs específicos
```bash
# Solo errores del backend
docker-compose logs backend | grep ERROR

# Últimas 100 líneas
docker-compose logs --tail=100 backend
```

## 🔄 Actualizaciones

Para actualizar la aplicación:

1. **Detener contenedores**:
   ```bash
   docker-compose down
   ```

2. **Actualizar código** (si es necesario)

3. **Reconstruir y ejecutar**:
   ```bash
   docker-compose up --build
   ```

## 📝 Notas importantes

- Los modelos reentrenados se guardan en `./etapa2/retrain_models/` y persisten entre reinicios
- El frontend se conecta automáticamente al backend usando el nombre del servicio Docker
- CORS está configurado para permitir todas las conexiones (modo desarrollo)
- Los logs se pueden ver con `docker-compose logs -f`

## 🆘 Soporte

Si tienes problemas:

1. Verifica que Docker esté ejecutándose
2. Revisa los logs: `docker-compose logs`
3. Verifica que los puertos no estén ocupados
4. Asegúrate de tener permisos suficientes
