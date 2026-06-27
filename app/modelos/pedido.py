"""
app/modelos/pedido.py - Modelos de Pedido y Detalle de Pedido
"""

from datetime import datetime
from app import db


class Pedido(db.Model):
    """Modelo que representa un pedido de compra."""

    __tablename__ = 'pedidos'

    # Estados permitidos del pedido
    ESTADO_PENDIENTE_PAGO = 'pendiente_pago'
    ESTADO_PENDIENTE_VERIFICACION = 'pendiente_verificacion'
    ESTADO_PAGADO = 'pagado'
    ESTADO_CANCELADO = 'cancelado'

    ESTADOS = [
        ESTADO_PENDIENTE_PAGO,
        ESTADO_PENDIENTE_VERIFICACION,
        ESTADO_PAGADO,
        ESTADO_CANCELADO,
    ]

    ETIQUETAS_ESTADO = {
        ESTADO_PENDIENTE_PAGO: 'Pendiente de Pago',
        ESTADO_PENDIENTE_VERIFICACION: 'Pendiente de Verificación',
        ESTADO_PAGADO: 'Pagado',
        ESTADO_CANCELADO: 'Cancelado',
    }

    CLASES_BOOTSTRAP_ESTADO = {
        ESTADO_PENDIENTE_PAGO: 'warning',
        ESTADO_PENDIENTE_VERIFICACION: 'info',
        ESTADO_PAGADO: 'success',
        ESTADO_CANCELADO: 'danger',
    }

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_pedido = db.Column(db.String(40), nullable=False, unique=True, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    estado = db.Column(db.String(30), nullable=False, default=ESTADO_PENDIENTE_PAGO, index=True)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    direccion_entrega = db.Column(db.String(300), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    detalles = db.relationship('DetallePedido', backref='pedido', lazy='dynamic', cascade='all, delete-orphan')
    comprobantes = db.relationship('ComprobantePago', backref='pedido', lazy='dynamic')

    def __repr__(self):
        return f'<Pedido {self.numero_pedido}>'

    @staticmethod
    def generar_numero_pedido():
        """Genera un número de pedido único."""
        import random
        import string
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        sufijo = ''.join(random.choices(string.digits, k=4))
        return f'PED{timestamp}{sufijo}'

    @property
    def etiqueta_estado(self):
        """Retorna la etiqueta legible del estado."""
        return self.ETIQUETAS_ESTADO.get(self.estado, self.estado)

    @property
    def clase_estado(self):
        """Retorna la clase Bootstrap para el badge de estado."""
        return self.CLASES_BOOTSTRAP_ESTADO.get(self.estado, 'secondary')

    @property
    def puede_pagar(self):
        """Retorna True si el pedido puede recibir un pago."""
        return self.estado == self.ESTADO_PENDIENTE_PAGO

    @property
    def comprobante_activo(self):
        """Retorna el último comprobante subido."""
        from app.modelos.pago import ComprobantePago
        return self.comprobantes.order_by(ComprobantePago.creado_en.desc()).first()

    def to_dict(self):
        """Serializa el pedido a diccionario."""
        return {
            'id': self.id,
            'numero_pedido': self.numero_pedido,
            'usuario_id': self.usuario_id,
            'estado': self.estado,
            'etiqueta_estado': self.etiqueta_estado,
            'total': float(self.total),
            'direccion_entrega': self.direccion_entrega,
            'notas': self.notas,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'detalles': [d.to_dict() for d in self.detalles.all()],
        }


class DetallePedido(db.Model):
    """Modelo que representa un ítem dentro de un pedido."""

    __tablename__ = 'detalle_pedido'

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DetallePedido pedido={self.pedido_id} producto={self.producto_id}>'

    def to_dict(self):
        """Serializa el detalle a diccionario."""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto.nombre if self.producto else None,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': float(self.subtotal),
        }


