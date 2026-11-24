from django.db import migrations


SUBMISSIONS = [
    {
        "usuario": "Felipe Reyes",
        "reto": "Condicional par o impar",
        "codigo": (
            "numero = 8\n"
            "if numero % 2 == 0:\n"
            "    print(True)\n"
            "else:\n"
            "    print(False)"
        ),
        "estado": "ACEPTADO",
        "resuelto": True,
    },
    {
        "usuario": "Gabriela Silva",
        "reto": "Contar caracteres",
        "codigo": 'palabra = "python"\nprint(len(palabra))',
        "estado": "ACEPTADO",
        "resuelto": True,
    },
    {
        "usuario": "Hugo Paredes",
        "reto": "Suma acumulada",
        "codigo": (
            "total = 0\n"
            "for numero in range(1, 6):\n"
            "    total += numero\n"
            "print(total)"
        ),
        "estado": "ACEPTADO",
        "resuelto": True,
    },
    {
        "usuario": "Isabel Fuentes",
        "reto": "Mayor de una lista",
        "codigo": "print(max([4, 9, 2, 7]))",
        "estado": "ACEPTADO",
        "resuelto": True,
    },
    {
        "usuario": "Joaquín Soto",
        "reto": "Suma de números pares",
        "codigo": (
            "total = 0\n"
            "for numero in range(1, 11):\n"
            "    if numero % 2 == 0:\n"
            "        total += numero\n"
            "print(total)"
        ),
        "estado": "ACEPTADO",
        "resuelto": True,
    },
    {
        "usuario": "Karla Vega",
        "reto": "Factorial de cinco",
        "codigo": (
            "resultado = 1\n"
            "for numero in range(1, 5):\n"
            "    resultado *= numero\n"
            "print(resultado)"
        ),
        "estado": "RECHAZADO",
        "resuelto": False,
    },
    {
        "usuario": "Luis Araya",
        "reto": "Comprobar si un número es primo",
        "codigo": "numero = 7\nprint(numero % 2 == 0)",
        "estado": "RECHAZADO",
        "resuelto": False,
    },
    {
        "usuario": "María Paz",
        "reto": "Secuencia de Fibonacci",
        "codigo": "print(0)",
        "estado": "PENDIENTE",
        "resuelto": False,
    },
]


def agregar_actividad_demo(apps, schema_editor):
    Reto = apps.get_model("retos", "Reto")
    RetoResuelto = apps.get_model("retos", "RetoResuelto")
    Envio = apps.get_model("retos", "Envio")
    database = schema_editor.connection.alias

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
                usuario=datos["usuario"].casefold(),
                reto_id=reto.pk,
                defaults={"puntos_obtenidos": reto.puntos},
            )


def eliminar_actividad_demo(apps, schema_editor):
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
                usuario=datos["usuario"].casefold(),
                reto_id=reto.pk,
            ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("retos", "0006_seed_demo_records"),
    ]

    operations = [
        migrations.RunPython(agregar_actividad_demo, eliminar_actividad_demo),
    ]
