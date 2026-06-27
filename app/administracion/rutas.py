"""
app/administracion/rutas.py - Panel de administración completo
"""

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required

from app import db
from app.administracion import bp
from app.utilidades.decoradores import requiere_admin
from app.modelos.usuario import Usuario
from app.modelos.rol import Rol
from app.modelos.categoria import Categoria
from app.modelos.producto import Producto
from app.modelos.pedido import Pedido
from app.modelos.pago import MetodoPago, ComprobantePago
from app.formularios import (
    FormularioCategoria, FormularioProducto, FormularioMetodoPago,
    FormularioRevisarComprobante, FormularioUsuarioAdmin
)
from app.utilidades.archivos import (
    guardar_imagen_producto, guardar_imagen_qr, eliminar_archivo
)


# ─── USUARIOS ─────────────────────────────────────────────────────────────────

@bp.route('/usuarios')
@login_required
@requiere_admin
def usuarios():
    """Lista todos los usuarios del sistema."""
    por_pagina = current_app.config.get('USUARIOS_POR_PAGINA', 10)
    pagina = request.args.get('pagina', 1, type=int)
    paginacion = Usuario.query.order_by(Usuario.creado_en.desc()).paginate(
        page=pagina, per_page=por_pagina, error_out=False
    )
    return render_template('administracion/usuarios/listar.html',
                           titulo='Gestión de Usuarios',
                           usuarios=paginacion.items,
                           paginacion=paginacion)


@bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@requiere_admin
def crear_usuario():
    """Crea un nuevo usuario desde el panel admin."""
    form = FormularioUsuarioAdmin()
    roles = Rol.query.all()
    form.rol_id.choices = [(r.id, r.nombre.capitalize()) for r in roles]

    if form.validate_on_submit():
        # Verificar email único
        if Usuario.query.filter_by(email=form.email.data.lower()).first():
            flash('Ya existe un usuario con ese correo.', 'danger')
            return render_template('administracion/usuarios/formulario.html',
                                   form=form, titulo='Crear Usuario')

        usuario = Usuario(
            nombre=form.nombre.data.strip(),
            apellido=form.apellido.data.strip(),
            email=form.email.data.lower().strip(),
            telefono=form.telefono.data.strip() if form.telefono.data else None,
            rol_id=form.rol_id.data,
            activo=form.activo.data,
        )
        if form.contrasena.data:
            usuario.establecer_contrasena(form.contrasena.data)
        else:
            usuario.establecer_contrasena('Temporal123!')

        db.session.add(usuario)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('administracion.usuarios'))

    return render_template('administracion/usuarios/formulario.html',
                           form=form, titulo='Crear Usuario')


@bp.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_admin
def editar_usuario(usuario_id):
    """Edita un usuario existente."""
    usuario = Usuario.query.get_or_404(usuario_id)
    roles = Rol.query.all()
    form = FormularioUsuarioAdmin(obj=usuario)
    form.rol_id.choices = [(r.id, r.nombre.capitalize()) for r in roles]

    if form.validate_on_submit():
        usuario.nombre = form.nombre.data.strip()
        usuario.apellido = form.apellido.data.strip()
        usuario.email = form.email.data.lower().strip()
        usuario.telefono = form.telefono.data.strip() if form.telefono.data else None
        usuario.rol_id = form.rol_id.data
        usuario.activo = form.activo.data
        if form.contrasena.data:
            usuario.establecer_contrasena(form.contrasena.data)
        db.session.commit()
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('administracion.usuarios'))

    return render_template('administracion/usuarios/formulario.html',
                           form=form, titulo='Editar Usuario', usuario=usuario)


@bp.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
@requiere_admin
def eliminar_usuario(usuario_id):
    """Elimina un usuario del sistema."""
    from flask_login import current_user
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propio usuario.', 'danger')
        return redirect(url_for('administracion.usuarios'))

    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('administracion.usuarios'))


# ─── CATEGORÍAS ───────────────────────────────────────────────────────────────

@bp.route('/categorias')
@login_required
@requiere_admin
def categorias():
    """Lista todas las categorías."""
    todas = Categoria.query.order_by(Categoria.nombre).all()
    return render_template('administracion/categorias/listar.html',
                           titulo='Gestión de Categorías',
                           categorias=todas)


