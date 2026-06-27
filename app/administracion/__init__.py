"""
app/administracion/__init__.py - Blueprint de Administración
"""

from flask import Blueprint

bp = Blueprint('administracion', __name__)

from app.administracion import rutas  # noqa: E402, F401
