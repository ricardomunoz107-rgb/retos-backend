-- Ejecutar con un usuario administrador de PostgreSQL.
-- Ejecutar este archivo con psql, que solicita la contraseña de forma segura.
CREATE USER admin_retos WITH LOGIN;
\password admin_retos
CREATE DATABASE retos_db OWNER admin_retos;
GRANT ALL PRIVILEGES ON DATABASE retos_db TO admin_retos;
\connect retos_db
GRANT USAGE, CREATE ON SCHEMA public TO admin_retos;