@bp.route('/categorias/crear', methods=['GET', 'POST'])
@login_required
@requiere_admin
def crear_categoria():
    """Crea una nueva categoría."""
    form = FormularioCategoria()

    if form.validate_on_submit():
        categoria = Categoria(
            nombre=form.nombre.data.strip(),
            descripcion=form.descripcion.data.strip() if form.descripcion.data else None,
            activa=form.activa.data,
        )
        categoria.slug = categoria.generar_slug()
        db.session.add(categoria)
        db.session.commit()
        flash('Categoría creada exitosamente.', 'success')
        return redirect(url_for('administracion.categorias'))

    return render_template('administracion/categorias/formulario.html',
                           form=form, titulo='Crear Categoría')


@bp.route('/categorias/<int:categoria_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_admin
def editar_categoria(categoria_id):
    """Edita una categoría existente."""
    categoria = Categoria.query.get_or_404(categoria_id)
    form = FormularioCategoria(obj=categoria)

    if form.validate_on_submit():
        categoria.nombre = form.nombre.data.strip()
        categoria.descripcion = form.descripcion.data.strip() if form.descripcion.data else None
        categoria.activa = form.activa.data
        categoria.slug = categoria.generar_slug()
        db.session.commit()
        flash('Categoría actualizada exitosamente.', 'success')
        return redirect(url_for('administracion.categorias'))

    return render_template('administracion/categorias/formulario.html',
                           form=form, titulo='Editar Categoría', categoria=categoria)


@bp.route('/categorias/<int:categoria_id>/eliminar', methods=['POST'])
@login_required
@requiere_admin
def eliminar_categoria(categoria_id):
    """Elimina una categoría (solo si no tiene productos)."""
    categoria = Categoria.query.get_or_404(categoria_id)

    if categoria.total_productos > 0:
        flash('No puedes eliminar una categoría que tiene productos asociados.', 'danger')
        return redirect(url_for('administracion.categorias'))

    db.session.delete(categoria)
    db.session.commit()
    flash('Categoría eliminada exitosamente.', 'success')
    return redirect(url_for('administracion.categorias'))


# ─── PRODUCTOS ────────────────────────────────────────────────────────────────

@bp.route('/productos')
@login_required
@requiere_admin
def productos():
    """Lista todos los productos."""
    por_pagina = current_app.config.get('PRODUCTOS_POR_PAGINA', 12)
    pagina = request.args.get('pagina', 1, type=int)
    q = request.args.get('q', '').strip()

    query = Producto.query
    if q:
        query = query.filter(Producto.nombre.ilike(f'%{q}%'))

    paginacion = query.order_by(Producto.creado_en.desc()).paginate(
        page=pagina, per_page=por_pagina, error_out=False
    )
    return render_template('administracion/productos/listar.html',
                           titulo='Gestión de Productos',
                           productos=paginacion.items,
                           paginacion=paginacion,
                           q=q)


@bp.route('/productos/crear', methods=['GET', 'POST'])
@login_required
@requiere_admin
def crear_producto():
    """Crea un nuevo producto."""
    form = FormularioProducto()
    categorias = Categoria.query.filter_by(activa=True).order_by(Categoria.nombre).all()
    form.categoria_id.choices = [(c.id, c.nombre) for c in categorias]

    if form.validate_on_submit():
        nombre_imagen = None
        if form.imagen.data and form.imagen.data.filename:
            nombre_imagen = guardar_imagen_producto(form.imagen.data)

        producto = Producto(
            nombre=form.nombre.data.strip(),
            descripcion=form.descripcion.data.strip() if form.descripcion.data else None,
            precio=form.precio.data,
            stock=form.stock.data,
            categoria_id=form.categoria_id.data,
            activo=form.activo.data,
            destacado=form.destacado.data,
            imagen=nombre_imagen,
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('administracion.productos'))

    return render_template('administracion/productos/formulario.html',
                           form=form, titulo='Crear Producto')


@bp.route('/productos/<int:producto_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_admin
def editar_producto(producto_id):
    """Edita un producto existente."""
    producto = Producto.query.get_or_404(producto_id)
    form = FormularioProducto(obj=producto)
    categorias = Categoria.query.filter_by(activa=True).order_by(Categoria.nombre).all()
    form.categoria_id.choices = [(c.id, c.nombre) for c in categorias]

    if form.validate_on_submit():
        if form.imagen.data and form.imagen.data.filename:
            # Eliminar imagen anterior
            if producto.imagen:
                eliminar_archivo(producto.imagen, current_app.config['UPLOAD_FOLDER_PRODUCTOS'])
            producto.imagen = guardar_imagen_producto(form.imagen.data)

        producto.nombre = form.nombre.data.strip()
        producto.descripcion = form.descripcion.data.strip() if form.descripcion.data else None
        producto.precio = form.precio.data
        producto.stock = form.stock.data
        producto.categoria_id = form.categoria_id.data
        producto.activo = form.activo.data
        producto.destacado = form.destacado.data
        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('administracion.productos'))

    return render_template('administracion/productos/formulario.html',
                           form=form, titulo='Editar Producto', producto=producto)


@bp.route('/productos/<int:producto_id>/eliminar', methods=['POST'])
@login_required
@requiere_admin
def eliminar_producto(producto_id):
    """Elimina un producto del sistema."""
    producto = Producto.query.get_or_404(producto_id)

    if producto.imagen:
        eliminar_archivo(producto.imagen, current_app.config['UPLOAD_FOLDER_PRODUCTOS'])

    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente.', 'success')
    return redirect(url_for('administracion.productos'))


# ─── PEDIDOS ──────────────────────────────────────────────────────────────────

@bp.route('/pedidos')
@login_required
@requiere_admin
def pedidos():
    """Lista todos los pedidos del sistema."""
    por_pagina = current_app.config.get('PEDIDOS_POR_PAGINA', 10)
    pagina = request.args.get('pagina', 1, type=int)
    estado_filtro = request.args.get('estado', '')

    query = Pedido.query
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)

    paginacion = query.order_by(Pedido.creado_en.desc()).paginate(
        page=pagina, per_page=por_pagina, error_out=False
    )
    return render_template('administracion/pedidos/listar.html',
                           titulo='Gestión de Pedidos',
                           pedidos=paginacion.items,
                           paginacion=paginacion,
                           estado_filtro=estado_filtro,
                           estados=Pedido.ETIQUETAS_ESTADO)


