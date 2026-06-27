# 🛒 TiendaOnline — Tienda Virtual con Flask y PostgreSQL

Proyecto académico universitario: tienda virtual completa con pagos QR, panel administrativo y API REST, desarrollada con Python Flask, PostgreSQL y Bootstrap 5.

---

## 📋 Descripción

TiendaOnline es una aplicación web monolítica que permite a los usuarios explorar productos, gestionar un carrito de compras, realizar pedidos y pagar mediante códigos QR de distintos bancos bolivianos. Los administradores disponen de un panel completo con estadísticas en tiempo real.

---

## 🏗️ Arquitectura

```
Arquitectura: Monolítica profesional
Patrón:       Application Factory + Blueprints
Entornos:     desarrollo | pruebas | producción
```

```
tienda_online/
├── app/
│   ├── autenticacion/      # Registro, login, perfil
│   ├── administracion/     # CRUD admin completo
│   ├── productos/          # Catálogo y búsqueda
│   ├── carrito/            # Carrito de compras
│   ├── pedidos/            # Gestión de pedidos
│   ├── pagos/              # Pagos QR + comprobantes
│   ├── dashboard/          # Panel + gráficas Chart.js
│   ├── principal/          # Página de inicio
│   ├── modelos/            # SQLAlchemy ORM (10 tablas)
│   ├── formularios/        # WTForms con validaciones
│   ├── servicios/          # API REST + seed
│   ├── utilidades/         # Decoradores, archivos, errores
│   ├── templates/          # Jinja2 + Bootstrap 5
│   └── static/             # CSS, JS, imágenes
├── migrations/             # Flask-Migrate
├── tests/                  # Pytest
├── config.py               # Configuración por entornos
├── run.py                  # Punto de entrada
├── requirements.txt
├── render.yaml             # Despliegue en Render
└── init_db.sql             # Script PostgreSQL inicial
```

---

## 🛠️ Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.13, Flask 3.1 |
| ORM | Flask-SQLAlchemy, Flask-Migrate |
| Auth | Flask-Login, Flask-Bcrypt |
| Forms | Flask-WTF, WTForms |
| Base de Datos | PostgreSQL |
| Frontend | Bootstrap 5.3, Bootstrap Icons, Chart.js |
| Despliegue | Render, Gunicorn |
| Tests | Pytest |

---

## ⚙️ Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/tienda-online.git
cd tienda-online
```

### 2. Crear entorno virtual

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:

```env
FLASK_ENV=desarrollo
SECRET_KEY=genera-una-clave-con-secrets.token_hex(32)
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/tienda_online_dev
```

---

## 🗄️ Configuración de PostgreSQL

### Opción A — Script SQL automático

```bash
psql -U postgres -f init_db.sql
```

### Opción B — Manual

```sql
CREATE DATABASE tienda_online_dev WITH ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE tienda_online_test WITH ENCODING 'UTF8' TEMPLATE template0;
```

---

## 🔄 Migraciones

```bash
# Inicializar migraciones (solo la primera vez)
flask db init

# Generar migración inicial
flask db migrate -m "Creación inicial de tablas"

# Aplicar migraciones
flask db upgrade
```

---

## 🚀 Ejecución local

```bash
# Crear usuario administrador
flask crear-admin

# (Opcional) Poblar con datos de ejemplo
flask poblar-db

