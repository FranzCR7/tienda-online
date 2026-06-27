"""
tests/conftest.py - Configuración global de pytest
"""

import pytest
from app import crear_app, db


@pytest.fixture(scope='session')
def app():
    """App de pruebas compartida entre tests."""
    app = crear_app('pruebas')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='session')
def cliente(app):
    return app.test_client()
