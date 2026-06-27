"""
app/pagos/__init__.py - Blueprint de Pagos
"""

from flask import Blueprint

bp = Blueprint('pagos', __name__)

from app.pagos import rutas  # noqa: E402, F401
