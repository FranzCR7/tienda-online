"""
tests/test_autenticacion.py - Pruebas del módulo de autenticación
"""

import pytest
from app import crear_app, db
from app.modelos.rol import Rol
from app.modelos.usuario import Usuario


@pytest.fixture
def app():
    """Crea una instancia de la app para pruebas."""
    app = crear_app('pruebas')
    with app.app_context():
        db.create_all()
        _crear_datos_prueba()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def cliente(app):
    """Cliente de prueba Flask."""
    return app.test_client()


@pytest.fixture
def cliente_autenticado(app):
    """Cliente de prueba con sesión de cliente iniciada."""
    with app.test_client() as c:
        with app.app_context():
            c.post('/auth/login', data={
                'email': 'cliente@test.com',
                'contrasena': 'Test1234!',
                'csrf_token': _obtener_csrf(c, '/auth/login'),
            }, follow_redirects=True)
        yield c


@pytest.fixture
def admin_autenticado(app):
    """Cliente de prueba con sesión de admin iniciada."""
    with app.test_client() as c:
        with app.app_context():
            c.post('/auth/login', data={
                'email': 'admin@test.com',
                'contrasena': 'Admin1234!',
                'csrf_token': _obtener_csrf(c, '/auth/login'),
            }, follow_redirects=True)
        yield c


def _obtener_csrf(client, url):
    """Obtiene el token CSRF de un formulario."""
    resp = client.get(url)
    html = resp.data.decode('utf-8')
    # Extrae el valor del campo csrf_token
    start = html.find('name="csrf_token" value="')
    if start == -1:
        return ''
    start += len('name="csrf_token" value="')
    end = html.find('"', start)
    return html[start:end]


def _crear_datos_prueba():
    """Inserta datos mínimos para las pruebas."""
    rol_admin = Rol(nombre='administrador', descripcion='Admin')
    rol_cliente = Rol(nombre='cliente', descripcion='Cliente')
    db.session.add_all([rol_admin, rol_cliente])
    db.session.commit()

    admin = Usuario(
        nombre='Admin', apellido='Test',
        email='admin@test.com', rol_id=rol_admin.id, activo=True
    )
    admin.establecer_contrasena('Admin1234!')

    cliente = Usuario(
        nombre='Cliente', apellido='Test',
        email='cliente@test.com', rol_id=rol_cliente.id, activo=True
    )
    cliente.establecer_contrasena('Test1234!')

    db.session.add_all([admin, cliente])
    db.session.commit()


# ── Tests de autenticación ────────────────────────────────────────────────────

class TestRegistro:
    """Pruebas del registro de usuarios."""

    def test_registro_exitoso(self, cliente):
        """Un usuario puede registrarse con datos válidos."""
        csrf = _obtener_csrf(cliente, '/auth/registro')
        resp = cliente.post('/auth/registro', data={
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'email': 'nuevo@test.com',
            'contrasena': 'Nuevo1234!',
            'confirmar_contrasena': 'Nuevo1234!',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'exitosamente' in resp.data or b'sesi' in resp.data

    def test_registro_email_duplicado(self, cliente):
        """El registro falla si el email ya existe."""
        csrf = _obtener_csrf(cliente, '/auth/registro')
        resp = cliente.post('/auth/registro', data={
            'nombre': 'Otro',
            'apellido': 'Usuario',
            'email': 'cliente@test.com',
            'contrasena': 'Test1234!',
            'confirmar_contrasena': 'Test1234!',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'registrado' in resp.data

    def test_registro_contrasenas_no_coinciden(self, cliente):
        """El registro falla si las contraseñas no coinciden."""
        csrf = _obtener_csrf(cliente, '/auth/registro')
        resp = cliente.post('/auth/registro', data={
            'nombre': 'Test',
            'apellido': 'User',
            'email': 'testuser@test.com',
            'contrasena': 'Pass1234!',
            'confirmar_contrasena': 'OtraPass!',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'no coinciden' in resp.data


class TestLogin:
    """Pruebas del inicio de sesión."""

    def test_login_correcto(self, cliente):
        """El login funciona con credenciales correctas."""
        csrf = _obtener_csrf(cliente, '/auth/login')
        resp = cliente.post('/auth/login', data={
            'email': 'cliente@test.com',
            'contrasena': 'Test1234!',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_login_contrasena_incorrecta(self, cliente):
        """El login falla con contraseña incorrecta."""
        csrf = _obtener_csrf(cliente, '/auth/login')
        resp = cliente.post('/auth/login', data={
            'email': 'cliente@test.com',
            'contrasena': 'Incorrecta123',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'incorrectos' in resp.data

    def test_login_usuario_inexistente(self, cliente):
        """El login falla con un email que no existe."""
        csrf = _obtener_csrf(cliente, '/auth/login')
        resp = cliente.post('/auth/login', data={
            'email': 'noexiste@test.com',
            'contrasena': 'Test1234!',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'incorrectos' in resp.data

    def test_logout(self, cliente_autenticado):
        """El cierre de sesión funciona correctamente."""
        resp = cliente_autenticado.get('/auth/logout', follow_redirects=True)
        assert resp.status_code == 200

    def test_redireccion_no_autenticado(self, cliente):
        """Un usuario no autenticado es redirigido al intentar acceder a área privada."""
        resp = cliente.get('/carrito/', follow_redirects=False)
        assert resp.status_code in [302, 301]
        assert '/auth/login' in resp.headers.get('Location', '')


class TestModelos:
    """Pruebas unitarias de los modelos."""

    def test_hash_contrasena(self, app):
        """La contraseña se hashea correctamente."""
        with app.app_context():
            u = Usuario(nombre='Test', apellido='Hash', email='hash@test.com',
                        rol_id=1, activo=True)
            u.establecer_contrasena('MiContrasena123')
            assert u.contrasena_hash != 'MiContrasena123'
            assert u.verificar_contrasena('MiContrasena123')
            assert not u.verificar_contrasena('OtraContrasena')

    def test_nombre_completo(self, app):
        """La propiedad nombre_completo devuelve el nombre y apellido."""
        with app.app_context():
            u = Usuario.query.filter_by(email='cliente@test.com').first()
            assert u.nombre_completo == 'Cliente Test'

    def test_roles(self, app):
        """Los roles se asignan correctamente."""
        with app.app_context():
            admin = Usuario.query.filter_by(email='admin@test.com').first()
            cliente = Usuario.query.filter_by(email='cliente@test.com').first()
            assert admin.es_administrador
            assert not admin.es_cliente
            assert cliente.es_cliente
            assert not cliente.es_administrador
