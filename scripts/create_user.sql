-- Ejecutar con psql como administrador despues de create_database.sql.
-- psql solicita la contraseña de forma segura y no la guarda en este archivo.
CREATE USER admin_retos WITH LOGIN;
\password admin_retos
GRANT ALL PRIVILEGES ON DATABASE retos_db TO admin_retos;
\connect retos_db
GRANT USAGE, CREATE ON SCHEMA public TO admin_retos;
