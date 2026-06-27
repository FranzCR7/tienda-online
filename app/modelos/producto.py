"""
app/modelos/producto.py - Modelo de Producto
"""

from datetime import datetime
from app import db


class Producto(db.Model):
    """Modelo que representa los productos de la tienda."""

    __tablename__ = 'productos'

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    imagen = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    destacado = db.Column(db.Boolean, nullable=False, default=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False, index=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    detalles_carrito = db.relationship('DetalleCarrito', backref='producto', lazy='dynamic')
    detalles_pedido = db.relationship('DetallePedido', backref='producto', lazy='dynamic')

    def __repr__(self):
        return f'<Producto {self.nombre}>'

    @property
    def en_stock(self):
        """Retorna True si hay stock disponible."""
        return self.stock > 0

    @property
    def imagen_url(self):
        """Retorna la URL de la imagen del producto."""
        if self.imagen:
            return f'/static/uploads/productos/{self.imagen}'
        return '/static/img/producto-default.png'

    @property
    def precio_formateado(self):
        """Retorna el precio formateado."""
        return f'Bs. {float(self.precio):,.2f}'

    def reducir_stock(self, cantidad):
        """Reduce el stock del producto."""
        if self.stock >= cantidad:
            self.stock -= cantidad
            return True
        return False

    def aumentar_stock(self, cantidad):
        """Aumenta el stock del producto."""
        self.stock += cantidad

    @property
    def total_vendido(self):
        """Retorna el total de unidades vendidas."""
        from app.modelos.pedido import DetallePedido, Pedido
        from sqlalchemy import func
        resultado = db.session.query(
            func.sum(DetallePedido.cantidad)
        ).join(Pedido).filter(
            DetallePedido.producto_id == self.id,
            Pedido.estado.in_(['pagado'])
        ).scalar()
        return resultado or 0

    def to_dict(self):
        """Serializa el producto a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': float(self.precio),
            'stock': self.stock,
            'imagen_url': self.imagen_url,
            'activo': self.activo,
            'destacado': self.destacado,
            'categoria_id': self.categoria_id,
            'categoria': self.categoria.nombre if self.categoria else None,
            'en_stock': self.en_stock,
        }
