# TTOCA Backend API

API REST para el sistema de gestión de colas de TTOCA.

## Descripción

Backend desarrollado en Python con Flask que proporciona una API REST completa para la gestión de empresas, colas y turnos. Incluye autenticación, WebSockets para actualizaciones en tiempo real y endpoints de health check.

## Características

- API REST pura (no sirve archivos estáticos)
- Autenticación con JWT
- WebSockets para actualizaciones en tiempo real
- CORS configurado para dominios específicos
- Health check endpoints
- Limpieza automática de turnos antiguos
- Base de datos SQLite

## Requisitos

- Python 3.8+
- pip

## Instalación

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
python app.py
```

El servidor se ejecutará en `http://0.0.0.0:8001`

## Endpoints

### Health Check

- `GET /` - Información básica de la API
- `GET /health` - Health check simple
- `GET /api/health` - Health check detallado con estado de DB
- `GET /api/status` - Estado completo del sistema

### Autenticación

- `POST /api/auth/login` - Inicio de sesión
- `POST /api/auth/logout` - Cierre de sesión
- `POST /api/auth/register` - Registro de usuario

### Empresas

- `GET /api/empresas` - Listar empresas
- `POST /api/empresas` - Crear empresa
- `GET /api/empresas/:id` - Obtener empresa
- `PUT /api/empresas/:id` - Actualizar empresa
- `DELETE /api/empresas/:id` - Eliminar empresa

### Colas

- `GET /api/colas` - Listar colas
- `POST /api/colas` - Crear cola
- `GET /api/colas/:id` - Obtener cola
- `PUT /api/colas/:id` - Actualizar cola
- `DELETE /api/colas/:id` - Eliminar cola

### Configuración de Colas

- `GET /api/colas/:id/config` - Obtener configuración de cola
- `PUT /api/colas/:id/config` - Actualizar configuración de cola

## CORS

El backend está configurado para aceptar peticiones desde:

- `http://localhost:5173` (desarrollo)
- `https://ttoca.online` (producción)
- `https://www.ttoca.online` (producción)

## WebSockets

El backend incluye soporte para WebSockets en tiempo real para actualizaciones de colas y turnos.

## Base de Datos

Utiliza SQLite con el archivo `ttoca.db`. Ver `README_SQLITE.md` para más información.

## Estructura del Proyecto

```
TTOCA-BACKEND/
├── api/              # Blueprints de la API
│   ├── auth.py       # Endpoints de autenticación
│   ├── empresa.py    # Endpoints de empresas
│   ├── cola.py       # Endpoints de colas
│   └── cola_config.py # Endpoints de configuración
├── core/             # Funcionalidad core
│   ├── database.py   # Gestión de base de datos
│   └── websocket.py  # Configuración de WebSockets
├── services/         # Lógica de negocio
├── app.py            # Punto de entrada
├── config.py         # Configuración
└── requirements.txt  # Dependencias
```

## Limpieza Automática

El sistema realiza una limpieza automática de turnos antiguos al cerrar la aplicación.

## Desarrollo

### Variables de Entorno

Puedes crear un archivo `.env` para configurar variables de entorno:

```
FLASK_ENV=development
DATABASE_URL=sqlite:///ttoca.db
SECRET_KEY=your-secret-key
```

## Notas

- Este backend NO sirve archivos estáticos ni el frontend
- El frontend debe ser desplegado por separado
- El directorio `dist/` está ignorado en git
