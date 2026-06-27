"""
app/modelos/carrito.py - Modelos de Carrito y Detalle de Carrito
"""

from datetime import datetime
from app import db


class Carrito(db.Model):
    """Modelo que representa el carrito de compras de un usuario."""

    __tablename__ = 'carritos'

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    detalles = db.relationship('DetalleCarrito', backref='carrito', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Carrito usuario_id={self.usuario_id}>'

    @property
    def total_items(self):
        """Retorna el total de ítems (unidades) en el carrito."""
        return sum(detalle.cantidad for detalle in self.detalles.all())

    @property
    def total(self):
        """Retorna el total monetario del carrito."""
        return sum(detalle.subtotal for detalle in self.detalles.all())

    @property
    def esta_vacio(self):
        """Retorna True si el carrito está vacío."""
        return self.detalles.count() == 0

    def agregar_producto(self, producto, cantidad=1):
        """Agrega un producto al carrito o actualiza su cantidad."""
        detalle = self.detalles.filter_by(producto_id=producto.id).first()
        if detalle:
            # Validar stock disponible
            nueva_cantidad = detalle.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                return False, 'No hay suficiente stock disponible.'
            detalle.cantidad = nueva_cantidad
        else:
            if cantidad > producto.stock:
                return False, 'No hay suficiente stock disponible.'
            detalle = DetalleCarrito(
                carrito_id=self.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            db.session.add(detalle)
        return True, 'Producto agregado al carrito.'

    def eliminar_producto(self, producto_id):
        """Elimina un producto del carrito."""
        detalle = self.detalles.filter_by(producto_id=producto_id).first()
        if detalle:
            db.session.delete(detalle)
            return True
        return False

    def vaciar(self):
        """Elimina todos los productos del carrito."""
        for detalle in self.detalles.all():
            db.session.delete(detalle)

    def to_dict(self):
        """Serializa el carrito a diccionario."""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'total_items': self.total_items,
            'total': float(self.total),
            'detalles': [d.to_dict() for d in self.detalles.all()],
        }


class DetalleCarrito(db.Model):
    """Modelo que representa un ítem dentro del carrito de compras."""

    __tablename__ = 'detalle_carrito'

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carrito_id = db.Column(db.Integer, db.ForeignKey('carritos.id'), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Índice único para evitar duplicados
    __table_args__ = (
        db.UniqueConstraint('carrito_id', 'producto_id', name='uq_carrito_producto'),
    )

    def __repr__(self):
        return f'<DetalleCarrito carrito={self.carrito_id} producto={self.producto_id}>'

    @property
    def subtotal(self):
        """Retorna el subtotal del ítem."""
        return float(self.precio_unitario) * self.cantidad

    def to_dict(self):
        """Serializa el detalle a diccionario."""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto.nombre if self.producto else None,
            'producto_imagen': self.producto.imagen_url if self.producto else None,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': self.subtotal,
        }
