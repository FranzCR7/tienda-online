"""
app/modelos/__init__.py - Registro centralizado de todos los modelos
Importar todos los modelos aquí para que Flask-Migrate los detecte.
"""

from app.modelos.rol import Rol
from app.modelos.usuario import Usuario
from app.modelos.categoria import Categoria
from app.modelos.producto import Producto
from app.modelos.carrito import Carrito, DetalleCarrito
from app.modelos.pedido import Pedido, DetallePedido
from app.modelos.pago import MetodoPago, ComprobantePago

__all__ = [
    'Rol',
    'Usuario',
    'Categoria',
    'Producto',
    'Carrito',
    'DetalleCarrito',
    'Pedido',
    'DetallePedido',
    'MetodoPago',
    'ComprobantePago',
]
