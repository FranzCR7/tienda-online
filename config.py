"""
config.py - Configuración por entornos de la aplicación Flask
Tienda Online - Proyecto Universitario
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class ConfiguracionBase:
    """Configuración base compartida por todos los entornos."""

    # Clave secreta para sesiones y CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-muy-segura-cambiar-en-produccion'

    # Configuración de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Configuración de subida de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB máximo
    UPLOAD_FOLDER_PRODUCTOS = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'productos')
    UPLOAD_FOLDER_COMPROBANTES = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'comprobantes')
    UPLOAD_FOLDER_QR = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'qr')
    EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Configuración de paginación
    PRODUCTOS_POR_PAGINA = 12
    PEDIDOS_POR_PAGINA = 10
    USUARIOS_POR_PAGINA = 10

    # Nombre de la aplicación
    NOMBRE_APP = 'TiendaOnline'

    # WTF CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    @staticmethod
    def init_app(app):
        """Inicialización adicional de la aplicación."""
        # Crear directorios de uploads si no existen
        os.makedirs(app.config['UPLOAD_FOLDER_PRODUCTOS'], exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER_COMPROBANTES'], exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER_QR'], exist_ok=True)


class ConfiguracionDesarrollo(ConfiguracionBase):
    """Configuración para entorno de desarrollo."""

    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/tienda_online_dev'

    # Mostrar queries SQL en consola durante desarrollo
    SQLALCHEMY_ECHO = False


class ConfiguracionPruebas(ConfiguracionBase):
    """Configuración para entorno de pruebas."""

    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/tienda_online_test'


class ConfiguracionProduccion(ConfiguracionBase):
    """Configuración para entorno de producción (Render)."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

    # Render provee la variable DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Corrección para el prefijo de PostgreSQL en Render
    @classmethod
    def init_app(cls, app):
        ConfiguracionBase.init_app(app)
        # Render usa 'postgres://' pero SQLAlchemy requiere 'postgresql://'
        db_url = os.environ.get('DATABASE_URL', '')
        if db_url.startswith('postgres://'):
            app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace('postgres://', 'postgresql://', 1)


# Mapa de configuraciones por nombre de entorno
configuraciones = {
    'desarrollo': ConfiguracionDesarrollo,
    'pruebas': ConfiguracionPruebas,
    'produccion': ConfiguracionProduccion,
    'default': ConfiguracionDesarrollo,
}
