# Plataforma de Retos de Programación - API REST

Backend desarrollado con Django y Django REST Framework. Incluye una portada web,
una API CRUD para las entidades del proyecto, páginas de práctica y soporte para
SQLite o PostgreSQL.

## Requisitos

- Python 3.13 o compatible con la versión de Django indicada en `requirements.txt`.
- SQLite (incluido con Python) o PostgreSQL.

## Instalación local

Desde la raíz del repositorio:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Configura PostgreSQL, después aplica las migraciones y crea el administrador:

```powershell
psql -U postgres -d postgres -f scripts\create_database.sql
psql -U postgres -d postgres -f scripts\create_user.sql
# Edita .env con la contraseña que psql te pidió.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En Linux o macOS, activa el entorno con `source .venv/bin/activate`. El archivo
`.env` es local y está excluido de Git. La plantilla `.env.example` configura
PostgreSQL; usa el mismo usuario, base, host y puerto creados por los scripts.
Si `psql` no se reconoce en PowerShell, agrega al `PATH` la carpeta `bin` de tu
instalación PostgreSQL, por ejemplo `C:\Program Files\PostgreSQL\18\bin`.
Puedes hacerlo solo en la terminal actual con:

```powershell
$env:Path += ';C:\Program Files\PostgreSQL\18\bin'
```

También se puede usar SQLite en `.env` con
`DB_ENGINE=django.db.backends.sqlite3` y `DB_NAME=db.sqlite3`.

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
- `/api/retos-resueltos/`
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
Las migraciones `0006_seed_demo_records` y
`0007_seed_extended_demo_activity` agregan categorías, retos resueltos y envíos
de ejemplo para que los listados de gestión y el registro público de participantes
tengan datos visibles; las acciones CRUD modifican los registros guardados en la
base activa.

Las lecturas de categorías, retos y retos resueltos son públicas. Las operaciones
de escritura requieren permisos de administrador; el endpoint de envíos requiere
administrador para todas sus operaciones. Inicia sesión en `/admin/` para
administrar los registros.

## Evaluación 3: CRUD web con CBV

El proyecto conserva la API REST acumulativa y agrega operaciones web con vistas
basadas en clases nativas de Django para las cuatro entidades: `Categoria`,
`Reto`, `RetoResuelto` y `Envio`. Cada entidad tiene vistas ListView, DetailView,
CreateView, UpdateView y DeleteView, con confirmación antes de eliminar.

Los formularios ModelForm están centralizados en `retos/forms.py`; especifican
los campos editables y widgets HTML con clases, placeholders y áreas de texto.
Las vistas de gestión requieren una cuenta de personal (`is_staff`); crea una
con `python manage.py createsuperuser` e inicia sesión en `/admin/`. Este equipo
usa una cuenta local de demostración configurada mediante variables
`DJANGO_SUPERUSER_*` en `.env`; para crearla en una base nueva ejecuta
`python manage.py createsuperuser --noinput`. El `.env` no se publica; en una
instalación real, crea una contraseña propia y segura.

| Entidad | Listado | Detalle | Crear | API |
| --- | --- | --- | --- | --- |
| Categorías | `/gestion/categorias/` | `/gestion/categorias/<id>/` | `/gestion/categorias/nueva/` | `/api/categorias/` |
| Retos | `/gestion/retos/` | `/gestion/retos/<id>/` | `/gestion/retos/nuevo/` | `/api/retos/` |
| Retos resueltos | `/gestion/retos-resueltos/` | `/gestion/retos-resueltos/<id>/` | `/gestion/retos-resueltos/nuevo/` | `/api/retos-resueltos/` |
| Envíos | `/gestion/envios/` | `/gestion/envios/<id>/` | `/gestion/envios/nuevo/` | `/api/envios/` |

Desde cada listado se puede abrir el detalle, editar o eliminar; los enlaces de
crear y navegación entre entidades están disponibles en las pantallas de gestión.
La portada pública `/` enlaza a la gestión, que solicita autenticación.

## Consultar los datos desde PHP

`php/index.php` es un panel PHP de solo lectura que muestra categorías, retos,
retos resueltos y envíos consultando la API REST. No conecta PHP al archivo
SQLite directamente, por lo que Django y su base de datos actual no se modifican.
Se necesita PHP CLI y la extensión PHP cURL habilitada.

1. En una terminal, inicia Django desde la carpeta del proyecto:
   `python manage.py runserver`.
2. En una segunda terminal, desde la misma carpeta, configura las credenciales
   de un usuario creado con `python manage.py createsuperuser` y arranca el
   servidor de desarrollo de PHP:

   ```powershell
   $env:EVA3_ADMIN_USER = "tu_usuario"
   $securePassword = Read-Host "Contraseña del administrador Django" -AsSecureString
   $env:EVA3_ADMIN_PASSWORD = [System.Net.NetworkCredential]::new("", $securePassword).Password
   php -S 127.0.0.1:8080 -t php
   ```

3. Abre `http://127.0.0.1:8080/` en el navegador. Si solo quieres ver las tablas
   públicas, puedes iniciar PHP sin configurar las credenciales: los envíos
   requieren acceso de administrador.

