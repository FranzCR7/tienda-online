"""
app/productos/__init__.py - Blueprint de Productos
"""

from flask import Blueprint

bp = Blueprint('productos', __name__)

from app.productos import rutas  # noqa: E402, F401
