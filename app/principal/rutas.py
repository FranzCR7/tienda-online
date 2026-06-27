"""
app/principal/rutas.py - Rutas de la página principal
"""

from flask import render_template
from app.principal import bp
from app.modelos.producto import Producto
from app.modelos.categoria import Categoria


@bp.route('/')
@bp.route('/inicio')
def index():
    """Página de inicio de la tienda."""
    productos_destacados = Producto.query.filter_by(activo=True, destacado=True).limit(8).all()
    productos_recientes = Producto.query.filter_by(activo=True).order_by(
        Producto.creado_en.desc()
    ).limit(8).all()
    categorias = Categoria.query.filter_by(activa=True).all()

    return render_template('principal/index.html',
                           titulo='Inicio',
                           productos_destacados=productos_destacados,
                           productos_recientes=productos_recientes,
                           categorias=categorias)


@bp.route('/acerca-de')
def acerca_de():
    """Página de información sobre la tienda."""
    return render_template('principal/acerca_de.html', titulo='Acerca de')
