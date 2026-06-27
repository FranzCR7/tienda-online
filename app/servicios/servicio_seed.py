"""
app/servicios/servicio_seed.py - Poblar la base de datos con datos iniciales de ejemplo
"""

from app import db
from app.modelos.rol import Rol
from app.modelos.usuario import Usuario
from app.modelos.categoria import Categoria
from app.modelos.producto import Producto
from app.modelos.pago import MetodoPago


def poblar_base_datos():
    """Inserta datos de ejemplo en la base de datos."""

    # ── Roles ─────────────────────────────────────────────────────────────────
    rol_admin = Rol.query.filter_by(nombre='administrador').first()
    if not rol_admin:
        rol_admin = Rol(nombre='administrador', descripcion='Administrador del sistema')
        db.session.add(rol_admin)

    rol_cliente = Rol.query.filter_by(nombre='cliente').first()
    if not rol_cliente:
        rol_cliente = Rol(nombre='cliente', descripcion='Cliente de la tienda')
        db.session.add(rol_cliente)

    db.session.commit()

    # ── Usuarios ──────────────────────────────────────────────────────────────
    if not Usuario.query.filter_by(email='admin@tienda.com').first():
        admin = Usuario(
            nombre='Administrador',
            apellido='Sistema',
            email='admin@tienda.com',
            telefono='70000000',
            rol_id=rol_admin.id,
            activo=True,
        )
        admin.establecer_contrasena('Admin123!')
        db.session.add(admin)

    if not Usuario.query.filter_by(email='cliente@tienda.com').first():
        cliente = Usuario(
            nombre='Juan',
            apellido='Pérez',
            email='cliente@tienda.com',
            telefono='71234567',
            direccion='Av. Arce 123',
            ciudad='La Paz',
            rol_id=rol_cliente.id,
            activo=True,
        )
        cliente.establecer_contrasena('Cliente123!')
        db.session.add(cliente)

    db.session.commit()

    # ── Categorías ────────────────────────────────────────────────────────────
    categorias_data = [
        ('Electrónica', 'Dispositivos y gadgets electrónicos'),
        ('Ropa y Moda', 'Prendas de vestir y accesorios'),
        ('Hogar y Cocina', 'Artículos para el hogar'),
        ('Deportes', 'Equipos y artículos deportivos'),
        ('Libros', 'Libros y materiales educativos'),
        ('Juguetes', 'Juguetes y juegos para niños'),
    ]

    categorias = {}
    for nombre, descripcion in categorias_data:
        cat = Categoria.query.filter_by(nombre=nombre).first()
        if not cat:
            cat = Categoria(nombre=nombre, descripcion=descripcion, activa=True)
            cat.slug = cat.generar_slug()
            db.session.add(cat)
            db.session.flush()
        categorias[nombre] = cat

    db.session.commit()

    # ── Productos ─────────────────────────────────────────────────────────────
    productos_data = [
        ('Smartphone Samsung Galaxy A54', 'Teléfono inteligente con pantalla AMOLED 6.4", 8GB RAM, 256GB almacenamiento.', 1899.00, 15, 'Electrónica', True),
        ('Audífonos Bluetooth JBL', 'Audífonos inalámbricos con cancelación de ruido activa, 30 horas de batería.', 350.00, 25, 'Electrónica', True),
        ('Laptop Lenovo IdeaPad', 'Procesador Intel Core i5, 8GB RAM, 512GB SSD, pantalla 15.6".', 4500.00, 8, 'Electrónica', True),
        ('Camiseta Polo Clásica', 'Camiseta polo de algodón premium, disponible en múltiples colores.', 89.00, 50, 'Ropa y Moda', False),
        ('Jeans Skinny Premium', 'Pantalón de mezclilla stretch de alta calidad, corte skinny.', 149.00, 30, 'Ropa y Moda', False),
        ('Zapatillas Running', 'Zapatillas deportivas con tecnología de amortiguación avanzada.', 299.00, 20, 'Deportes', True),
        ('Cafetera Espresso', 'Cafetera automática con molinillo integrado, capacidad 1.2 litros.', 450.00, 12, 'Hogar y Cocina', True),
        ('Set de Sartenes', 'Juego de 3 sartenes antiadherentes de aluminio forjado.', 189.00, 18, 'Hogar y Cocina', False),
        ('Python para Todos', 'Libro de programación en Python para principiantes, 400 páginas.', 65.00, 40, 'Libros', False),
        ('Pelota de Fútbol', 'Pelota oficial de fútbol FIFA, material sintético de alta durabilidad.', 120.00, 35, 'Deportes', False),
        ('LEGO Ciudad 500 piezas', 'Set de construcción LEGO con más de 500 piezas, para mayores de 6 años.', 280.00, 15, 'Juguetes', True),
        ('Tablet Fire HD 8', 'Tablet de 8 pulgadas con 32GB, pantalla HD, ideal para entretenimiento.', 750.00, 10, 'Electrónica', True),
    ]

    for nombre, descripcion, precio, stock, cat_nombre, destacado in productos_data:
        if not Producto.query.filter_by(nombre=nombre).first():
            cat = categorias.get(cat_nombre)
            if cat:
                producto = Producto(
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    stock=stock,
                    categoria_id=cat.id,
                    activo=True,
                    destacado=destacado,
                )
                db.session.add(producto)

    db.session.commit()

    # ── Métodos de Pago ───────────────────────────────────────────────────────
    metodos_data = [
        ('QR Yape', 'Pago mediante código QR de Yape BCP', 'TiendaOnline', '70000000'),
        ('QR Banco Unión', 'Transferencia mediante código QR del Banco Unión', 'TiendaOnline S.R.L.', '4001234567'),
        ('QR BNB', 'Pago con código QR del Banco Nacional de Bolivia', 'TiendaOnline S.R.L.', '3001234567'),
        ('QR Mercantil Santa Cruz', 'Pago QR del Banco Mercantil Santa Cruz', 'TiendaOnline S.R.L.', '2001234567'),
    ]

    for nombre, descripcion, titular, numero in metodos_data:
        if not MetodoPago.query.filter_by(nombre=nombre).first():
            metodo = MetodoPago(
                nombre=nombre,
                descripcion=descripcion,
                titular=titular,
                numero_cuenta=numero,
                activo=True,
            )
            db.session.add(metodo)

    db.session.commit()
    print('✅ Datos de ejemplo insertados correctamente.')
