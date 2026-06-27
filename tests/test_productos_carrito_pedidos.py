"""
tests/test_productos_carrito_pedidos.py - Pruebas de productos, carrito y pedidos
"""

import pytest
from decimal import Decimal
from app import crear_app, db
from app.modelos.rol import Rol
from app.modelos.usuario import Usuario
from app.modelos.categoria import Categoria
from app.modelos.producto import Producto
from app.modelos.carrito import Carrito, DetalleCarrito
from app.modelos.pedido import Pedido, DetallePedido
from app.modelos.pago import MetodoPago, ComprobantePago


@pytest.fixture(scope='module')
def app():
    app = crear_app('pruebas')
    with app.app_context():
        db.create_all()
        _seed()
        yield app
        db.session.remove()
        db.drop_all()


def _seed():
    """Datos base para las pruebas."""
    r_admin = Rol(nombre='administrador', descripcion='Admin')
    r_cliente = Rol(nombre='cliente', descripcion='Cliente')
    db.session.add_all([r_admin, r_cliente])
    db.session.commit()

    admin = Usuario(nombre='Admin', apellido='T', email='admin@prod.com',
                    rol_id=r_admin.id, activo=True)
    admin.establecer_contrasena('Admin1234!')

    u = Usuario(nombre='Juan', apellido='Perez', email='juan@prod.com',
                rol_id=r_cliente.id, activo=True)
    u.establecer_contrasena('Juan1234!')

    db.session.add_all([admin, u])
    db.session.commit()

    cat = Categoria(nombre='Electrónica', slug='electronica', activa=True)
    db.session.add(cat)
    db.session.commit()

    p1 = Producto(nombre='Laptop Test', precio=Decimal('1500.00'),
                  stock=10, categoria_id=cat.id, activo=True)
    p2 = Producto(nombre='Mouse Test', precio=Decimal('50.00'),
                  stock=3, categoria_id=cat.id, activo=True)
    p3 = Producto(nombre='Sin Stock', precio=Decimal('100.00'),
                  stock=0, categoria_id=cat.id, activo=True)
    db.session.add_all([p1, p2, p3])

    metodo = MetodoPago(nombre='QR Test', activo=True)
    db.session.add(metodo)
    db.session.commit()


# ── Tests de Productos ────────────────────────────────────────────────────────

class TestProductos:
    """Pruebas del módulo de productos."""

    def test_listar_productos_publico(self, app):
        """La lista de productos es accesible sin autenticación."""
        with app.test_client() as c:
            resp = c.get('/productos/')
            assert resp.status_code == 200

    def test_detalle_producto(self, app):
        """El detalle de un producto activo es accesible."""
        with app.app_context():
            p = Producto.query.filter_by(nombre='Laptop Test').first()
            with app.test_client() as c:
                resp = c.get(f'/productos/{p.id}')
                assert resp.status_code == 200

    def test_detalle_producto_inexistente(self, app):
        """Un producto con ID inexistente devuelve 404."""
        with app.test_client() as c:
            resp = c.get('/productos/99999')
            assert resp.status_code == 404

    def test_busqueda_producto(self, app):
        """La búsqueda de productos funciona correctamente."""
        with app.test_client() as c:
            resp = c.get('/productos/?q=Laptop')
            assert resp.status_code == 200
            assert b'Laptop' in resp.data

    def test_filtro_por_categoria(self, app):
        """El filtro por categoría funciona."""
        with app.app_context():
            cat = Categoria.query.filter_by(nombre='Electrónica').first()
            with app.test_client() as c:
                resp = c.get(f'/productos/?categoria={cat.id}')
                assert resp.status_code == 200

    def test_modelo_en_stock(self, app):
        """La propiedad en_stock refleja el estado del stock."""
        with app.app_context():
            p_con_stock = Producto.query.filter_by(nombre='Laptop Test').first()
            p_sin_stock = Producto.query.filter_by(nombre='Sin Stock').first()
            assert p_con_stock.en_stock is True
            assert p_sin_stock.en_stock is False

    def test_modelo_reducir_stock(self, app):
        """Reducir stock funciona correctamente."""
        with app.app_context():
            p = Producto.query.filter_by(nombre='Laptop Test').first()
            stock_inicial = p.stock
            assert p.reducir_stock(2) is True
            assert p.stock == stock_inicial - 2
            assert p.reducir_stock(999) is False  # No hay suficiente stock
            db.session.rollback()


# ── Tests de API REST ─────────────────────────────────────────────────────────

