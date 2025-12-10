"""
Services module - Business logic layer
"""

from .auth_service import (
    add_user, 
    validate_user, 
    get_user_projects, 
    get_user_project_by_id,
    add_user_project,
    update_user_project,
    delete_user_project
)

from .cola_service import (
    agregar_turno,
    siguiente_turno,
    obtener_turnos,
    eliminar_cola,
    obtener_turno_actual,
    obtener_posicion_turno,
    buscar_turno_global,
    obtener_estadisticas_cola,
    limpiar_turnos_antiguos
)

from .cola_config_service import (
    obtener_configuracion,
    guardar_configuracion_empresa,
    agregar_categoria,
    actualizar_categoria,
    eliminar_categoria,
    obtener_categoria,
    obtener_categorias_resumen,
    resetear_contador_categoria
)

__all__ = [
    # Auth
    'add_user', 'validate_user', 'get_user_projects', 
    'get_user_project_by_id', 'add_user_project',
    'update_user_project', 'delete_user_project',
    # Cola
    'agregar_turno', 'siguiente_turno', 'obtener_turnos',
    'eliminar_cola', 'obtener_turno_actual', 'obtener_posicion_turno',
    'buscar_turno_global', 'obtener_estadisticas_cola', 'limpiar_turnos_antiguos',
    # Cola Config
    'obtener_configuracion', 'guardar_configuracion_empresa',
    'agregar_categoria', 'actualizar_categoria', 'eliminar_categoria',
    'obtener_categoria', 'obtener_categorias_resumen', 'resetear_contador_categoria'
]