# Iniciar servidor
python run.py
```

Acceder a: **http://localhost:5000**

### Credenciales del administrador inicial

| Campo | Valor |
|-------|-------|
| Email | `admin@tienda.com` |
| Contraseña | `Admin123!` |

### Credenciales del cliente de ejemplo (si se ejecuta poblar-db)

| Campo | Valor |
|-------|-------|
| Email | `cliente@tienda.com` |
| Contraseña | `Cliente123!` |

---

## 🌐 Despliegue en Render

### 1. Subir a GitHub

```bash
git init
git add .
git commit -m "feat: proyecto tienda online completo"
git branch -M main
git remote add origin https://github.com/tu-usuario/tienda-online.git
git push -u origin main
```

### 2. Conectar en Render

1. Ir a [render.com](https://render.com) → **New Web Service**
2. Conectar el repositorio de GitHub
3. Render detectará automáticamente el archivo `render.yaml`
4. Las variables de entorno se configuran automáticamente
5. El despliegue ejecutará: `pip install → flask db upgrade → flask crear-admin → flask poblar-db`

### Variables de entorno en Render

| Variable | Valor |
|----------|-------|
| `FLASK_ENV` | `produccion` |
| `SECRET_KEY` | *(generada automáticamente)* |
| `DATABASE_URL` | *(proporcionada por Render PostgreSQL)* |

---

## 📡 API REST

Base URL: `/api/v1`

### Productos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/productos` | Listar productos | No |
| `GET` | `/api/v1/productos/<id>` | Detalle de producto | No |
| `POST` | `/api/v1/productos` | Crear producto | Admin |
| `PUT` | `/api/v1/productos/<id>` | Actualizar producto | Admin |
| `DELETE` | `/api/v1/productos/<id>` | Eliminar producto | Admin |

**Parámetros de búsqueda (GET /productos):**
- `q` — Término de búsqueda
- `categoria_id` — Filtrar por categoría
- `pagina` — Número de página (default: 1)
- `por_pagina` — Ítems por página (default: 12, max: 50)

**Ejemplo de respuesta:**
```json
{
  "ok": true,
  "datos": {
    "productos": [
      {
        "id": 1,
        "nombre": "Smartphone Samsung",
        "precio": 1899.00,
        "stock": 15,
        "categoria": "Electrónica",
        "en_stock": true
      }
    ],
    "total": 12,
    "paginas": 1,
    "pagina_actual": 1
  }
}
```

### Pedidos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/pedidos` | Listar pedidos del usuario | Sí |
| `GET` | `/api/v1/pedidos/<id>` | Detalle de pedido | Sí |
| `POST` | `/api/v1/pedidos` | Crear pedido desde carrito | Sí |

---

## 🗃️ Modelos de Base de Datos

| Tabla | Descripción |
|-------|-------------|
| `roles` | Roles del sistema (administrador, cliente) |
| `usuarios` | Usuarios con hash bcrypt |
| `categorias` | Categorías de productos |
| `productos` | Catálogo con imagen y stock |
| `carritos` | Carrito activo por usuario |
| `detalle_carrito` | Ítems del carrito |
| `pedidos` | Pedidos con estados |
| `detalle_pedido` | Ítems del pedido (snapshot de precios) |
| `metodos_pago` | QRs configurados por el admin |
| `comprobantes_pago` | Comprobantes subidos por clientes |

---

## 🧪 Ejecutar Tests

```bash
# Crear base de datos de pruebas primero
psql -U postgres -c "CREATE DATABASE tienda_online_test WITH ENCODING 'UTF8' TEMPLATE template0;"

# Ejecutar todos los tests
pytest

# Con reporte de cobertura
pytest --cov=app tests/
```

---

## 🔒 Seguridad implementada

- ✅ Hash de contraseñas con Bcrypt
- ✅ Protección CSRF en todos los formularios (Flask-WTF)
- ✅ Protección contra SQL Injection (SQLAlchemy ORM)
- ✅ Control de acceso basado en roles (decoradores)
- ✅ Validaciones de formularios en frontend y backend
- ✅ Escape automático de HTML en Jinja2 (anti-XSS)
- ✅ Rutas protegidas con `@login_required`
- ✅ Sesiones seguras con cookie HTTPONLY

---

## 👨‍💻 Comandos útiles de Flask CLI

```bash
flask crear-admin       # Crea el usuario administrador
flask poblar-db         # Inserta datos de ejemplo
flask db migrate -m ""  # Genera migración
flask db upgrade        # Aplica migraciones
flask shell             # Shell interactivo con modelos cargados
```

---

## 📄 Licencia

Proyecto académico universitario. Libre para uso educativo.
