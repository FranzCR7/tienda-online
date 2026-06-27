"""
app/carrito/__init__.py - Blueprint de Carrito
"""

from flask import Blueprint

bp = Blueprint('carrito', __name__)

from app.carrito import rutas  # noqa: E402, F401
