"""
app/dashboard/__init__.py - Blueprint del Dashboard Administrativo
"""

from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from app.dashboard import rutas  # noqa: E402, F401
