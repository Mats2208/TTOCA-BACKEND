from flask import Flask, send_from_directory, request, abort
from flask_cors import CORS
from api.auth import auth_bp
from api.empresa import empresa_bp
from api.cola import cola_bp
from api.cola_config import cola_config_bp
from database import init_database
import os
import atexit

# --- Config estática manual ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

# Desactiva la ruta estática automática (evita interceptar /pricing, /login, etc.)
app = Flask(__name__, static_folder=None)

# CORS solo para API
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "https://ttoca.online",
        "https://www.ttoca.online",
    ]}},
    supports_credentials=True
)

# Inicializa DB
init_database()

# Blueprints API
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(empresa_bp, url_prefix='/api')
app.register_blueprint(cola_bp, url_prefix='/api')
app.register_blueprint(cola_config_bp, url_prefix='/api')

# Limpieza al salir
def cleanup_old_records():
    try:
        from db_cola_utils import limpiar_turnos_antiguos
        n = limpiar_turnos_antiguos()
        if n > 0:
            print(f"🧹 Limpieza automática: {n} turnos antiguos eliminados")
    except Exception as e:
        print(f"Error en limpieza automática: {e}")

atexit.register(cleanup_old_records)

# --- Servir SPA ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def spa(path):
    # No interceptar rutas de API
    if path.startswith("api/"):
        abort(404)

    fullpath = os.path.join(DIST_DIR, path)
    if path and os.path.exists(fullpath) and os.path.isfile(fullpath):
        # Sirve archivos reales de /dist (ej: /assets/...)
        return send_from_directory(DIST_DIR, path)

    # Fallback a index.html para rutas del router (login, pricing, servicios, etc.)
    return send_from_directory(DIST_DIR, "index.html")

# (Opcional) Si algún 404 se escapa y NO es API ni archivo con extensión, devolver index.html
@app.errorhandler(404)
def not_found(e):
    # Si es API o parece archivo (tiene extensión), deja el 404
    last = request.path.rsplit("/", 1)[-1]
    if request.path.startswith("/api") or "." in last:
        return e
    return send_from_directory(DIST_DIR, "index.html")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
