from django.db import migrations


PRACTICE_CHALLENGES = [
    {
        "titulo": "Suma de dos números",
        "descripcion": "¿Cuál es el resultado de sumar 7 + 5?",
        "respuesta_correcta": "12",
        "puntos": 10,
    },
    {
        "titulo": "Condicional par o impar",
        "descripcion": 'Para n = 8, si el programa comprueba n % 2 == 0, ¿qué palabra debe mostrar: "par" o "impar"?',
        "respuesta_correcta": "par",
        "puntos": 15,
    },
    {
        "titulo": "Contar caracteres",
        "descripcion": '¿Cuántas letras tiene la palabra "python"?',
        "respuesta_correcta": "6",
        "puntos": 10,
    },
]


def crear_retos_de_practica(apps, schema_editor):
    Categoria = apps.get_model("retos", "Categoria")
    Reto = apps.get_model("retos", "Reto")
    categoria, _ = Categoria.objects.get_or_create(
        nombre="Fundamentos de programación",
        defaults={"descripcion": "Retos introductorios de lógica y programación."},
    )

    for datos in PRACTICE_CHALLENGES:
        Reto.objects.get_or_create(
            titulo=datos["titulo"],
            defaults={
                **datos,
                "dificultad": "FACIL",
                "activo": True,
                "categoria_id": categoria.pk,
            },
        )


def eliminar_retos_de_practica(apps, schema_editor):
    Categoria = apps.get_model("retos", "Categoria")
    Reto = apps.get_model("retos", "Reto")
    Reto.objects.filter(titulo__in=[reto["titulo"] for reto in PRACTICE_CHALLENGES]).delete()
    Categoria.objects.filter(
        nombre="Fundamentos de programación",
        retos__isnull=True,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("retos", "0002_reto_respuesta_correcta_retoresuelto"),
    ]

    operations = [
        migrations.RunPython(crear_retos_de_practica, eliminar_retos_de_practica),
    ]
