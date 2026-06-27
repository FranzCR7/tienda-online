"""
app/autenticacion/__init__.py - Blueprint de Autenticación
"""

from flask import Blueprint

bp = Blueprint('autenticacion', __name__)

from app.autenticacion import rutas  # noqa: E402, F401