class TestApiProductos:
    """Pruebas de la API REST de productos."""

    def test_api_listar_productos(self, app):
        """GET /api/v1/productos devuelve lista de productos."""
        with app.test_client() as c:
            resp = c.get('/api/v1/productos')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['ok'] is True
            assert 'productos' in data['datos']

    def test_api_obtener_producto(self, app):
        """GET /api/v1/productos/<id> devuelve el producto."""
        with app.app_context():
            p = Producto.query.filter_by(nombre='Laptop Test').first()
            with app.test_client() as c:
                resp = c.get(f'/api/v1/productos/{p.id}')
                assert resp.status_code == 200
                data = resp.get_json()
                assert data['ok'] is True
                assert data['datos']['nombre'] == 'Laptop Test'

    def test_api_producto_no_existe(self, app):
        """GET /api/v1/productos/99999 devuelve 404."""
        with app.test_client() as c:
            resp = c.get('/api/v1/productos/99999')
            assert resp.status_code == 404

    def test_api_crear_producto_sin_auth(self, app):
        """POST /api/v1/productos sin auth devuelve redirección."""
        with app.test_client() as c:
            resp = c.post('/api/v1/productos',
                          json={'nombre': 'Nuevo', 'precio': 100, 'stock': 5, 'categoria_id': 1})
            assert resp.status_code in [302, 401, 403]

    def test_api_busqueda(self, app):
        """GET /api/v1/productos?q=Mouse filtra resultados."""
        with app.test_client() as c:
            resp = c.get('/api/v1/productos?q=Mouse')
            assert resp.status_code == 200
            data = resp.get_json()
            nombres = [p['nombre'] for p in data['datos']['productos']]
            assert any('Mouse' in n for n in nombres)


# ── Tests de Carrito ──────────────────────────────────────────────────────────

class TestCarrito:
    """Pruebas del módulo de carrito de compras."""

    def _login(self, client, app):
        """Autentica al cliente de prueba."""
        with app.app_context():
            resp = client.get('/auth/login')
            html = resp.data.decode('utf-8')
            start = html.find('name="csrf_token" value="')
            token = ''
            if start != -1:
                start += len('name="csrf_token" value="')
                token = html[start:html.find('"', start)]

            client.post('/auth/login', data={
                'email': 'juan@prod.com',
                'contrasena': 'Juan1234!',
                'csrf_token': token,
            }, follow_redirects=True)

    def test_ver_carrito_requiere_auth(self, app):
        """Ver el carrito requiere autenticación."""
        with app.test_client() as c:
            resp = c.get('/carrito/', follow_redirects=False)
            assert resp.status_code in [301, 302]

    def test_modelo_carrito_agregar(self, app):
        """Se puede agregar un producto al carrito."""
        with app.app_context():
            u = Usuario.query.filter_by(email='juan@prod.com').first()
            p = Producto.query.filter_by(nombre='Laptop Test').first()

            carrito = Carrito(usuario_id=u.id, activo=True)
            db.session.add(carrito)
            db.session.flush()

            exito, msg = carrito.agregar_producto(p, 2)
            assert exito is True
            assert carrito.total_items == 2
            db.session.rollback()

    def test_modelo_carrito_sin_stock(self, app):
        """No se puede agregar más unidades de las disponibles."""
        with app.app_context():
            u = Usuario.query.filter_by(email='juan@prod.com').first()
            p_sin_stock = Producto.query.filter_by(nombre='Sin Stock').first()

            carrito = Carrito(usuario_id=u.id, activo=True)
            db.session.add(carrito)
            db.session.flush()

            exito, msg = carrito.agregar_producto(p_sin_stock, 1)
            assert exito is False
            db.session.rollback()

    def test_modelo_carrito_subtotal(self, app):
        """El subtotal del carrito se calcula correctamente."""
        with app.app_context():
            u = Usuario.query.filter_by(email='juan@prod.com').first()
            p = Producto.query.filter_by(nombre='Laptop Test').first()

            carrito = Carrito(usuario_id=u.id, activo=True)
            db.session.add(carrito)
            db.session.flush()

            carrito.agregar_producto(p, 3)
            assert float(carrito.total) == float(p.precio) * 3
            db.session.rollback()

    def test_modelo_carrito_vaciar(self, app):
        """Vaciar el carrito elimina todos los ítems."""
        with app.app_context():
            u = Usuario.query.filter_by(email='juan@prod.com').first()
            p = Producto.query.filter_by(nombre='Mouse Test').first()

            carrito = Carrito(usuario_id=u.id, activo=True)
            db.session.add(carrito)
            db.session.flush()

            carrito.agregar_producto(p, 1)
            assert not carrito.esta_vacio

            carrito.vaciar()
            db.session.flush()
            assert carrito.esta_vacio
            db.session.rollback()


