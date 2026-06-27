"""
app/modelos/categoria.py - Modelo de Categoría de productos
"""

from datetime import datetime
from app import db


class Categoria(db.Model):
    """Modelo que representa las categorías de productos."""

    __tablename__ = 'categorias'

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    activa = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    productos = db.relationship('Producto', backref='categoria', lazy='dynamic')

    def __repr__(self):
        return f'<Categoria {self.nombre}>'

    def generar_slug(self):
        """Genera slug a partir del nombre."""
        import re
        slug = self.nombre.lower()
        slug = re.sub(r'[áàäâ]', 'a', slug)
        slug = re.sub(r'[éèëê]', 'e', slug)
        slug = re.sub(r'[íìïî]', 'i', slug)
        slug = re.sub(r'[óòöô]', 'o', slug)
        slug = re.sub(r'[úùüû]', 'u', slug)
        slug = re.sub(r'ñ', 'n', slug)
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug.strip())
        return slug

    @property
    def total_productos(self):
        """Retorna el total de productos activos en la categoría."""
        return self.productos.filter_by(activo=True).count()

    def to_dict(self):
        """Serializa la categoría a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'slug': self.slug,
            'activa': self.activa,
            'total_productos': self.total_productos,
        }