@bp.route('/pedidos/<int:pedido_id>')
@login_required
@requiere_admin
def detalle_pedido(pedido_id):
    """Detalle de un pedido desde el panel admin."""
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('administracion/pedidos/detalle.html',
                           titulo=f'Pedido {pedido.numero_pedido}',
                           pedido=pedido)


@bp.route('/pedidos/<int:pedido_id>/estado', methods=['POST'])
@login_required
@requiere_admin
def cambiar_estado_pedido(pedido_id):
    """Cambia el estado de un pedido manualmente."""
    pedido = Pedido.query.get_or_404(pedido_id)
    nuevo_estado = request.form.get('estado')

    if nuevo_estado not in Pedido.ESTADOS:
        flash('Estado inválido.', 'danger')
        return redirect(url_for('administracion.detalle_pedido', pedido_id=pedido.id))

    pedido.estado = nuevo_estado
    db.session.commit()
    flash(f'Estado del pedido actualizado a "{pedido.etiqueta_estado}".', 'success')
    return redirect(url_for('administracion.detalle_pedido', pedido_id=pedido.id))


# ─── MÉTODOS DE PAGO ──────────────────────────────────────────────────────────

@bp.route('/metodos-pago')
@login_required
@requiere_admin
def metodos_pago():
    """Lista todos los métodos de pago."""
    metodos = MetodoPago.query.order_by(MetodoPago.nombre).all()
    return render_template('administracion/pagos/metodos_listar.html',
                           titulo='Métodos de Pago',
                           metodos=metodos)


@bp.route('/metodos-pago/crear', methods=['GET', 'POST'])
@login_required
@requiere_admin
def crear_metodo_pago():
    """Crea un nuevo método de pago."""
    form = FormularioMetodoPago()

    if form.validate_on_submit():
        nombre_qr = None
        if form.imagen_qr.data and form.imagen_qr.data.filename:
            nombre_qr = guardar_imagen_qr(form.imagen_qr.data)

        metodo = MetodoPago(
            nombre=form.nombre.data.strip(),
            descripcion=form.descripcion.data.strip() if form.descripcion.data else None,
            titular=form.titular.data.strip() if form.titular.data else None,
            numero_cuenta=form.numero_cuenta.data.strip() if form.numero_cuenta.data else None,
            imagen_qr=nombre_qr,
            activo=form.activo.data,
        )
        db.session.add(metodo)
        db.session.commit()
        flash('Método de pago creado exitosamente.', 'success')
        return redirect(url_for('administracion.metodos_pago'))

    return render_template('administracion/pagos/metodo_formulario.html',
                           form=form, titulo='Crear Método de Pago')


