"""
app/pagos/rutas.py - Rutas del módulo de Pagos QR
"""

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app import db
from app.pagos import bp
from app.modelos.pedido import Pedido
from app.modelos.pago import MetodoPago, ComprobantePago
from app.formularios import FormularioSubirComprobante
from app.utilidades.archivos import guardar_comprobante


@bp.route('/pagar/<int:pedido_id>', methods=['GET', 'POST'])
@login_required
def seleccionar_metodo(pedido_id):
    """Selección de método de pago QR y subida de comprobante."""
    pedido = Pedido.query.filter_by(
        id=pedido_id, usuario_id=current_user.id
    ).first_or_404()

    if not pedido.puede_pagar:
        flash('Este pedido no puede recibir un pago en este momento.', 'warning')
        return redirect(url_for('pedidos.detalle', pedido_id=pedido.id))

    metodos = MetodoPago.query.filter_by(activo=True).all()
    if not metodos:
        flash('No hay métodos de pago disponibles en este momento.', 'warning')
        return redirect(url_for('pedidos.detalle', pedido_id=pedido.id))

    form = FormularioSubirComprobante()
    form.metodo_pago_id.choices = [(m.id, m.nombre) for m in metodos]

    # Método seleccionado para mostrar QR
    metodo_id = request.args.get('metodo', metodos[0].id, type=int)
    metodo_seleccionado = MetodoPago.query.get(metodo_id) or metodos[0]

    if form.validate_on_submit():
        metodo = MetodoPago.query.get(form.metodo_pago_id.data)
        if not metodo or not metodo.activo:
            flash('Método de pago no válido.', 'danger')
            return redirect(url_for('pagos.seleccionar_metodo', pedido_id=pedido.id))

        # Guardar comprobante
        nombre_archivo = guardar_comprobante(form.comprobante.data)
        if not nombre_archivo:
            flash('Error al guardar el comprobante. Verifica el formato del archivo.', 'danger')
            return redirect(url_for('pagos.seleccionar_metodo', pedido_id=pedido.id))

        # Crear registro de comprobante
        comprobante = ComprobantePago(
            pedido_id=pedido.id,
            metodo_pago_id=metodo.id,
            imagen_comprobante=nombre_archivo,
            monto=pedido.total,
            estado=ComprobantePago.ESTADO_PENDIENTE,
        )
        db.session.add(comprobante)

        # Cambiar estado del pedido
        pedido.estado = Pedido.ESTADO_PENDIENTE_VERIFICACION
        db.session.commit()

        flash(
            '¡Comprobante subido exitosamente! Tu pago está pendiente de verificación por el administrador.',
            'success'
        )
        return redirect(url_for('pedidos.detalle', pedido_id=pedido.id))

    return render_template('pagos/pagar.html',
                           titulo='Realizar Pago',
                           pedido=pedido,
                           metodos=metodos,
                           metodo_seleccionado=metodo_seleccionado,
                           form=form)


@bp.route('/comprobante/<int:comprobante_id>')
@login_required
def ver_comprobante(comprobante_id):
    """Visualiza un comprobante de pago."""
    comprobante = ComprobantePago.query.get_or_404(comprobante_id)

    # Solo el dueño del pedido o el admin puede ver el comprobante
    if not current_user.es_administrador and comprobante.pedido.usuario_id != current_user.id:
        from flask import abort
        abort(403)

    return render_template('pagos/comprobante.html',
                           titulo='Comprobante de Pago',
                           comprobante=comprobante)
