from django.db import migrations


CATEGORIES = [
    {
        "nombre": "Estructuras de datos",
        "descripcion": "Retos de listas y organización de información.",
    },
    {
        "nombre": "Matemática y lógica",
        "descripcion": "Retos de razonamiento, operaciones y patrones.",
    },
]

SUBMISSIONS = [
    {
        "usuario": "Ana Rivas",
        "usuario_resuelto": "ana rivas",
        "reto": "Suma de dos números",
        "codigo": "print(7 + 5)",
        "estado": "ACEPTADO",
        "resuelto": True,
    },
    {
        "usuario": "Bruno Torres",
        "usuario_resuelto": "bruno torres",
        "reto": "Área de un rectángulo",
        "codigo": "base = 4\naltura = 3\nprint(base * altura)",
        "estado": "ACEPTADO",
        "resuelto": True,
    },
    {
        "usuario": "Camila Ortiz",
        "usuario_resuelto": "camila ortiz",
        "reto": "Suma acumulada",
        "codigo": "total = 0\nfor numero in range(1, 6):\n    total += numero\nprint(total)",
        "estado": "ACEPTADO",
        "resuelto": True,
    },
    {
        "usuario": "Diego Fuentes",
        "usuario_resuelto": "diego fuentes",
        "reto": "Tabla del siete",
        "codigo": "print(7)",
        "estado": "RECHAZADO",
        "resuelto": False,
    },
    {
        "usuario": "Elena Mora",
        "usuario_resuelto": "elena mora",
        "reto": "Mayor de una lista",
        "codigo": "print(max([4, 9, 2, 7]))",
        "estado": "PENDIENTE",
        "resuelto": False,
    },
]


def crear_datos_demo(apps, schema_editor):
    Categoria = apps.get_model("retos", "Categoria")
    Reto = apps.get_model("retos", "Reto")
    RetoResuelto = apps.get_model("retos", "RetoResuelto")
    Envio = apps.get_model("retos", "Envio")
    database = schema_editor.connection.alias

    for datos in CATEGORIES:
        Categoria.objects.using(database).get_or_create(
            nombre=datos["nombre"],
            defaults={"descripcion": datos["descripcion"]},
        )

    for datos in SUBMISSIONS:
        reto = Reto.objects.using(database).get(titulo=datos["reto"])
        Envio.objects.using(database).get_or_create(
            reto_id=reto.pk,
            usuario=datos["usuario"],
            codigo_fuente=datos["codigo"],
            defaults={
                "lenguaje": "python",
                "estado": datos["estado"],
            },
        )
        if datos["resuelto"]:
            RetoResuelto.objects.using(database).get_or_create(
                usuario=datos["usuario_resuelto"],
                reto_id=reto.pk,
                defaults={"puntos_obtenidos": reto.puntos},
            )


def eliminar_datos_demo(apps, schema_editor):
    Categoria = apps.get_model("retos", "Categoria")
    Reto = apps.get_model("retos", "Reto")
    RetoResuelto = apps.get_model("retos", "RetoResuelto")
    Envio = apps.get_model("retos", "Envio")
    database = schema_editor.connection.alias

    for datos in SUBMISSIONS:
        reto = Reto.objects.using(database).get(titulo=datos["reto"])
        Envio.objects.using(database).filter(
            reto_id=reto.pk,
            usuario=datos["usuario"],
            codigo_fuente=datos["codigo"],
        ).delete()
        if datos["resuelto"]:
            RetoResuelto.objects.using(database).filter(
                usuario=datos["usuario_resuelto"],
                reto_id=reto.pk,
            ).delete()

    for datos in CATEGORIES:
        category = Categoria.objects.using(database).filter(
            nombre=datos["nombre"],
            descripcion=datos["descripcion"],
        ).first()
        if category and not Reto.objects.using(database).filter(
            categoria_id=category.pk
        ).exists():
            category.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("retos", "0005_expand_practice_challenges"),
    ]

    operations = [
        migrations.RunPython(crear_datos_demo, eliminar_datos_demo),
    ]
