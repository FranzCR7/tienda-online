"""
app/productos/rutas.py - Rutas del módulo de Productos (vista cliente)
"""

from flask import render_template, request, abort
from app.productos import bp
from app.modelos.producto import Producto
from app.modelos.categoria import Categoria
from app.formularios import FormularioAgregarCarrito, FormularioBuscarProducto


@bp.route('/')
def listar():
    """Lista de productos con búsqueda y filtros."""
    form = FormularioBuscarProducto(request.args)

    # Cargar categorías para el selector
    categorias = Categoria.query.filter_by(activa=True).all()
    form.categoria.choices = [(0, 'Todas las categorías')] + \
                              [(c.id, c.nombre) for c in categorias]

    # Construir query base
    query = Producto.query.filter_by(activo=True)

    # Filtro por búsqueda de texto
    termino = request.args.get('q', '').strip()
    if termino:
        query = query.filter(
            Producto.nombre.ilike(f'%{termino}%') |
            Producto.descripcion.ilike(f'%{termino}%')
        )

    # Filtro por categoría
    categoria_id = request.args.get('categoria', 0, type=int)
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)

    # Filtro por precio mínimo
    precio_min = request.args.get('precio_min', type=float)
    if precio_min is not None:
        query = query.filter(Producto.precio >= precio_min)

    # Filtro por precio máximo
    precio_max = request.args.get('precio_max', type=float)
    if precio_max is not None:
        query = query.filter(Producto.precio <= precio_max)

    # Ordenamiento
    orden = request.args.get('orden', 'reciente')
    if orden == 'precio_asc':
        query = query.order_by(Producto.precio.asc())
    elif orden == 'precio_desc':
        query = query.order_by(Producto.precio.desc())
    elif orden == 'nombre':
        query = query.order_by(Producto.nombre.asc())
    else:
        query = query.order_by(Producto.creado_en.desc())

    # Paginación
    from flask import current_app
    por_pagina = current_app.config.get('PRODUCTOS_POR_PAGINA', 12)
    pagina = request.args.get('pagina', 1, type=int)
    paginacion = query.paginate(page=pagina, per_page=por_pagina, error_out=False)

    return render_template('productos/listar.html',
                           titulo='Productos',
                           productos=paginacion.items,
                           paginacion=paginacion,
                           categorias=categorias,
                           form=form,
                           termino=termino,
                           categoria_id=categoria_id,
                           orden=orden)


@bp.route('/<int:producto_id>')
def detalle(producto_id):
    """Detalle de un producto específico."""
    producto = Producto.query.filter_by(id=producto_id, activo=True).first_or_404()

    # Productos relacionados (misma categoría)
    relacionados = Producto.query.filter(
        Producto.categoria_id == producto.categoria_id,
        Producto.id != producto.id,
        Producto.activo == True
    ).limit(4).all()

    form_carrito = FormularioAgregarCarrito()
    form_carrito.producto_id.data = producto.id

    return render_template('productos/detalle.html',
                           titulo=producto.nombre,
                           producto=producto,
                           relacionados=relacionados,
                           form_carrito=form_carrito)


@bp.route('/categoria/<int:categoria_id>')
def por_categoria(categoria_id):
    """Productos filtrados por categoría."""
    categoria = Categoria.query.filter_by(id=categoria_id, activa=True).first_or_404()
    return render_template('productos/listar.html',
                           titulo=f'Categoría: {categoria.nombre}',
                           categoria_activa=categoria,
                           categoria_id=categoria_id)