# ── Tests de Pedidos ──────────────────────────────────────────────────────────

class TestPedidos:
    """Pruebas del módulo de pedidos."""

    def test_numero_pedido_unico(self, app):
        """El número de pedido generado es único cada vez."""
        with app.app_context():
            num1 = Pedido.generar_numero_pedido()
            num2 = Pedido.generar_numero_pedido()
            assert num1 != num2
            assert num1.startswith('PED-')

    def test_historial_requiere_auth(self, app):
        """Ver historial de pedidos requiere autenticación."""
        with app.test_client() as c:
            resp = c.get('/pedidos/historial', follow_redirects=False)
            assert resp.status_code in [301, 302]

    def test_estados_pedido(self, app):
        """Los estados del pedido son los correctos."""
        with app.app_context():
            u = Usuario.query.filter_by(email='juan@prod.com').first()
            pedido = Pedido(
                numero_pedido=Pedido.generar_numero_pedido(),
                usuario_id=u.id,
                total=Decimal('100.00'),
                estado=Pedido.ESTADO_PENDIENTE_PAGO,
            )
            db.session.add(pedido)
            db.session.commit()

            assert pedido.puede_pagar is True
            assert pedido.etiqueta_estado == 'Pendiente de Pago'
            assert pedido.clase_estado == 'warning'

            pedido.estado = Pedido.ESTADO_PAGADO
            assert pedido.puede_pagar is False
            assert pedido.etiqueta_estado == 'Pagado'

            db.session.delete(pedido)
            db.session.commit()

    def test_detalle_pedido_otro_usuario(self, app):
        """Un usuario no puede ver el pedido de otro usuario."""
        with app.app_context():
            admin = Usuario.query.filter_by(email='admin@prod.com').first()
            pedido = Pedido(
                numero_pedido=Pedido.generar_numero_pedido(),
                usuario_id=admin.id,
                total=Decimal('200.00'),
                estado=Pedido.ESTADO_PENDIENTE_PAGO,
            )
            db.session.add(pedido)
            db.session.commit()

            # Cliente intenta acceder al pedido del admin
            with app.test_client() as c:
                resp = c.get('/auth/login')
                html = resp.data.decode('utf-8')
                start = html.find('name="csrf_token" value="')
                token = ''
                if start != -1:
                    start += len('name="csrf_token" value="')
                    token = html[start:html.find('"', start)]

                c.post('/auth/login', data={
                    'email': 'juan@prod.com',
                    'contrasena': 'Juan1234!',
                    'csrf_token': token,
                }, follow_redirects=True)

                resp = c.get(f'/pedidos/{pedido.id}')
                assert resp.status_code == 404  # 404 porque filtra por usuario_id

            db.session.delete(pedido)
            db.session.commit()


# ── Tests de Pagos ────────────────────────────────────────────────────────────

class TestPagos:
    """Pruebas del módulo de pagos."""

    def test_modelo_metodo_pago(self, app):
        """El modelo MetodoPago funciona correctamente."""
        with app.app_context():
            metodo = MetodoPago.query.filter_by(nombre='QR Test').first()
            assert metodo is not None
            assert metodo.activo is True

    def test_modelo_comprobante_estado(self, app):
        """Los estados del comprobante son correctos."""
        with app.app_context():
            u = Usuario.query.filter_by(email='juan@prod.com').first()
            metodo = MetodoPago.query.filter_by(nombre='QR Test').first()

            pedido = Pedido(
                numero_pedido=Pedido.generar_numero_pedido(),
                usuario_id=u.id,
                total=Decimal('500.00'),
                estado=Pedido.ESTADO_PENDIENTE_VERIFICACION,
            )
            db.session.add(pedido)
            db.session.flush()

            comp = ComprobantePago(
                pedido_id=pedido.id,
                metodo_pago_id=metodo.id,
                imagen_comprobante='test_comprobante.jpg',
                monto=Decimal('500.00'),
                estado=ComprobantePago.ESTADO_PENDIENTE,
            )
            db.session.add(comp)
            db.session.commit()

            assert comp.etiqueta_estado == 'Pendiente de Revisión'
            assert comp.clase_estado == 'warning'

            comp.estado = ComprobantePago.ESTADO_APROBADO
            assert comp.etiqueta_estado == 'Aprobado'
            assert comp.clase_estado == 'success'

            db.session.delete(comp)
            db.session.delete(pedido)
            db.session.commit()

    def test_pago_requiere_auth(self, app):
        """El módulo de pago requiere autenticación."""
        with app.test_client() as c:
            resp = c.get('/pagos/pagar/1', follow_redirects=False)
            assert resp.status_code in [301, 302]
