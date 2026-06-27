"""
app/modelos/usuario.py - Modelo de Usuario con Flask-Login
"""

from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt, login_manager


class Usuario(UserMixin, db.Model):
    """Modelo que representa los usuarios del sistema."""

    __tablename__ = 'usuarios'

    # Columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(300), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    foto_perfil = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)

    # Relaciones
    carritos = db.relationship('Carrito', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    pedidos = db.relationship('Pedido', backref='usuario', lazy='dynamic')

    def __repr__(self):
        return f'<Usuario {self.email}>'

    # ── Métodos de contraseña ──────────────────────────────────────────────
    def establecer_contrasena(self, contrasena):
        """Genera y almacena el hash de la contraseña."""
        self.contrasena_hash = bcrypt.generate_password_hash(contrasena).decode('utf-8')

    def verificar_contrasena(self, contrasena):
        """Verifica si la contraseña coincide con el hash almacenado."""
        return bcrypt.check_password_hash(self.contrasena_hash, contrasena)

    # ── Propiedades de Flask-Login ─────────────────────────────────────────
    @property
    def is_active(self):
        return self.activo

    # ── Propiedades de rol ─────────────────────────────────────────────────
    @property
    def es_administrador(self):
        """Retorna True si el usuario tiene rol de administrador."""
        return self.rol and self.rol.nombre == 'administrador'

    @property
    def es_cliente(self):
        """Retorna True si el usuario tiene rol de cliente."""
        return self.rol and self.rol.nombre == 'cliente'

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario."""
        return f'{self.nombre} {self.apellido}'

    # ── Carrito activo ─────────────────────────────────────────────────────
    def obtener_carrito_activo(self):
        """Retorna el carrito activo del usuario o None."""
        from app.modelos.carrito import Carrito
        return Carrito.query.filter_by(usuario_id=self.id, activo=True).first()

    def to_dict(self):
        """Serializa el usuario a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'activo': self.activo,
            'rol': self.rol.nombre if self.rol else None,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
        }


@login_manager.user_loader
def cargar_usuario(user_id):
    """Callback de Flask-Login para cargar usuario por ID."""
    return Usuario.query.get(int(user_id))
