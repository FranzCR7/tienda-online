"""
app/modelos/pago.py - Modelos de Método de Pago y Comprobante de Pago
"""

from datetime import datetime
from app import db


class MetodoPago(db.Model):
    """Modelo que representa los métodos de pago QR disponibles."""

    __tablename__ = 'metodos_pago'

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_qr = db.Column(db.String(255), nullable=True)
    titular = db.Column(db.String(150), nullable=True)
    numero_cuenta = db.Column(db.String(50), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    comprobantes = db.relationship('ComprobantePago', backref='metodo_pago', lazy='dynamic')

    def __repr__(self):
        return f'<MetodoPago {self.nombre}>'

    @property
    def qr_url(self):
        """Retorna la URL del QR del método de pago."""
        if self.imagen_qr:
            return f'/static/uploads/qr/{self.imagen_qr}'
        return '/static/img/qr-default.png'

    def to_dict(self):
        """Serializa el método de pago a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'qr_url': self.qr_url,
            'titular': self.titular,
            'numero_cuenta': self.numero_cuenta,
            'activo': self.activo,
        }


class ComprobantePago(db.Model):
    """Modelo que representa los comprobantes de pago subidos por los clientes."""

    __tablename__ = 'comprobantes_pago'

    # Estados del comprobante
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADO = 'aprobado'
    ESTADO_RECHAZADO = 'rechazado'

    ESTADOS = [ESTADO_PENDIENTE, ESTADO_APROBADO, ESTADO_RECHAZADO]

    ETIQUETAS_ESTADO = {
        ESTADO_PENDIENTE: 'Pendiente de Revisión',
        ESTADO_APROBADO: 'Aprobado',
        ESTADO_RECHAZADO: 'Rechazado',
    }

    CLASES_BOOTSTRAP_ESTADO = {
        ESTADO_PENDIENTE: 'warning',
        ESTADO_APROBADO: 'success',
        ESTADO_RECHAZADO: 'danger',
    }

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False, index=True)
    metodo_pago_id = db.Column(db.Integer, db.ForeignKey('metodos_pago.id'), nullable=False)
    imagen_comprobante = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default=ESTADO_PENDIENTE)
    observaciones = db.Column(db.Text, nullable=True)
    revisado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    revisado_en = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con el revisor
    revisor = db.relationship('Usuario', foreign_keys=[revisado_por])

    def __repr__(self):
        return f'<ComprobantePago pedido={self.pedido_id} estado={self.estado}>'

    @property
    def imagen_url(self):
        """Retorna la URL del comprobante."""
        if self.imagen_comprobante:
            return f'/static/uploads/comprobantes/{self.imagen_comprobante}'
        return '/static/img/comprobante-default.png'

    @property
    def etiqueta_estado(self):
        """Retorna la etiqueta legible del estado."""
        return self.ETIQUETAS_ESTADO.get(self.estado, self.estado)

    @property
    def clase_estado(self):
        """Retorna la clase Bootstrap del estado."""
        return self.CLASES_BOOTSTRAP_ESTADO.get(self.estado, 'secondary')

    def to_dict(self):
        """Serializa el comprobante a diccionario."""
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'metodo_pago': self.metodo_pago.nombre if self.metodo_pago else None,
            'imagen_url': self.imagen_url,
            'monto': float(self.monto),
            'estado': self.estado,
            'etiqueta_estado': self.etiqueta_estado,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
        }
