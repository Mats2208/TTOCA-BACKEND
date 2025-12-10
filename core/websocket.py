"""
WebSocket manager para eventos en tiempo real
Maneja emisiones de eventos para actualizaciones de cola
"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from functools import wraps

# Instancia global de SocketIO (se inicializa en app.py)
socketio = None

def init_socketio(app):
    """Inicializa SocketIO con la aplicación Flask"""
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins=[
            "http://localhost:5173",
            "https://ttoca.online",
            "https://www.ttoca.online",
        ],
        async_mode='eventlet',
        logger=False,
        engineio_logger=False
    )

    # Registrar event handlers
    register_handlers()

    return socketio

def register_handlers():
    """Registra todos los event handlers de WebSocket"""

    @socketio.on('connect')
    def handle_connect():
        print(f"Cliente conectado")

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Cliente desconectado")

    @socketio.on('join_queue')
    def handle_join_queue(data):
        """Cliente se une a una sala de cola específica"""
        empresa_id = data.get('empresaId')
        cola_id = data.get('colaId')

        if empresa_id and cola_id:
            room = f"queue_{empresa_id}_{cola_id}"
            join_room(room)
            print(f"Cliente unido a sala: {room}")
            emit('joined_queue', {'room': room, 'empresaId': empresa_id, 'colaId': cola_id})
        else:
            emit('error', {'message': 'empresaId y colaId son requeridos'})

    @socketio.on('leave_queue')
    def handle_leave_queue(data):
        """Cliente abandona una sala de cola específica"""
        empresa_id = data.get('empresaId')
        cola_id = data.get('colaId')

        if empresa_id and cola_id:
            room = f"queue_{empresa_id}_{cola_id}"
            leave_room(room)
            print(f"Cliente salió de sala: {room}")

    @socketio.on('join_empresa')
    def handle_join_empresa(data):
        """Cliente se une a todas las colas de una empresa"""
        empresa_id = data.get('empresaId')

        if empresa_id:
            room = f"empresa_{empresa_id}"
            join_room(room)
            print(f"Cliente unido a empresa: {room}")
            emit('joined_empresa', {'room': room, 'empresaId': empresa_id})
        else:
            emit('error', {'message': 'empresaId es requerido'})

    @socketio.on('leave_empresa')
    def handle_leave_empresa(data):
        """Cliente abandona las salas de una empresa"""
        empresa_id = data.get('empresaId')

        if empresa_id:
            room = f"empresa_{empresa_id}"
            leave_room(room)
            print(f"Cliente salió de empresa: {room}")

# Funciones de emisión para usar desde servicios

def emit_queue_update(empresa_id, cola_id, turnos):
    """Emite actualización de turnos en espera de una cola"""
    if not socketio:
        return

    room = f"queue_{empresa_id}_{cola_id}"
    socketio.emit('queue_updated', {
        'empresaId': empresa_id,
        'colaId': cola_id,
        'turnos': turnos
    }, room=room)

    # También emitir a nivel de empresa
    empresa_room = f"empresa_{empresa_id}"
    socketio.emit('queue_updated', {
        'empresaId': empresa_id,
        'colaId': cola_id,
        'turnos': turnos
    }, room=empresa_room)

    print(f"[WS] Emitido queue_updated a {room}")

def emit_turno_llamado(empresa_id, cola_id, turno):
    """Emite cuando se llama al siguiente turno"""
    if not socketio:
        return

    room = f"queue_{empresa_id}_{cola_id}"
    socketio.emit('turno_llamado', {
        'empresaId': empresa_id,
        'colaId': cola_id,
        'turno': turno
    }, room=room)

    # También emitir a nivel de empresa
    empresa_room = f"empresa_{empresa_id}"
    socketio.emit('turno_llamado', {
        'empresaId': empresa_id,
        'colaId': cola_id,
        'turno': turno
    }, room=empresa_room)

    print(f"[WS] Emitido turno_llamado a {room}: {turno.get('numero')}")

def emit_turno_agregado(empresa_id, cola_id, turno):
    """Emite cuando se agrega un nuevo turno"""
    if not socketio:
        return

    room = f"queue_{empresa_id}_{cola_id}"
    socketio.emit('turno_agregado', {
        'empresaId': empresa_id,
        'colaId': cola_id,
        'turno': turno
    }, room=room)

    # También emitir a nivel de empresa
    empresa_room = f"empresa_{empresa_id}"
    socketio.emit('turno_agregado', {
        'empresaId': empresa_id,
        'colaId': cola_id,
        'turno': turno
    }, room=empresa_room)

    print(f"[WS] Emitido turno_agregado a {room}: {turno.get('numero')}")

def emit_cola_eliminada(empresa_id, cola_id):
    """Emite cuando se elimina una cola"""
    if not socketio:
        return

    room = f"queue_{empresa_id}_{cola_id}"
    socketio.emit('cola_eliminada', {
        'empresaId': empresa_id,
        'colaId': cola_id
    }, room=room)

    # También emitir a nivel de empresa
    empresa_room = f"empresa_{empresa_id}"
    socketio.emit('cola_eliminada', {
        'empresaId': empresa_id,
        'colaId': cola_id
    }, room=empresa_room)

    print(f"[WS] Emitido cola_eliminada a {room}")
