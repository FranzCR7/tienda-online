"""
app/carrito/rutas.py - Rutas del módulo de Carrito de Compras
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.carrito import bp
from app.modelos.carrito import Carrito, DetalleCarrito
from app.modelos.producto import Producto
from app.formularios import FormularioAgregarCarrito, FormularioActualizarCarrito


def obtener_o_crear_carrito():
    """Obtiene el carrito activo del usuario o crea uno nuevo."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, activo=True).first()
    if not carrito:
        carrito = Carrito(usuario_id=current_user.id, activo=True)
        db.session.add(carrito)
        db.session.commit()
    return carrito


@bp.route('/')
@login_required
def ver():
    """Vista del carrito de compras."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, activo=True).first()
    form_actualizar = FormularioActualizarCarrito()

    return render_template('carrito/ver.html',
                           titulo='Mi Carrito',
                           carrito=carrito,
                           form_actualizar=form_actualizar)


@bp.route('/agregar', methods=['POST'])
@login_required
def agregar():
    """Agrega un producto al carrito."""
    form = FormularioAgregarCarrito()

    if form.validate_on_submit():
        producto_id = int(form.producto_id.data)
        cantidad = form.cantidad.data

        producto = Producto.query.filter_by(id=producto_id, activo=True).first()
        if not producto:
            flash('Producto no encontrado.', 'danger')
            return redirect(url_for('productos.listar'))

        carrito = obtener_o_crear_carrito()
        exito, mensaje = carrito.agregar_producto(producto, cantidad)
        db.session.commit()

        if exito:
            flash(mensaje, 'success')
        else:
            flash(mensaje, 'warning')
    else:
        flash('Error al agregar el producto. Intenta de nuevo.', 'danger')

    # Redirigir al referrer o al carrito
    siguiente = request.referrer or url_for('carrito.ver')
    return redirect(siguiente)


@bp.route('/actualizar/<int:detalle_id>', methods=['POST'])
@login_required
def actualizar(detalle_id):
    """Actualiza la cantidad de un ítem del carrito."""
    form = FormularioActualizarCarrito()

    if form.validate_on_submit():
        carrito = Carrito.query.filter_by(usuario_id=current_user.id, activo=True).first()
        if not carrito:
            flash('Carrito no encontrado.', 'danger')
            return redirect(url_for('carrito.ver'))

        detalle = DetalleCarrito.query.filter_by(
            id=detalle_id, carrito_id=carrito.id
        ).first()

        if not detalle:
            flash('Ítem no encontrado en el carrito.', 'danger')
            return redirect(url_for('carrito.ver'))

        nueva_cantidad = form.cantidad.data
        if nueva_cantidad > detalle.producto.stock:
            flash(f'Solo hay {detalle.producto.stock} unidades disponibles.', 'warning')
        else:
            detalle.cantidad = nueva_cantidad
            db.session.commit()
            flash('Carrito actualizado.', 'success')
    else:
        flash('Cantidad inválida.', 'danger')

    return redirect(url_for('carrito.ver'))


@bp.route('/eliminar/<int:detalle_id>', methods=['POST'])
@login_required
def eliminar(detalle_id):
    """Elimina un ítem del carrito."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, activo=True).first()
    if not carrito:
        flash('Carrito no encontrado.', 'danger')
        return redirect(url_for('carrito.ver'))

    detalle = DetalleCarrito.query.filter_by(
        id=detalle_id, carrito_id=carrito.id
    ).first()

    if detalle:
        db.session.delete(detalle)
        db.session.commit()
        flash('Producto eliminado del carrito.', 'success')
    else:
        flash('Ítem no encontrado.', 'warning')

    return redirect(url_for('carrito.ver'))


@bp.route('/vaciar', methods=['POST'])
@login_required
def vaciar():
    """Vacía completamente el carrito."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, activo=True).first()
    if carrito:
        carrito.vaciar()
        db.session.commit()
        flash('Carrito vaciado correctamente.', 'info')

    return redirect(url_for('carrito.ver'))


@bp.route('/contar')
@login_required
def contar():
    """Retorna el número de ítems en el carrito (para AJAX)."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, activo=True).first()
    total = carrito.total_items if carrito else 0
    return jsonify({'total': total})
