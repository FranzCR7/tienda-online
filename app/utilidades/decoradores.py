"""
app/utilidades/decoradores.py - Decoradores personalizados para control de acceso
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def requiere_admin(f):
    """Decorador que requiere que el usuario sea administrador."""
    @wraps(f)
    def decorado(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('autenticacion.login'))
        if not current_user.es_administrador:
            abort(403)
        return f(*args, **kwargs)
    return decorado


def requiere_cliente(f):
    """Decorador que requiere que el usuario sea cliente."""
    @wraps(f)
    def decorado(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('autenticacion.login'))
        if not current_user.es_cliente and not current_user.es_administrador:
            abort(403)
        return f(*args, **kwargs)
    return decorado


def requiere_activo(f):
    """Decorador que requiere que el usuario esté activo."""
    @wraps(f)
    def decorado(*args, **kwargs):
        if current_user.is_authenticated and not current_user.activo:
            flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'danger')
            return redirect(url_for('autenticacion.logout'))
        return f(*args, **kwargs)
    return decorado
