"""
app/dashboard/rutas.py - Rutas del Dashboard Administrativo con estadísticas
"""

from flask import render_template, jsonify
from flask_login import login_required
from sqlalchemy import func, extract

from app import db
from app.dashboard import bp
from app.utilidades.decoradores import requiere_admin
from app.modelos.usuario import Usuario
from app.modelos.producto import Producto
from app.modelos.pedido import Pedido, DetallePedido
from app.modelos.pago import ComprobantePago
from app.modelos.categoria import Categoria


@bp.route('/')
@login_required
@requiere_admin
def index():
    """Panel principal del dashboard administrativo."""

    # Estadísticas generales
    total_usuarios = Usuario.query.count()
    total_productos = Producto.query.filter_by(activo=True).count()
    total_pedidos = Pedido.query.count()

    total_ventas = db.session.query(
        func.coalesce(func.sum(Pedido.total), 0)
    ).filter_by(estado='pagado').scalar()

    # Pedidos pendientes
    pedidos_pendientes_pago = Pedido.query.filter_by(estado='pendiente_pago').count()
    pedidos_pendientes_verificacion = Pedido.query.filter_by(estado='pendiente_verificacion').count()
    comprobantes_pendientes = ComprobantePago.query.filter_by(estado='pendiente').count()

    # Últimos 5 pedidos
    ultimos_pedidos = Pedido.query.order_by(Pedido.creado_en.desc()).limit(5).all()

    # Productos con bajo stock (menos de 5 unidades)
    productos_bajo_stock = Producto.query.filter(
        Producto.stock < 5, Producto.activo == True
    ).order_by(Producto.stock.asc()).limit(5).all()

    # Top 5 productos más vendidos
    top_productos = db.session.query(
        Producto.nombre,
        func.sum(DetallePedido.cantidad).label('total_vendido')
    ).join(DetallePedido, Producto.id == DetallePedido.producto_id
    ).join(Pedido, DetallePedido.pedido_id == Pedido.id
    ).filter(Pedido.estado == 'pagado'
    ).group_by(Producto.id, Producto.nombre
    ).order_by(func.sum(DetallePedido.cantidad).desc()
    ).limit(5).all()

    return render_template('dashboard/index.html',
                           titulo='Dashboard',
                           total_usuarios=total_usuarios,
                           total_productos=total_productos,
                           total_pedidos=total_pedidos,
                           total_ventas=float(total_ventas),
                           pedidos_pendientes_pago=pedidos_pendientes_pago,
                           pedidos_pendientes_verificacion=pedidos_pendientes_verificacion,
                           comprobantes_pendientes=comprobantes_pendientes,
                           ultimos_pedidos=ultimos_pedidos,
                           productos_bajo_stock=productos_bajo_stock,
                           top_productos=top_productos)


@bp.route('/api/ventas-por-mes')
@login_required
@requiere_admin
def api_ventas_por_mes():
    """API endpoint para el gráfico de ventas por mes (Chart.js)."""
    from datetime import datetime
    año_actual = datetime.utcnow().year

    resultados = db.session.query(
        extract('month', Pedido.creado_en).label('mes'),
        func.coalesce(func.sum(Pedido.total), 0).label('total')
    ).filter(
        extract('year', Pedido.creado_en) == año_actual,
        Pedido.estado == 'pagado'
    ).group_by(
        extract('month', Pedido.creado_en)
    ).order_by('mes').all()

    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                     'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    datos = {i: 0 for i in range(1, 13)}
    for fila in resultados:
        datos[int(fila.mes)] = float(fila.total)

    return jsonify({
        'labels': meses_nombres,
        'datos': [datos[i] for i in range(1, 13)],
        'año': año_actual,
    })


@bp.route('/api/pedidos-por-estado')
@login_required
@requiere_admin
def api_pedidos_por_estado():
    """API endpoint para el gráfico de pedidos por estado."""
    resultados = db.session.query(
        Pedido.estado,
        func.count(Pedido.id).label('total')
    ).group_by(Pedido.estado).all()

    etiquetas = []
    datos = []
    colores = {
        'pendiente_pago': '#ffc107',
        'pendiente_verificacion': '#0dcaf0',
        'pagado': '#198754',
        'cancelado': '#dc3545',
    }

    for fila in resultados:
        etiquetas.append(Pedido.ETIQUETAS_ESTADO.get(fila.estado, fila.estado))
        datos.append(fila.total)

    return jsonify({
        'labels': etiquetas,
        'datos': datos,
        'colores': [colores.get(fila.estado, '#6c757d') for fila in resultados],
    })


@bp.route('/api/productos-por-categoria')
@login_required
@requiere_admin
def api_productos_por_categoria():
    """API endpoint para el gráfico de productos por categoría."""
    resultados = db.session.query(
        Categoria.nombre,
        func.count(Producto.id).label('total')
    ).join(Producto, Categoria.id == Producto.categoria_id
    ).filter(Producto.activo == True
    ).group_by(Categoria.nombre
    ).order_by(func.count(Producto.id).desc()).all()

    return jsonify({
        'labels': [r.nombre for r in resultados],
        'datos': [r.total for r in resultados],
    })
