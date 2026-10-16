-- Ejecutar con un usuario administrador de PostgreSQL.
-- Cambia la contraseña de ejemplo antes de ejecutar este script.
CREATE USER admin_retos WITH PASSWORD 'CAMBIAR_ESTA_PASSWORD';
CREATE DATABASE retos_db OWNER admin_retos;
GRANT ALL PRIVILEGES ON DATABASE retos_db TO admin_retos;