Para usar XAMPP/Apache en vez del servidor de desarrollo PHP, copia `php/index.php`
a una carpeta bajo `C:\xampp\htdocs\` y configura allí las mismas variables de
entorno en el proceso Apache. Nunca pongas la contraseña directamente en un
archivo PHP dentro de `htdocs` ni publiques las credenciales.

Si prefieres no configurar credenciales de administrador, el panel sigue
mostrando las categorías, los retos y los retos resueltos; los envíos requieren
autenticación de administrador. Ambos servidores deben funcionar en el mismo
equipo para usar la conexión local recomendada.

## Base de datos y configuración

PostgreSQL es el motor recomendado y el predeterminado de `.env.example`. El
archivo `.env` local está excluido de Git. En otra instalación, créalo desde
`.env.example` si todavía no existe. No publiques claves ni contraseñas reales
en un repositorio público.
Si ya existía un `.env` con SQLite, el instalador no lo sobrescribe: cambia sus
variables `DB_*` explícitamente cuando quieras pasar a PostgreSQL y conserva tu
archivo `db.sqlite3` como respaldo.

Para PostgreSQL, ejecuta los scripts con `psql` en este orden, como administrador:

```powershell
psql -U postgres -d postgres -f scripts\create_database.sql
psql -U postgres -d postgres -f scripts\create_user.sql
```

`create_user.sql` crea el usuario y concede permisos sobre la base de datos y el
esquema `public`; `psql` solicitará dos veces una contraseña. Colócala en
`DB_PASSWORD` en `.env` y ejecuta las migraciones. `scripts\init_db.sql` combina
ambos pasos cuando prefieras ejecutarlos en un solo archivo con `psql`.
El documento [Base de datos migracion.txt](<./Base de datos migracion.txt>)
resume las tablas, relaciones y comandos de migración.

El proyecto del profesor incluido como referencia configura MySQL
(`django.db.backends.mysql` y `mysqlclient`); no es PostgreSQL. Para este
proyecto mantenemos PostgreSQL, que ya es compatible con Django mediante
`psycopg2-binary`, sin copiar el tema ni el modelo bibliotecario del profesor.

## Evidencias de evaluación

Entrega `evidencias_eva3.pdf` junto al README en el repositorio. Incluye
capturas de ListView, DetailView, CreateView, UpdateView, DeleteView con
confirmación, navegación y portada pública. En cada evidencia deja visible la
URL del navegador y el terminal donde Django registra la solicitud, la ruta y
el código HTTP. No uses capturas simuladas: genera las evidencias al ejecutar
el proyecto.

## Repositorio GitHub

El archivo `.gitignore` excluye `.env`, bases de datos locales, archivos
estáticos generados y carpetas del entorno virtual. Conserva `.env.example` y
los scripts SQL en el repositorio. Revisa que no se hayan añadido contraseñas
ni archivos de base de datos antes de publicar.

## Publicar en Render

El proyecto incluye `render.yaml` para desplegar Django junto con una instancia
PostgreSQL administrada en Render:

1. Sube el código a un repositorio de GitHub sin incluir `.env` ni archivos
   `.sqlite3`.
2. En Render, elige **New > Blueprint**, conecta el repositorio y confirma la
   configuración de `render.yaml`.
3. Render instala las dependencias, recopila los archivos estáticos, ejecuta las
   migraciones al iniciar y publica una URL HTTPS. El primer arranque puede
   tardar varios minutos.
4. La base de datos de Render es independiente de la PostgreSQL local. Las
   credenciales del administrador de demostración local no se publican ni se
   copian al servicio. Crea un administrador nuevo y seguro para el sitio
   publicado; no reutilices las credenciales locales de demostración.

La configuración usa el plan gratuito para una demostración académica. Los
servicios gratuitos pueden pausarse por inactividad o tener límites de
disponibilidad; consulta las condiciones actuales de Render antes de depender
de ellos para uso permanente.

## Ver los datos en pgAdmin

Para la base local, abre pgAdmin y navega por **Servers > PostgreSQL >
Databases > retos_db > Schemas > public > Tables**. Si no aparece, actualiza
`Databases` con clic derecho en **Refresh**. Para abrir las filas de una tabla,
haz clic derecho en su nombre y selecciona **View/Edit Data > All Rows**.
También puedes usar **Tools > Query Tool** y ejecutar:

```sql
SELECT * FROM retos_categoria;
SELECT * FROM retos_reto;
SELECT * FROM retos_envio;
SELECT * FROM retos_retoresuelto;
```

Los nombres exactos pueden confirmarse en **public > Tables**. Estas tablas
corresponden a la PostgreSQL local (`localhost:5432`, base `retos_db`); la base
de Render es otra y sus registros no aparecerán en tu pgAdmin local a menos que
configures una conexión remota autorizada.

## Pruebas

```powershell
python manage.py test
```
