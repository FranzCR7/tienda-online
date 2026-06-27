"""
app/formularios/__init__.py - Formularios WTForms de la aplicación
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, PasswordField, BooleanField, TextAreaField,
    SelectField, IntegerField, DecimalField, HiddenField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, NumberRange,
    Optional, ValidationError, Regexp
)


# ─── Formularios de Autenticación ─────────────────────────────────────────────

class FormularioRegistro(FlaskForm):
    """Formulario de registro de nuevo usuario."""
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio.'),
        Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres.')
    ])
    apellido = StringField('Apellido', validators=[
        DataRequired(message='El apellido es obligatorio.'),
        Length(min=2, max=100, message='El apellido debe tener entre 2 y 100 caracteres.')
    ])
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message='El correo es obligatorio.'),
        Email(message='Ingresa un correo electrónico válido.'),
        Length(max=150)
    ])
    telefono = StringField('Teléfono', validators=[
        Optional(),
        Length(max=20),
        Regexp(r'^\d{7,15}$', message='El teléfono debe contener solo números (7-15 dígitos).')
    ])
    contrasena = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria.'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres.')
    ])
    confirmar_contrasena = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Por favor confirma tu contraseña.'),
        EqualTo('contrasena', message='Las contraseñas no coinciden.')
    ])
    enviar = SubmitField('Registrarse')

    def validate_email(self, email):
        from app.modelos.usuario import Usuario
        usuario = Usuario.query.filter_by(email=email.data.lower()).first()
        if usuario:
            raise ValidationError('Este correo ya está registrado.')


class FormularioLogin(FlaskForm):
    """Formulario de inicio de sesión."""
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message='El correo es obligatorio.'),
        Email(message='Ingresa un correo electrónico válido.')
    ])
    contrasena = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria.')
    ])
    recordarme = BooleanField('Recordarme')
    enviar = SubmitField('Iniciar Sesión')


class FormularioPerfil(FlaskForm):
    """Formulario de edición de perfil de usuario."""
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio.'),
        Length(min=2, max=100)
    ])
    apellido = StringField('Apellido', validators=[
        DataRequired(message='El apellido es obligatorio.'),
        Length(min=2, max=100)
    ])
    telefono = StringField('Teléfono', validators=[
        Optional(),
        Length(max=20),
        Regexp(r'^\d{7,15}$', message='Solo números, 7-15 dígitos.')
    ])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=300)])
    ciudad = StringField('Ciudad', validators=[Optional(), Length(max=100)])
    foto_perfil = FileField('Foto de Perfil', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo imágenes.')
    ])
    enviar = SubmitField('Actualizar Perfil')


class FormularioCambiarContrasena(FlaskForm):
    """Formulario para cambiar la contraseña."""
    contrasena_actual = PasswordField('Contraseña Actual', validators=[
        DataRequired(message='Ingresa tu contraseña actual.')
    ])
    nueva_contrasena = PasswordField('Nueva Contraseña', validators=[
        DataRequired(message='Ingresa la nueva contraseña.'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres.')
    ])
    confirmar_contrasena = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(message='Confirma la nueva contraseña.'),
        EqualTo('nueva_contrasena', message='Las contraseñas no coinciden.')
    ])
    enviar = SubmitField('Cambiar Contraseña')


# ─── Formularios de Categorías ─────────────────────────────────────────────────

class FormularioCategoria(FlaskForm):
    """Formulario de creación y edición de categorías."""
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio.'),
        Length(min=2, max=100)
    ])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    activa = BooleanField('Activa', default=True)
    enviar = SubmitField('Guardar Categoría')

    def validate_nombre(self, nombre):
        from app.modelos.categoria import Categoria
        from flask import request
        try:
            categoria_id = request.view_args.get('categoria_id')
        except Exception:
            categoria_id = None
        categoria = Categoria.query.filter_by(nombre=nombre.data).first()
        if categoria and (not categoria_id or str(categoria.id) != str(categoria_id)):
            raise ValidationError('Ya existe una categoría con ese nombre.')


# ─── Formularios de Productos ──────────────────────────────────────────────────

class FormularioProducto(FlaskForm):
    """Formulario de creación y edición de productos."""
    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(message='El nombre es obligatorio.'),
        Length(min=2, max=200)
    ])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    precio = DecimalField('Precio (Bs.)', validators=[
        DataRequired(message='El precio es obligatorio.'),
        NumberRange(min=0.01, message='El precio debe ser mayor a 0.')
    ], places=2)
    stock = IntegerField('Stock disponible', validators=[
        DataRequired(message='El stock es obligatorio.'),
        NumberRange(min=0, message='El stock no puede ser negativo.')
    ])
    categoria_id = SelectField('Categoría', coerce=int, validators=[
        DataRequired(message='Selecciona una categoría.')
    ])
    activo = BooleanField('Producto Activo', default=True)
    destacado = BooleanField('Producto Destacado', default=False)
    imagen = FileField('Imagen del Producto', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo imágenes.')
    ])
    enviar = SubmitField('Guardar Producto')


class FormularioBuscarProducto(FlaskForm):
    """Formulario de búsqueda de productos."""
    q = StringField('Buscar', validators=[Optional()])
    categoria = SelectField('Categoría', coerce=int, validators=[Optional()])
    precio_min = DecimalField('Precio mínimo', validators=[Optional(), NumberRange(min=0)], places=2)
    precio_max = DecimalField('Precio máximo', validators=[Optional(), NumberRange(min=0)], places=2)
    enviar = SubmitField('Buscar')

    class Meta:
        csrf = False  # Formulario GET no necesita CSRF


# ─── Formularios de Carrito ────────────────────────────────────────────────────

class FormularioAgregarCarrito(FlaskForm):
    """Formulario para agregar un producto al carrito."""
    producto_id = HiddenField('Producto ID', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(message='La cantidad es obligatoria.'),
        NumberRange(min=1, max=99, message='La cantidad debe ser entre 1 y 99.')
    ], default=1)
    enviar = SubmitField('Agregar al Carrito')


class FormularioActualizarCarrito(FlaskForm):
    """Formulario para actualizar la cantidad de un ítem del carrito."""
    detalle_id = HiddenField('Detalle ID', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(),
        NumberRange(min=1, max=99)
    ])
    enviar = SubmitField('Actualizar')


# ─── Formularios de Pedidos ────────────────────────────────────────────────────

class FormularioPedido(FlaskForm):
    """Formulario para confirmar y crear un pedido."""
    direccion_entrega = StringField('Dirección de Entrega', validators=[
        Optional(),
        Length(max=300)
    ])
    notas = TextAreaField('Notas adicionales', validators=[Optional(), Length(max=500)])
    enviar = SubmitField('Confirmar Pedido')


# ─── Formularios de Pagos ──────────────────────────────────────────────────────

class FormularioSubirComprobante(FlaskForm):
    """Formulario para subir el comprobante de pago."""
    metodo_pago_id = SelectField('Método de Pago', coerce=int, validators=[
        DataRequired(message='Selecciona un método de pago.')
    ])
    comprobante = FileField('Comprobante de Pago', validators=[
        FileRequired(message='Debes subir el comprobante de pago.'),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'gif', 'webp'], 'Solo imágenes o PDF.')
    ])
    enviar = SubmitField('Subir Comprobante')


class FormularioMetodoPago(FlaskForm):
    """Formulario de creación y edición de métodos de pago."""
    nombre = StringField('Nombre del Método de Pago', validators=[
        DataRequired(message='El nombre es obligatorio.'),
        Length(min=2, max=100)
    ])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    titular = StringField('Titular de la cuenta', validators=[Optional(), Length(max=150)])
    numero_cuenta = StringField('Número de cuenta / Teléfono', validators=[Optional(), Length(max=50)])
    imagen_qr = FileField('Imagen QR', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo imágenes.')
    ])
    activo = BooleanField('Activo', default=True)
    enviar = SubmitField('Guardar Método de Pago')


class FormularioRevisarComprobante(FlaskForm):
    """Formulario para que el admin revise y apruebe/rechace un comprobante."""
    accion = SelectField('Acción', choices=[
        ('aprobado', 'Aprobar pago'),
        ('rechazado', 'Rechazar pago')
    ], validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones', validators=[Optional(), Length(max=500)])
    enviar = SubmitField('Guardar Revisión')


# ─── Formularios de Administración de Usuarios ────────────────────────────────

class FormularioUsuarioAdmin(FlaskForm):
    """Formulario para gestionar usuarios desde el panel admin."""
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=150)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    rol_id = SelectField('Rol', coerce=int, validators=[DataRequired()])
    activo = BooleanField('Activo', default=True)
    contrasena = PasswordField('Contraseña (dejar vacío para no cambiar)', validators=[
        Optional(),
        Length(min=8, message='Mínimo 8 caracteres.')
    ])
    enviar = SubmitField('Guardar Usuario')
