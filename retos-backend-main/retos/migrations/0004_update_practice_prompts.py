from django.db import migrations


PROMPTS = {
    "Suma de dos números": (
        "Escribe un programa Python que calcule 7 + 5 e imprima el resultado.",
        "12",
    ),
    "Condicional par o impar": (
        "Guarda 8 en una variable y usa un if para imprimir True si el número es par.",
        "True",
    ),
    "Contar caracteres": (
        'Guarda "python" en una variable y usa len() para imprimir cuántas letras tiene.',
        "6",
    ),
}


def actualizar_enunciados(apps, schema_editor):
    Reto = apps.get_model("retos", "Reto")
    for titulo, (descripcion, respuesta) in PROMPTS.items():
        Reto.objects.filter(titulo=titulo).update(
            descripcion=descripcion,
            respuesta_correcta=respuesta,
        )


def restaurar_enunciados(apps, schema_editor):
    Reto = apps.get_model("retos", "Reto")
    Reto.objects.filter(titulo="Suma de dos números").update(
        descripcion="¿Cuál es el resultado de sumar 7 + 5?",
        respuesta_correcta="12",
    )
    Reto.objects.filter(titulo="Condicional par o impar").update(
        descripcion='Para n = 8, si el programa comprueba n % 2 == 0, ¿qué palabra debe mostrar: "par" o "impar"?',
        respuesta_correcta="par",
    )
    Reto.objects.filter(titulo="Contar caracteres").update(
        descripcion='¿Cuántas letras tiene la palabra "python"?',
        respuesta_correcta="6",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("retos", "0003_seed_practice_challenges"),
    ]

    operations = [
        migrations.RunPython(actualizar_enunciados, restaurar_enunciados),
    ]