@bp.route('/metodos-pago/<int:metodo_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_admin
def editar_metodo_pago(metodo_id):
    """Edita un método de pago existente."""
    metodo = MetodoPago.query.get_or_404(metodo_id)
    form = FormularioMetodoPago(obj=metodo)

    if form.validate_on_submit():
        if form.imagen_qr.data and form.imagen_qr.data.filename:
            if metodo.imagen_qr:
                eliminar_archivo(metodo.imagen_qr, current_app.config['UPLOAD_FOLDER_QR'])
            metodo.imagen_qr = guardar_imagen_qr(form.imagen_qr.data)

        metodo.nombre = form.nombre.data.strip()
        metodo.descripcion = form.descripcion.data.strip() if form.descripcion.data else None
        metodo.titular = form.titular.data.strip() if form.titular.data else None
        metodo.numero_cuenta = form.numero_cuenta.data.strip() if form.numero_cuenta.data else None
        metodo.activo = form.activo.data
        db.session.commit()
        flash('Método de pago actualizado exitosamente.', 'success')
        return redirect(url_for('administracion.metodos_pago'))

    return render_template('administracion/pagos/metodo_formulario.html',
                           form=form, titulo='Editar Método de Pago', metodo=metodo)


@bp.route('/metodos-pago/<int:metodo_id>/eliminar', methods=['POST'])
@login_required
@requiere_admin
def eliminar_metodo_pago(metodo_id):
    """Elimina un método de pago."""
    metodo = MetodoPago.query.get_or_404(metodo_id)

    if metodo.imagen_qr:
        eliminar_archivo(metodo.imagen_qr, current_app.config['UPLOAD_FOLDER_QR'])

    db.session.delete(metodo)
    db.session.commit()
    flash('Método de pago eliminado exitosamente.', 'success')
    return redirect(url_for('administracion.metodos_pago'))


# ─── COMPROBANTES ─────────────────────────────────────────────────────────────

@bp.route('/comprobantes')
@login_required
@requiere_admin
def comprobantes():
    """Lista todos los comprobantes de pago pendientes de revisión."""
    estado_filtro = request.args.get('estado', 'pendiente')
    por_pagina = 10
    pagina = request.args.get('pagina', 1, type=int)

    query = ComprobantePago.query
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)

    paginacion = query.order_by(ComprobantePago.creado_en.desc()).paginate(
        page=pagina, per_page=por_pagina, error_out=False
    )
    return render_template('administracion/pagos/comprobantes_listar.html',
                           titulo='Revisión de Comprobantes',
                           comprobantes=paginacion.items,
                           paginacion=paginacion,
                           estado_filtro=estado_filtro)


@bp.route('/comprobantes/<int:comprobante_id>/revisar', methods=['GET', 'POST'])
@login_required
@requiere_admin
def revisar_comprobante(comprobante_id):
    """Aprueba o rechaza un comprobante de pago."""
    from flask_login import current_user
    comprobante = ComprobantePago.query.get_or_404(comprobante_id)
    form = FormularioRevisarComprobante()

    if form.validate_on_submit():
        accion = form.accion.data
        comprobante.estado = accion
        comprobante.observaciones = form.observaciones.data
        comprobante.revisado_por = current_user.id
        comprobante.revisado_en = datetime.utcnow()

        # Actualizar estado del pedido según la acción
        pedido = comprobante.pedido
        if accion == ComprobantePago.ESTADO_APROBADO:
            pedido.estado = Pedido.ESTADO_PAGADO
            flash('Pago aprobado. El pedido ha sido marcado como Pagado.', 'success')
        else:
            pedido.estado = Pedido.ESTADO_PENDIENTE_PAGO
            flash('Pago rechazado. El pedido vuelve a Pendiente de Pago.', 'warning')

        db.session.commit()
        return redirect(url_for('administracion.comprobantes'))

    return render_template('administracion/pagos/revisar_comprobante.html',
                           titulo='Revisar Comprobante',
                           comprobante=comprobante,
                           form=form)
