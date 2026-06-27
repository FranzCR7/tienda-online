"""
app/servicios/api_rest.py - API REST para Productos y Pedidos
Endpoints documentados con soporte JSON.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app import db
from app.modelos.producto import Producto
from app.modelos.pedido import Pedido
from app.modelos.categoria import Categoria
from app.utilidades.decoradores import requiere_admin

api = Blueprint('api', __name__, url_prefix='/api/v1')


def respuesta_ok(datos, codigo=200):
    """Retorna una respuesta JSON exitosa."""
    return jsonify({'ok': True, 'datos': datos}), codigo


def respuesta_error(mensaje, codigo=400):
    """Retorna una respuesta JSON de error."""
    return jsonify({'ok': False, 'error': mensaje}), codigo


# ─── PRODUCTOS API ─────────────────────────────────────────────────────────────

@api.route('/productos', methods=['GET'])
def api_listar_productos():
    """
    GET /api/v1/productos
    Lista todos los productos activos.
    Query params: q (búsqueda), categoria_id, pagina, por_pagina
    """
    q = request.args.get('q', '').strip()
    categoria_id = request.args.get('categoria_id', type=int)
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = min(request.args.get('por_pagina', 12, type=int), 50)

    query = Producto.query.filter_by(activo=True)
    if q:
        query = query.filter(
            Producto.nombre.ilike(f'%{q}%') | Producto.descripcion.ilike(f'%{q}%')
        )
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)

    paginacion = query.paginate(page=pagina, per_page=por_pagina, error_out=False)

    return respuesta_ok({
        'productos': [p.to_dict() for p in paginacion.items],
        'total': paginacion.total,
        'paginas': paginacion.pages,
        'pagina_actual': paginacion.page,
    })


@api.route('/productos/<int:producto_id>', methods=['GET'])
def api_obtener_producto(producto_id):
    """
    GET /api/v1/productos/<id>
    Obtiene el detalle de un producto específico.
    """
    producto = Producto.query.filter_by(id=producto_id, activo=True).first()
    if not producto:
        return respuesta_error('Producto no encontrado.', 404)
    return respuesta_ok(producto.to_dict())


@api.route('/productos', methods=['POST'])
@login_required
@requiere_admin
def api_crear_producto():
    """
    POST /api/v1/productos
    Crea un nuevo producto. Requiere autenticación de administrador.
    Body JSON: nombre, descripcion, precio, stock, categoria_id
    """
    datos = request.get_json()
    if not datos:
        return respuesta_error('Se requiere un cuerpo JSON.')

    campos_requeridos = ['nombre', 'precio', 'stock', 'categoria_id']
    for campo in campos_requeridos:
        if campo not in datos:
            return respuesta_error(f'El campo "{campo}" es obligatorio.')

    categoria = Categoria.query.get(datos['categoria_id'])
    if not categoria or not categoria.activa:
        return respuesta_error('Categoría no válida.')

    try:
        producto = Producto(
            nombre=str(datos['nombre']).strip(),
            descripcion=datos.get('descripcion', '').strip(),
            precio=float(datos['precio']),
            stock=int(datos['stock']),
            categoria_id=int(datos['categoria_id']),
            activo=datos.get('activo', True),
            destacado=datos.get('destacado', False),
        )
        db.session.add(producto)
        db.session.commit()
        return respuesta_ok(producto.to_dict(), 201)
    except (ValueError, TypeError) as e:
        return respuesta_error(f'Datos inválidos: {str(e)}')


@api.route('/productos/<int:producto_id>', methods=['PUT'])
@login_required
@requiere_admin
def api_actualizar_producto(producto_id):
    """
    PUT /api/v1/productos/<id>
    Actualiza un producto existente. Requiere autenticación de administrador.
    """
    producto = Producto.query.get(producto_id)
    if not producto:
        return respuesta_error('Producto no encontrado.', 404)

    datos = request.get_json()
    if not datos:
        return respuesta_error('Se requiere un cuerpo JSON.')

    try:
        if 'nombre' in datos:
            producto.nombre = str(datos['nombre']).strip()
        if 'descripcion' in datos:
            producto.descripcion = str(datos['descripcion']).strip()
        if 'precio' in datos:
            producto.precio = float(datos['precio'])
        if 'stock' in datos:
            producto.stock = int(datos['stock'])
        if 'categoria_id' in datos:
            categoria = Categoria.query.get(int(datos['categoria_id']))
            if not categoria:
                return respuesta_error('Categoría no válida.')
            producto.categoria_id = int(datos['categoria_id'])
        if 'activo' in datos:
            producto.activo = bool(datos['activo'])
        if 'destacado' in datos:
            producto.destacado = bool(datos['destacado'])

        db.session.commit()
        return respuesta_ok(producto.to_dict())
    except (ValueError, TypeError) as e:
        return respuesta_error(f'Datos inválidos: {str(e)}')


@api.route('/productos/<int:producto_id>', methods=['DELETE'])
@login_required
@requiere_admin
def api_eliminar_producto(producto_id):
    """
    DELETE /api/v1/productos/<id>
    Elimina un producto. Requiere autenticación de administrador.
    """
    producto = Producto.query.get(producto_id)
    if not producto:
        return respuesta_error('Producto no encontrado.', 404)

    db.session.delete(producto)
    db.session.commit()
    return respuesta_ok({'mensaje': f'Producto {producto_id} eliminado correctamente.'})


# ─── PEDIDOS API ───────────────────────────────────────────────────────────────

@api.route('/pedidos', methods=['GET'])
@login_required
def api_listar_pedidos():
    """
    GET /api/v1/pedidos
    Lista los pedidos del usuario autenticado (o todos si es admin).
    """
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = min(request.args.get('por_pagina', 10, type=int), 50)

    query = Pedido.query
    if not current_user.es_administrador:
        query = query.filter_by(usuario_id=current_user.id)

    paginacion = query.order_by(Pedido.creado_en.desc()).paginate(
        page=pagina, per_page=por_pagina, error_out=False
    )
    return respuesta_ok({
        'pedidos': [p.to_dict() for p in paginacion.items],
        'total': paginacion.total,
        'paginas': paginacion.pages,
        'pagina_actual': paginacion.page,
    })


@api.route('/pedidos/<int:pedido_id>', methods=['GET'])
@login_required
def api_obtener_pedido(pedido_id):
    """
    GET /api/v1/pedidos/<id>
    Obtiene el detalle de un pedido. Solo el dueño o el admin pueden verlo.
    """
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return respuesta_error('Pedido no encontrado.', 404)

    if not current_user.es_administrador and pedido.usuario_id != current_user.id:
        return respuesta_error('Acceso denegado.', 403)

    return respuesta_ok(pedido.to_dict())


@api.route('/pedidos', methods=['POST'])
@login_required
def api_crear_pedido():
    """
    POST /api/v1/pedidos
    Crea un pedido a partir del carrito activo del usuario.
    """
    from app.modelos.carrito import Carrito
    from app.modelos.pedido import DetallePedido

    carrito = Carrito.query.filter_by(usuario_id=current_user.id, activo=True).first()
    if not carrito or carrito.esta_vacio:
        return respuesta_error('El carrito está vacío.')

    datos = request.get_json() or {}

    total = carrito.total
    pedido = Pedido(
        numero_pedido=Pedido.generar_numero_pedido(),
        usuario_id=current_user.id,
        estado=Pedido.ESTADO_PENDIENTE_PAGO,
        total=total,
        direccion_entrega=datos.get('direccion_entrega', current_user.direccion),
        notas=datos.get('notas'),
    )
    db.session.add(pedido)
    db.session.flush()

    for detalle in carrito.detalles.all():
        producto = Producto.query.get(detalle.producto_id)
        if not producto or producto.stock < detalle.cantidad:
            db.session.rollback()
            return respuesta_error(f'Stock insuficiente para "{detalle.producto.nombre}".')

        dp = DetallePedido(
            pedido_id=pedido.id,
            producto_id=detalle.producto_id,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            subtotal=detalle.subtotal,
        )
        db.session.add(dp)
        producto.reducir_stock(detalle.cantidad)

    carrito.activo = False
    db.session.commit()

    return respuesta_ok(pedido.to_dict(), 201)
