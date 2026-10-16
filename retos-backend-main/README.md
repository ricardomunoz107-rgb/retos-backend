# Plataforma de Retos de Programación - API REST

Backend desarrollado con Django y Django REST Framework. Incluye una portada web,
una API CRUD para categorías, retos y envíos, y soporte para SQLite o PostgreSQL.

## Requisitos

- Python 3.13 o compatible con la versión de Django indicada en `requirements.txt`.
- SQLite (incluido con Python) o PostgreSQL.

## Instalación local

Desde la raíz del repositorio:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

En Linux o macOS, activa el entorno con `source .venv/bin/activate`. El archivo
`.env` es local y está excluido de Git. La plantilla usa SQLite para que el
proyecto arranque sin configurar un servidor de base de datos.

Para PostgreSQL, configura `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
`DB_HOST` y `DB_PORT` en `.env`. El script [scripts/init_db.sql](scripts/init_db.sql)
prepara la base y el usuario; cambia primero la contraseña de ejemplo.

`SECRET_KEY` de la plantilla es solo un marcador de posición. Define una clave
propia antes de usar el proyecto fuera de desarrollo. `DEBUG` y `ALLOWED_HOSTS`
también se configuran desde `.env`.

## Migraciones y administración

Cuando agregues o cambies modelos:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

El panel administrativo está en `/admin/`.

## API

El enrutador REST expone operaciones `GET`, `POST`, `PUT`, `PATCH` y `DELETE`:

- `/api/categorias/`
- `/api/retos/`
- `/api/envios/`

La interfaz HTML de inicio está en `/`. Los desafíos de la portada enlazan
directamente a su página de solución. `/jugar/` permite elegir un reto y cada
reto se resuelve en su propia página. El editor valida un subconjunto restringido
de Python (variables, operaciones, `if`, `for` con `range()` acotado y funciones
básicas); no ejecuta código Python arbitrario. Guarda los intentos en `Envio` y
el puntaje en `RetoResuelto`, con una recompensa por reto y nombre de jugador.
Doce retos de práctica (cuatro por nivel de dificultad) se cargan automáticamente
con las migraciones. El nombre es
un identificador para la tabla de posiciones, no una cuenta autenticada.

La API requiere un usuario administrador para las operaciones de escritura; los
endpoints de lectura siguen disponibles públicamente. Inicia sesión en `/admin/`
para administrar categorías, retos, respuestas correctas y envíos.

## Pruebas

```powershell
python manage.py test
```
