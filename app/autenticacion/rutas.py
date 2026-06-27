"""
app/autenticacion/rutas.py - Rutas del módulo de autenticación
"""

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.autenticacion import bp
from app.formularios import FormularioLogin, FormularioRegistro, FormularioPerfil, FormularioCambiarContrasena
from app.modelos.usuario import Usuario
from app.modelos.rol import Rol
from app.utilidades.archivos import guardar_imagen, eliminar_archivo


@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Vista de registro de nuevo usuario."""
    if current_user.is_authenticated:
        return redirect(url_for('principal.index'))

    form = FormularioRegistro()
    if form.validate_on_submit():
        # Obtener rol de cliente
        rol_cliente = Rol.query.filter_by(nombre='cliente').first()
        if not rol_cliente:
            flash('Error de configuración del sistema. Contacta al administrador.', 'danger')
            return redirect(url_for('autenticacion.registro'))

        usuario = Usuario(
            nombre=form.nombre.data.strip(),
            apellido=form.apellido.data.strip(),
            email=form.email.data.lower().strip(),
            telefono=form.telefono.data.strip() if form.telefono.data else None,
            rol_id=rol_cliente.id,
            activo=True
        )
        usuario.establecer_contrasena(form.contrasena.data)

        db.session.add(usuario)
        db.session.commit()

        flash('¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('autenticacion.login'))

    return render_template('autenticacion/registro.html', form=form, titulo='Registro')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Vista de inicio de sesión."""
    if current_user.is_authenticated:
        return redirect(url_for('principal.index'))

    form = FormularioLogin()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data.lower().strip()).first()

        if usuario and usuario.verificar_contrasena(form.contrasena.data):
            if not usuario.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                return render_template('autenticacion/login.html', form=form, titulo='Iniciar Sesión')

            login_user(usuario, remember=form.recordarme.data)

            # Actualizar último login
            usuario.ultimo_login = datetime.utcnow()
            db.session.commit()

            flash(f'¡Bienvenido, {usuario.nombre}!', 'success')

            # Redirigir a la página solicitada originalmente
            siguiente = request.args.get('next')
            if siguiente and siguiente.startswith('/'):
                return redirect(siguiente)

            if usuario.es_administrador:
                return redirect(url_for('dashboard.index'))
            return redirect(url_for('principal.index'))
        else:
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('autenticacion/login.html', form=form, titulo='Iniciar Sesión')


@bp.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario."""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('autenticacion.login'))


@bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Vista para editar el perfil del usuario."""
    form = FormularioPerfil(obj=current_user)

    if form.validate_on_submit():
        current_user.nombre = form.nombre.data.strip()
        current_user.apellido = form.apellido.data.strip()
        current_user.telefono = form.telefono.data.strip() if form.telefono.data else None
        current_user.direccion = form.direccion.data.strip() if form.direccion.data else None
        current_user.ciudad = form.ciudad.data.strip() if form.ciudad.data else None

        # Procesar foto de perfil
        if form.foto_perfil.data and form.foto_perfil.data.filename:
            # Eliminar foto anterior
            if current_user.foto_perfil:
                carpeta = current_app.config['UPLOAD_FOLDER_PRODUCTOS']
                eliminar_archivo(current_user.foto_perfil, carpeta)

            from app.utilidades.archivos import guardar_imagen
            carpeta = current_app.config['UPLOAD_FOLDER_PRODUCTOS']
            nombre_foto = guardar_imagen(form.foto_perfil.data, carpeta)
            if nombre_foto:
                current_user.foto_perfil = nombre_foto

        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('autenticacion.perfil'))

    return render_template('autenticacion/perfil.html', form=form, titulo='Mi Perfil')


@bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_contrasena():
    """Vista para cambiar la contraseña."""
    form = FormularioCambiarContrasena()

    if form.validate_on_submit():
        if not current_user.verificar_contrasena(form.contrasena_actual.data):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('autenticacion/cambiar_contrasena.html', form=form)

        current_user.establecer_contrasena(form.nueva_contrasena.data)
        db.session.commit()
        flash('Contraseña cambiada exitosamente.', 'success')
        return redirect(url_for('autenticacion.perfil'))

    return render_template('autenticacion/cambiar_contrasena.html',
                           form=form, titulo='Cambiar Contraseña')
