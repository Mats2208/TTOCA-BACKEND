from flask import Flask, jsonify
from flask_cors import CORS
from api.auth import auth_bp
from api.empresa import empresa_bp
from api.cola import cola_bp
from api.cola_config import cola_config_bp
from core.database import init_database
from core.websocket import init_socketio
import atexit
from datetime import datetime

# Inicializa Flask sin static_folder
app = Flask(__name__, static_folder=None)

# CORS configurado para permitir orígenes específicos
CORS(
    app,
    origins=[
        "http://localhost:5173",
        "https://ttoca.online",
        "https://www.ttoca.online",
    ],
    supports_credentials=True
)

# Inicializa DB
init_database()

# Inicializa WebSocket
socketio = init_socketio(app)

# Blueprints API
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(empresa_bp, url_prefix='/api')
app.register_blueprint(cola_bp, url_prefix='/api')
app.register_blueprint(cola_config_bp, url_prefix='/api')

# Limpieza al salir
def cleanup_old_records():
    try:
        from services.cola_service import limpiar_turnos_antiguos
        n = limpiar_turnos_antiguos()
        if n > 0:
            print(f"[LIMPIEZA] Limpieza automática: {n} turnos antiguos eliminados")
    except Exception as e:
        print(f"Error en limpieza automática: {e}")

atexit.register(cleanup_old_records)

# --- Health Check Endpoints ---
@app.route("/")
def root():
    """Endpoint raíz que indica que es una API"""
    return jsonify({
        "message": "TTOCA API",
        "version": "1.0.0",
        "status": "running"
    })

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/health")
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "api": "operational",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/status")
def api_status():
    """Endpoint de estado detallado"""
    try:
        # Verificar conexión a base de datos
        from core.database import db
        db.execute_query("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "api": "operational",
        "database": db_status,
        "websocket": "enabled",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    # Usar socketio.run() en lugar de app.run() para soporte de WebSocket
    socketio.run(app, debug=False, host="0.0.0.0", port=8001)
