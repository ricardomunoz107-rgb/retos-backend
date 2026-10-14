from django.db import migrations


CHALLENGES = [
    {
        "titulo": "Suma de dos números",
        "descripcion": "Escribe un programa Python que calcule 7 + 5 e imprima el resultado.",
        "respuesta_correcta": "12",
        "dificultad": "FACIL",
        "puntos": 10,
    },
    {
        "titulo": "Condicional par o impar",
        "descripcion": "Guarda 8 en una variable y usa un if para imprimir True si el número es par.",
        "respuesta_correcta": "True",
        "dificultad": "FACIL",
        "puntos": 10,
    },
    {
        "titulo": "Contar caracteres",
        "descripcion": 'Guarda "python" en una variable y usa len() para imprimir cuántas letras tiene.',
        "respuesta_correcta": "6",
        "dificultad": "FACIL",
        "puntos": 10,
    },
    {
        "titulo": "Área de un rectángulo",
        "descripcion": "Guarda base = 4 y altura = 3. Imprime el área del rectángulo.",
        "respuesta_correcta": "12",
        "dificultad": "FACIL",
        "puntos": 10,
    },
    {
        "titulo": "Suma acumulada",
        "descripcion": "Usa un ciclo for para sumar los números del 1 al 5 e imprimir el total.",
        "respuesta_correcta": "15",
        "dificultad": "MEDIA",
        "puntos": 20,
    },
    {
        "titulo": "Factorial de cinco",
        "descripcion": "Calcula 5! con un ciclo for e imprime el resultado. Recuerda que 5! = 1 × 2 × 3 × 4 × 5.",
        "respuesta_correcta": "120",
        "dificultad": "MEDIA",
        "puntos": 20,
    },
    {
        "titulo": "FizzBuzz del uno al cinco",
        "descripcion": 'Recorre del 1 al 5. Imprime "Fizz" para múltiplos de 3, "Buzz" para múltiplos de 5 y el número en los demás casos.',
        "respuesta_correcta": "1 2 Fizz 4 Buzz",
        "dificultad": "MEDIA",
        "puntos": 20,
    },
    {
        "titulo": "Mayor de una lista",
        "descripcion": "Encuentra e imprime el número mayor de la lista [4, 9, 2, 7] usando max().",
        "respuesta_correcta": "9",
        "dificultad": "MEDIA",
        "puntos": 20,
    },
    {
        "titulo": "Suma de números pares",
        "descripcion": "Usa un ciclo y un if para sumar los números pares del 1 al 10. Imprime el total.",
        "respuesta_correcta": "30",
        "dificultad": "DIFICIL",
        "puntos": 30,
    },
    {
        "titulo": "Comprobar si un número es primo",
        "descripcion": "Comprueba con un ciclo si 7 es primo. Imprime True si es primo y False si no lo es.",
        "respuesta_correcta": "True",
        "dificultad": "DIFICIL",
        "puntos": 30,
    },
    {
        "titulo": "Secuencia de Fibonacci",
        "descripcion": "Comienza con 0 y 1, avanza seis veces en la secuencia de Fibonacci e imprime el último número generado.",
        "respuesta_correcta": "8",
        "dificultad": "DIFICIL",
        "puntos": 30,
    },
    {
        "titulo": "Tabla del siete",
        "descripcion": "Usa un ciclo para imprimir la tabla del 7 desde 7 × 1 hasta 7 × 10.",
        "respuesta_correcta": "7 14 21 28 35 42 49 56 63 70",
        "dificultad": "DIFICIL",
        "puntos": 30,
    },
]


def actualizar_retos(apps, schema_editor):
    Categoria = apps.get_model("retos", "Categoria")
    Reto = apps.get_model("retos", "Reto")
    categoria, _ = Categoria.objects.get_or_create(
        nombre="Fundamentos de programación",
        defaults={"descripcion": "Retos de lógica y programación."},
    )

    for datos in CHALLENGES:
        Reto.objects.update_or_create(
            titulo=datos["titulo"],
            defaults={
                **datos,
                "activo": True,
                "categoria_id": categoria.pk,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("retos", "0004_update_practice_prompts"),
    ]

    operations = [
        migrations.RunPython(actualizar_retos, migrations.RunPython.noop),
    ]
