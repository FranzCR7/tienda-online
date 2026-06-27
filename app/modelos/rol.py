"""
app/modelos/rol.py - Modelo de Rol de usuario
"""

from app import db
from datetime import datetime


class Rol(db.Model):
    """Modelo que representa los roles del sistema."""

    __tablename__ = 'roles'

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.String(200), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuarios = db.relationship('Usuario', backref='rol', lazy='dynamic')

    def __repr__(self):
        return f'<Rol {self.nombre}>'

    def to_dict(self):
        """Serializa el rol a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
        }
