"""
app/utilidades/manejadores_error.py - Manejadores de errores HTTP
"""

from flask import render_template


def error_404(e):
    """Manejador para error 404 - Página no encontrada."""
    return render_template('errores/404.html'), 404


def error_403(e):
    """Manejador para error 403 - Acceso prohibido."""
    return render_template('errores/403.html'), 403


def error_500(e):
    """Manejador para error 500 - Error interno del servidor."""
    return render_template('errores/500.html'), 500
