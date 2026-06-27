-- =============================================================================
-- init_db.sql - Script de inicialización de la base de datos TiendaOnline
-- Ejecutar ANTES de las migraciones Flask-Migrate
-- Uso: psql -U postgres -f init_db.sql
-- =============================================================================

-- Crear base de datos (ejecutar como superusuario)
CREATE DATABASE tienda_online_dev
    WITH ENCODING 'UTF8'
    LC_COLLATE 'es_BO.UTF-8'
    LC_CTYPE 'es_BO.UTF-8'
    TEMPLATE template0;

-- Si el locale no está disponible, usar:
-- CREATE DATABASE tienda_online_dev WITH ENCODING 'UTF8' TEMPLATE template0;

-- Crear usuario de la aplicación
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'tienda_user') THEN
        CREATE ROLE tienda_user WITH LOGIN PASSWORD 'tienda_password_segura';
    END IF;
END
$$;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE tienda_online_dev TO tienda_user;

-- Conectar a la base de datos
\c tienda_online_dev;

GRANT ALL ON SCHEMA public TO tienda_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tienda_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tienda_user;

-- =============================================================================
-- Las tablas se crean automáticamente con Flask-Migrate.
-- Ejecutar después:
--   flask db init
--   flask db migrate -m "Creación inicial"
--   flask db upgrade
--   flask crear-admin
--   flask poblar-db
-- =============================================================================

-- Base de datos de pruebas
CREATE DATABASE tienda_online_test
    WITH ENCODING 'UTF8'
    TEMPLATE template0;

GRANT ALL PRIVILEGES ON DATABASE tienda_online_test TO tienda_user;

\echo '==================================================='
\echo 'Base de datos creada exitosamente.'
\echo 'Continúa con: flask db upgrade && flask crear-admin'
\echo '==================================================='
