-- fix_numero_pedido.sql
-- Ejecutar este script si ya tienes la base de datos creada
-- y el sistema arroja error de campo demasiado largo en numero_pedido

ALTER TABLE pedidos ALTER COLUMN numero_pedido TYPE VARCHAR(40);

SELECT 'Columna numero_pedido actualizada correctamente.' as resultado;
