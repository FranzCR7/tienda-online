"""
app/__init__.py - Application Factory de la Tienda Online
Implementa el patrón Application Factory de Flask.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

from config import configuraciones

# Instancias de extensiones (sin app todavía)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()


def crear_app(nombre_config='default'):
    """
    Application Factory: crea y configura la instancia de Flask.

    Args:
        nombre_config (str): Nombre de la configuración a usar.

    Returns:
        Flask: Instancia configurada de la aplicación.
    """
    app = Flask(__name__)

    # Cargar configuración según entorno
    config_obj = configuraciones.get(nombre_config, configuraciones['default'])
    app.config.from_object(config_obj)
    config_obj.init_app(app)

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Configurar Flask-Login
    login_manager.login_view = 'autenticacion.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'

    # Registrar Blueprints
    _registrar_blueprints(app)

    # Registrar manejadores de errores
    _registrar_manejadores_errores(app)

    # Registrar filtros Jinja2 personalizados
    _registrar_filtros_jinja(app)

    # Inyectar variables globales en todos los templates
    @app.context_processor
    def inyectar_variables_globales():
        from datetime import datetime
        from flask_login import current_user as cu
        return {'now': datetime.utcnow()}

    # Registrar comandos CLI
    _registrar_comandos_cli(app)

    return app


def _registrar_blueprints(app):
    """Registra todos los Blueprints de la aplicación."""

    from app.autenticacion import bp as bp_autenticacion
    app.register_blueprint(bp_autenticacion, url_prefix='/auth')

    from app.productos import bp as bp_productos
    app.register_blueprint(bp_productos, url_prefix='/productos')

    from app.carrito import bp as bp_carrito
    app.register_blueprint(bp_carrito, url_prefix='/carrito')

    from app.pedidos import bp as bp_pedidos
    app.register_blueprint(bp_pedidos, url_prefix='/pedidos')

    from app.pagos import bp as bp_pagos
    app.register_blueprint(bp_pagos, url_prefix='/pagos')

    from app.administracion import bp as bp_administracion
    app.register_blueprint(bp_administracion, url_prefix='/admin')

    from app.dashboard import bp as bp_dashboard
    app.register_blueprint(bp_dashboard, url_prefix='/dashboard')

    # Blueprint principal (rutas raíz)
    from app.principal import bp as bp_principal
    app.register_blueprint(bp_principal)

    # API REST
    from app.servicios.api_rest import api as bp_api
    app.register_blueprint(bp_api)


def _registrar_manejadores_errores(app):
    """Registra los manejadores de errores HTTP."""
    from app.utilidades.manejadores_error import (
        error_404, error_403, error_500
    )
    app.register_error_handler(404, error_404)
    app.register_error_handler(403, error_403)
    app.register_error_handler(500, error_500)


def _registrar_filtros_jinja(app):
    """Registra filtros personalizados para las plantillas Jinja2."""

    @app.template_filter('moneda')
    def filtro_moneda(valor):
        """Formatea un número como moneda boliviana."""
        try:
            return f'Bs. {float(valor):,.2f}'
        except (TypeError, ValueError):
            return 'Bs. 0.00'

    @app.template_filter('fecha_corta')
    def filtro_fecha_corta(fecha):
        """Formatea una fecha en formato corto."""
        if fecha:
            return fecha.strftime('%d/%m/%Y')
        return ''

    @app.template_filter('fecha_larga')
    def filtro_fecha_larga(fecha):
        """Formatea una fecha en formato largo."""
        if fecha:
            meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                     'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            return f'{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}'
        return ''

    @app.template_filter('truncar')
    def filtro_truncar(texto, longitud=100):
        """Trunca un texto a la longitud especificada."""
        if texto and len(texto) > longitud:
            return texto[:longitud] + '...'
        return texto or ''


def _registrar_comandos_cli(app):
    """Registra comandos CLI personalizados de Flask."""

    @app.cli.command('crear-admin')
    def crear_admin():
        """Crea el usuario administrador inicial."""
        from app.modelos.usuario import Usuario
        from app.modelos.rol import Rol

        with app.app_context():
            # Crear roles si no existen
            rol_admin = Rol.query.filter_by(nombre='administrador').first()
            if not rol_admin:
                rol_admin = Rol(nombre='administrador', descripcion='Administrador del sistema')
                db.session.add(rol_admin)

            rol_cliente = Rol.query.filter_by(nombre='cliente').first()
            if not rol_cliente:
                rol_cliente = Rol(nombre='cliente', descripcion='Cliente de la tienda')
                db.session.add(rol_cliente)

            db.session.commit()

            # Crear admin si no existe
            admin = Usuario.query.filter_by(email='admin@tienda.com').first()
            if not admin:
                admin = Usuario(
                    nombre='Administrador',
                    apellido='Sistema',
                    email='admin@tienda.com',
                    telefono='70000000',
                    rol_id=rol_admin.id,
                    activo=True
                )
                admin.establecer_contrasena('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print('✅ Usuario administrador creado:')
                print('   Email: admin@tienda.com')
                print('   Contraseña: Admin123!')
            else:
                print('⚠️  El usuario administrador ya existe.')

    @app.cli.command('poblar-db')
    def poblar_db():
        """Puebla la base de datos con datos de ejemplo."""
        from app.servicios.servicio_seed import poblar_base_datos
        poblar_base_datos()
        print('✅ Base de datos poblada con datos de ejemplo.')
