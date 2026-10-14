from urllib.parse import urlencode

from django.contrib import messages
from django.db import transaction
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from rest_framework import permissions, viewsets

from .models import Categoria, Envio, Reto, RetoResuelto
from .reportes import obtener_registro_participantes
from .serializers import CategoriaSerializer, EnvioSerializer, RetoSerializer
from .validadores import CodigoNoPermitido, ejecutar_codigo_restringido


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class RetoViewSet(viewsets.ModelViewSet):
    queryset = Reto.objects.all()
    serializer_class = RetoSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class EnvioViewSet(viewsets.ModelViewSet):
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer
    permission_classes = [permissions.IsAdminUser]


def home(request):
    retos_list = Reto.objects.filter(activo=True).select_related("categoria").order_by("id")
    estadisticas = retos_list.aggregate(suma_puntos=Sum("puntos"), promedio_puntos=Avg("puntos"))
    total_retos = retos_list.count()

    contexto = {
        "nombre_plataforma": "Plataforma de Retos de Programación API",
        "total_retos": total_retos,
        "suma_puntos": estadisticas["suma_puntos"] or 0,
        "promedio_puntos": estadisticas["promedio_puntos"] or 0,
        "activa": True,
        "retos": retos_list,
    }
    return render(request, "retos/index.html", contexto)


def jugar(request):
    usuario = " ".join(request.GET.get("usuario", "").strip().split())[:80]
    retos = Reto.objects.filter(activo=True).select_related("categoria").order_by("id")
    completados = set()
    puntos_usuario = 0
    if usuario:
        resoluciones = RetoResuelto.objects.filter(usuario=usuario.casefold())
        completados = set(resoluciones.values_list("reto_id", flat=True))
        puntos_usuario = resoluciones.aggregate(total=Sum("puntos_obtenidos"))["total"] or 0

    contexto = {
        "retos_por_dificultad": [
            {
                "nombre": nombre,
                "retos": retos.filter(dificultad=codigo),
            }
            for codigo, nombre in [
                ("FACIL", "Fáciles"),
                ("MEDIA", "Medios"),
                ("DIFICIL", "Difíciles"),
            ]
        ],
        "total_retos": retos.count(),
        "usuario": usuario,
        "retos_completados": completados,
        "puntos_usuario": puntos_usuario,
        "registro_participantes": obtener_registro_participantes(),
    }
    return render(request, "retos/jugar.html", contexto)


def detalle_reto(request, reto_id):
    reto = get_object_or_404(Reto, pk=reto_id, activo=True)
    usuario = " ".join(request.GET.get("usuario", "").strip().split())[:80]
    completado = bool(
        usuario
        and RetoResuelto.objects.filter(usuario=usuario.casefold(), reto=reto).exists()
    )
    return render(
        request,
        "retos/resolver.html",
        {
            "reto": reto,
            "usuario": usuario,
            "completado": completado,
            "puntos_usuario": (
                RetoResuelto.objects.filter(usuario=usuario.casefold()).aggregate(
                    total=Sum("puntos_obtenidos")
                )["total"]
                or 0
                if usuario
                else 0
            ),
        },
    )


@require_POST
def resolver_reto(request, reto_id):
    reto = get_object_or_404(Reto, pk=reto_id, activo=True)
    usuario = " ".join(request.POST.get("usuario", "").strip().split())
    codigo = request.POST.get("codigo_fuente", "")

    if not usuario or len(usuario) > 80:
        messages.error(request, "Escribe un nombre de hasta 80 caracteres antes de enviar.")
    elif not codigo.strip() or len(codigo) > 2000:
        messages.error(request, "Escribe una solución de hasta 2000 caracteres.")
    else:
        try:
            salida = ejecutar_codigo_restringido(codigo)
        except CodigoNoPermitido as error:
            Envio.objects.create(
                reto=reto,
                usuario=usuario[:80],
                codigo_fuente=codigo,
                lenguaje="python",
                estado="RECHAZADO",
            )
            messages.error(request, str(error))
        except (ArithmeticError, IndexError, KeyError, TypeError, ValueError, OverflowError):
            Envio.objects.create(
                reto=reto,
                usuario=usuario[:80],
                codigo_fuente=codigo,
                lenguaje="python",
                estado="RECHAZADO",
            )
            messages.error(request, "No se pudo resolver con esos valores. Revisa tu código.")
        else:
            aceptado = " ".join(salida.casefold().split()) == " ".join(
                reto.respuesta_correcta.casefold().split()
            )
            Envio.objects.create(
                reto=reto,
                usuario=usuario[:80],
                codigo_fuente=codigo,
                lenguaje="python",
                estado="ACEPTADO" if aceptado else "RECHAZADO",
            )
            if aceptado:
                with transaction.atomic():
                    _, creado = RetoResuelto.objects.get_or_create(
                        usuario=usuario.casefold(),
                        reto=reto,
                        defaults={"puntos_obtenidos": reto.puntos},
                    )
                if creado:
                    messages.success(request, f"¡Correcto! Tu programa imprimió {salida}. Ganaste {reto.puntos} puntos.")
                else:
                    messages.info(request, "Solución correcta. Ya habías ganado los puntos de este reto.")
            else:
                messages.error(request, "La salida de tu programa no es la esperada. ¡Inténtalo otra vez!")

    query = urlencode({"usuario": usuario}) if usuario else ""
    destino = reverse("detalle_reto", args=[reto.id])
    return redirect(f"{destino}?{query}" if query else destino)


def pagina_error_404(request, exception):
    return render(request, "404.html", status=404)