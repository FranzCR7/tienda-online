"""
app/principal/__init__.py - Blueprint principal (página de inicio)
"""

from flask import Blueprint

bp = Blueprint('principal', __name__)

from app.principal import rutas  # noqa: E402, F401
