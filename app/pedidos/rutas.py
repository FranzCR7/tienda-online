"""
app/pedidos/rutas.py - Rutas del módulo de Pedidos
"""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app import db
from app.pedidos import bp
from app.modelos.pedido import Pedido, DetallePedido
from app.modelos.carrito import Carrito
from app.modelos.producto import Producto
from app.formularios import FormularioPedido


@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """Crea un pedido a partir del carrito activo."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, activo=True).first()

    if not carrito or carrito.esta_vacio:
        flash('Tu carrito está vacío. Agrega productos antes de realizar un pedido.', 'warning')
        return redirect(url_for('carrito.ver'))

    form = FormularioPedido()

    if form.validate_on_submit():
        # Verificar stock de todos los productos antes de crear el pedido
        detalles_carrito = carrito.detalles.all()
        for detalle in detalles_carrito:
            producto = Producto.query.get(detalle.producto_id)
            if not producto or not producto.activo:
                flash(f'El producto "{detalle.producto.nombre}" ya no está disponible.', 'danger')
                return redirect(url_for('carrito.ver'))
            if producto.stock < detalle.cantidad:
                flash(
                    f'No hay suficiente stock de "{producto.nombre}". '
                    f'Disponible: {producto.stock} unidades.',
                    'danger'
                )
                return redirect(url_for('carrito.ver'))

        # Calcular total
        total = carrito.total

        # Crear el pedido
        pedido = Pedido(
            numero_pedido=Pedido.generar_numero_pedido(),
            usuario_id=current_user.id,
            estado=Pedido.ESTADO_PENDIENTE_PAGO,
            total=total,
            direccion_entrega=form.direccion_entrega.data.strip() if form.direccion_entrega.data else current_user.direccion,
            notas=form.notas.data.strip() if form.notas.data else None,
        )
        db.session.add(pedido)
        db.session.flush()  # Para obtener el ID del pedido

        # Crear detalles del pedido y descontar stock
        for detalle in detalles_carrito:
            producto = Producto.query.get(detalle.producto_id)
            detalle_pedido = DetallePedido(
                pedido_id=pedido.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal,
            )
            db.session.add(detalle_pedido)

            # Descontar stock
            producto.reducir_stock(detalle.cantidad)

        # Desactivar carrito
        carrito.activo = False

        db.session.commit()

        flash(f'¡Pedido #{pedido.numero_pedido} creado exitosamente! Ahora procede con el pago.', 'success')
        return redirect(url_for('pagos.seleccionar_metodo', pedido_id=pedido.id))

    return render_template('pedidos/crear.html',
                           titulo='Confirmar Pedido',
                           carrito=carrito,
                           form=form)


@bp.route('/<int:pedido_id>')
@login_required
def detalle(pedido_id):
    """Detalle de un pedido del usuario."""
    pedido = Pedido.query.filter_by(
        id=pedido_id, usuario_id=current_user.id
    ).first_or_404()

    return render_template('pedidos/detalle.html',
                           titulo=f'Pedido {pedido.numero_pedido}',
                           pedido=pedido)


@bp.route('/historial')
@login_required
def historial():
    """Historial de pedidos del usuario."""
    por_pagina = current_app.config.get('PEDIDOS_POR_PAGINA', 10)
    pagina = request.args.get('pagina', 1, type=int)

    paginacion = Pedido.query.filter_by(
        usuario_id=current_user.id
    ).order_by(Pedido.creado_en.desc()).paginate(
        page=pagina, per_page=por_pagina, error_out=False
    )

    return render_template('pedidos/historial.html',
                           titulo='Mis Pedidos',
                           pedidos=paginacion.items,
                           paginacion=paginacion)


@bp.route('/<int:pedido_id>/cancelar', methods=['POST'])
@login_required
def cancelar(pedido_id):
    """Cancela un pedido pendiente del usuario."""
    pedido = Pedido.query.filter_by(
        id=pedido_id, usuario_id=current_user.id
    ).first_or_404()

    if pedido.estado != Pedido.ESTADO_PENDIENTE_PAGO:
        flash('Solo puedes cancelar pedidos en estado "Pendiente de Pago".', 'warning')
        return redirect(url_for('pedidos.detalle', pedido_id=pedido.id))

    # Devolver stock
    for detalle in pedido.detalles.all():
        producto = Producto.query.get(detalle.producto_id)
        if producto:
            producto.aumentar_stock(detalle.cantidad)

    pedido.estado = Pedido.ESTADO_CANCELADO
    db.session.commit()

    flash(f'Pedido #{pedido.numero_pedido} cancelado. El stock ha sido devuelto.', 'info')
    return redirect(url_for('pedidos.historial'))
