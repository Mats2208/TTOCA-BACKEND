"""
Configuración para TTOCA Backend con SQLite

Este archivo contiene configuraciones recomendadas para diferentes entornos.
"""

import os
from datetime import timedelta

class Config:
    """Configuración base"""
    # Configuración de SQLite
    DATABASE_NAME = 'ttoca.db'
    
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # CORS - URLs permitidas
    CORS_ORIGINS = [
        'http://localhost:5173',
        'https://www.ttoca.online'
    ]
    
    # Configuración de limpieza automática
    AUTO_CLEANUP_DAYS = 1  # Días después de los cuales limpiar turnos antiguos
    
    # Configuración de backup automático
    AUTO_BACKUP_ENABLED = False
    AUTO_BACKUP_INTERVAL_HOURS = 24
    
class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    FLASK_ENV = 'development'
    
class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # En producción, usar variables de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-must-set-a-secret-key'
    
    # Configuración más estricta para producción
    AUTO_BACKUP_ENABLED = True
    AUTO_CLEANUP_DAYS = 7  # Mantener turnos por una semana en producción
    
    # URLs adicionales para producción
    CORS_ORIGINS = Config.CORS_ORIGINS + [
        # Agregar aquí URLs adicionales de producción
        # 'https://tu-dominio-adicional.com'
    ]

class TestConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    DATABASE_NAME = 'test_ttoca.db'
    
# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])