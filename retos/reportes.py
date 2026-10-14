from django.db.models import Count, Max, Sum

from .models import Envio, RetoResuelto


def obtener_registro_participantes():
    participantes = {}

    for envio in (
        Envio.objects.values("usuario")
        .annotate(ultima_actividad=Max("fecha_envio"))
        .order_by()
    ):
        clave = envio["usuario"].casefold()
        participante = participantes.setdefault(
            clave,
            {
                "usuario": envio["usuario"],
                "ultima_actividad": envio["ultima_actividad"],
                "ejercicios": 0,
                "puntos": 0,
            },
        )
        if envio["ultima_actividad"] > participante["ultima_actividad"]:
            participante["usuario"] = envio["usuario"]
            participante["ultima_actividad"] = envio["ultima_actividad"]

    for resultado in (
        RetoResuelto.objects.values("usuario")
        .annotate(
            ejercicios=Count("reto_id", distinct=True),
            puntos=Sum("puntos_obtenidos"),
            ultima_actividad=Max("fecha_resolucion"),
        )
        .order_by()
    ):
        clave = resultado["usuario"].casefold()
        participante = participantes.setdefault(
            clave,
            {
                "usuario": resultado["usuario"],
                "ultima_actividad": resultado["ultima_actividad"],
                "ejercicios": 0,
                "puntos": 0,
            },
        )
        participante["ejercicios"] = resultado["ejercicios"]
        participante["puntos"] = resultado["puntos"] or 0
        if resultado["ultima_actividad"] > participante["ultima_actividad"]:
            participante["ultima_actividad"] = resultado["ultima_actividad"]

    registro = list(participantes.values())
    registro.sort(key=lambda participante: participante["ultima_actividad"], reverse=True)
    registro.sort(key=lambda participante: participante["puntos"], reverse=True)
    return registro
