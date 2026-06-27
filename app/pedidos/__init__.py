"""
app/pedidos/__init__.py - Blueprint de Pedidos
"""

from flask import Blueprint

bp = Blueprint('pedidos', __name__)

from app.pedidos import rutas  # noqa: E402, F401
