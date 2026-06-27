"""
app/utilidades/archivos.py - Utilidades para manejo de archivos subidos
"""

import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def extension_permitida(nombre_archivo):
    """Verifica si la extensión del archivo está permitida."""
    extensiones = current_app.config.get('EXTENSIONES_PERMITIDAS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in nombre_archivo and \
        nombre_archivo.rsplit('.', 1)[1].lower() in extensiones


def guardar_imagen(archivo, carpeta):
    """
    Guarda una imagen subida y retorna el nombre de archivo generado.

    Args:
        archivo: FileStorage de Flask
        carpeta: Ruta absoluta de la carpeta destino

    Returns:
        str: Nombre del archivo guardado, o None si falla.
    """
    if not archivo or not archivo.filename:
        return None

    if not extension_permitida(archivo.filename):
        return None

    # Generar nombre único con UUID
    extension = archivo.filename.rsplit('.', 1)[1].lower()
    nombre_unico = f'{uuid.uuid4().hex}.{extension}'
    nombre_seguro = secure_filename(nombre_unico)

    # Asegurar que la carpeta existe
    os.makedirs(carpeta, exist_ok=True)

    ruta_completa = os.path.join(carpeta, nombre_seguro)
    archivo.save(ruta_completa)

    return nombre_seguro


def guardar_imagen_producto(archivo):
    """Guarda la imagen de un producto."""
    carpeta = current_app.config['UPLOAD_FOLDER_PRODUCTOS']
    return guardar_imagen(archivo, carpeta)


def guardar_comprobante(archivo):
    """Guarda el comprobante de pago (acepta también PDF)."""
    if not archivo or not archivo.filename:
        return None

    extension = archivo.filename.rsplit('.', 1)[1].lower() if '.' in archivo.filename else ''
    extensiones_ok = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

    if extension not in extensiones_ok:
        return None

    nombre_unico = f'{uuid.uuid4().hex}.{extension}'
    nombre_seguro = secure_filename(nombre_unico)
    carpeta = current_app.config['UPLOAD_FOLDER_COMPROBANTES']
    os.makedirs(carpeta, exist_ok=True)

    ruta_completa = os.path.join(carpeta, nombre_seguro)
    archivo.save(ruta_completa)
    return nombre_seguro


def guardar_imagen_qr(archivo):
    """Guarda la imagen QR de un método de pago."""
    carpeta = current_app.config['UPLOAD_FOLDER_QR']
    return guardar_imagen(archivo, carpeta)


def eliminar_archivo(nombre_archivo, carpeta):
    """Elimina un archivo del sistema de archivos."""
    if not nombre_archivo:
        return False
    ruta = os.path.join(carpeta, nombre_archivo)
    if os.path.exists(ruta):
        os.remove(ruta)
        return True
    return False
