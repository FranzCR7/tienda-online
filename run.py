"""
run.py - Punto de entrada de la aplicación TiendaOnline
Uso: python run.py
"""

import os
from app import crear_app
from app import db
from app.modelos import *  # noqa: importar todos los modelos para migraciones

# Determinar entorno de ejecución
entorno = os.environ.get('FLASK_ENV', 'desarrollo')
app = crear_app(entorno)


@app.shell_context_processor
def hacer_contexto_shell():
    """Contexto disponible en `flask shell` para debugging."""
    from app.modelos.usuario import Usuario
    from app.modelos.rol import Rol
    from app.modelos.categoria import Categoria
    from app.modelos.producto import Producto
    from app.modelos.carrito import Carrito, DetalleCarrito
    from app.modelos.pedido import Pedido, DetallePedido
    from app.modelos.pago import MetodoPago, ComprobantePago
    return {
        'db': db,
        'Usuario': Usuario,
        'Rol': Rol,
        'Categoria': Categoria,
        'Producto': Producto,
        'Carrito': Carrito,
        'DetalleCarrito': DetalleCarrito,
        'Pedido': Pedido,
        'DetallePedido': DetallePedido,
        'MetodoPago': MetodoPago,
        'ComprobantePago': ComprobantePago,
    }


if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'desarrollo') == 'desarrollo'
    app.run(host='0.0.0.0', port=puerto, debug=debug)
