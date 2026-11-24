from urllib.parse import urlencode

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework import permissions, viewsets

from .forms import CategoriaForm, EnvioForm, RetoForm, RetoResueltoForm
from .models import Categoria, Envio, Reto, RetoResuelto
from .reportes import obtener_registro_participantes
from .serializers import (
    CategoriaSerializer,
    EnvioSerializer,
    RetoResueltoSerializer,
    RetoSerializer,
)
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


class RetoResueltoViewSet(viewsets.ModelViewSet):
    queryset = RetoResuelto.objects.select_related("reto").all()
    serializer_class = RetoResueltoSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("admin:login")

    def test_func(self):
        return self.request.user.is_staff


class CRUDContextMixin:
    model_label = ""
    section_title = ""
    route_prefix = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "model_label": self.model_label,
                "section_title": self.section_title,
                "list_url_name": f"{self.route_prefix}-list",
                "detail_url_name": f"{self.route_prefix}-detail",
                "create_url_name": f"{self.route_prefix}-create",
                "update_url_name": f"{self.route_prefix}-update",
                "delete_url_name": f"{self.route_prefix}-delete",
            }
        )
        return context

class CRUDListView(AdminRequiredMixin, ListView):
    template_name = "retos/crud/list.html"
    ordering = "pk"

    def get_queryset(self):
        related_fields = [
            field_name
            for field_name, _ in self.list_fields
            if self.model._meta.get_field(field_name).is_relation
        ]
        return super().get_queryset().select_related(*related_fields)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_columns"] = [label for _, label in self.list_fields]
        context["list_rows"] = [
            {
                "item": item,
                "values": [
                    self._display_value(getattr(item, field_name))
                    for field_name, _ in self.list_fields
                ],
            }
            for item in context["object_list"]
        ]
        return context

    @staticmethod
    def _display_value(value):
        if isinstance(value, bool):
            return "Sí" if value else "No"
        if value is None or value == "":
            return "—"
        return value


class CRUDDetailView(AdminRequiredMixin, DetailView):
    template_name = "retos/crud/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail_rows"] = []
        for field_name in self.detail_fields:
            field = self.model._meta.get_field(field_name)
            value = getattr(self.object, field_name)
            if isinstance(value, bool):
                value = "Sí" if value else "No"
            elif value is None or value == "":
                value = "—"
            context["detail_rows"].append(
                {"label": field.verbose_name.capitalize(), "value": value}
            )
        return context


class CRUDCreateView(AdminRequiredMixin, CreateView):
    template_name = "retos/crud/form.html"

    def get_success_url(self):
        return reverse(f"{self.route_prefix}-detail", kwargs={"pk": self.object.pk})


class CRUDUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "retos/crud/form.html"

    def get_success_url(self):
        return reverse(f"{self.route_prefix}-detail", kwargs={"pk": self.object.pk})


class CRUDDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "retos/crud/confirm_delete.html"

    def get_form_class(self):
        return forms.Form

    def get_success_url(self):
        return reverse(f"{self.route_prefix}-list")


class CategoriaCRUDMixin(CRUDContextMixin):
    model = Categoria
    form_class = CategoriaForm
    model_label = "Categoría"
    section_title = "Categorías"
    route_prefix = "gestion-categoria"
    detail_fields = ["nombre", "descripcion"]
    list_fields = [("nombre", "Nombre"), ("descripcion", "Descripción")]


class CategoriaListView(CategoriaCRUDMixin, CRUDListView):
    pass


class CategoriaDetailView(CategoriaCRUDMixin, CRUDDetailView):
    pass


class CategoriaCreateView(CategoriaCRUDMixin, CRUDCreateView):
    pass


class CategoriaUpdateView(CategoriaCRUDMixin, CRUDUpdateView):
    pass


class CategoriaDeleteView(CategoriaCRUDMixin, CRUDDeleteView):
    pass


class RetoCRUDMixin(CRUDContextMixin):
    model = Reto
    form_class = RetoForm
    model_label = "Reto"
    section_title = "Retos"
    route_prefix = "gestion-reto"
    list_fields = [
        ("titulo", "Título"),
        ("categoria", "Categoría"),
        ("dificultad", "Dificultad"),
        ("puntos", "Puntos"),
        ("activo", "Activo"),
    ]
    detail_fields = [
        "titulo",
        "descripcion",
        "dificultad",
        "puntos",
        "activo",
        "categoria",
        "respuesta_correcta",
        "fecha_creacion",
    ]


class RetoListView(RetoCRUDMixin, CRUDListView):
    pass


class RetoDetailView(RetoCRUDMixin, CRUDDetailView):
    pass


class RetoCreateView(RetoCRUDMixin, CRUDCreateView):
    pass


class RetoUpdateView(RetoCRUDMixin, CRUDUpdateView):
    pass


class RetoDeleteView(RetoCRUDMixin, CRUDDeleteView):
    pass


class RetoResueltoCRUDMixin(CRUDContextMixin):
    model = RetoResuelto
    form_class = RetoResueltoForm
    model_label = "Reto resuelto"
    section_title = "Retos resueltos"
    route_prefix = "gestion-reto-resuelto"
    list_fields = [
        ("usuario", "Participante"),
        ("reto", "Reto"),
        ("puntos_obtenidos", "Puntos"),
        ("fecha_resolucion", "Fecha de resolución"),
    ]
    detail_fields = ["usuario", "reto", "puntos_obtenidos", "fecha_resolucion"]


class RetoResueltoListView(RetoResueltoCRUDMixin, CRUDListView):
    pass


class RetoResueltoDetailView(RetoResueltoCRUDMixin, CRUDDetailView):
    pass


class RetoResueltoCreateView(RetoResueltoCRUDMixin, CRUDCreateView):
    pass


class RetoResueltoUpdateView(RetoResueltoCRUDMixin, CRUDUpdateView):
    pass


class RetoResueltoDeleteView(RetoResueltoCRUDMixin, CRUDDeleteView):
    pass


class EnvioCRUDMixin(CRUDContextMixin):
    model = Envio
    form_class = EnvioForm
    model_label = "Envío"
    section_title = "Envíos"
    route_prefix = "gestion-envio"
    list_fields = [
        ("usuario", "Participante"),
        ("reto", "Reto"),
        ("lenguaje", "Lenguaje"),
        ("estado", "Estado"),
        ("fecha_envio", "Fecha de envío"),
    ]
    detail_fields = ["reto", "usuario", "codigo_fuente", "lenguaje", "estado", "fecha_envio"]


class EnvioListView(EnvioCRUDMixin, CRUDListView):
    pass


class EnvioDetailView(EnvioCRUDMixin, CRUDDetailView):
    pass


class EnvioCreateView(EnvioCRUDMixin, CRUDCreateView):
    pass


class EnvioUpdateView(EnvioCRUDMixin, CRUDUpdateView):
    pass


class EnvioDeleteView(EnvioCRUDMixin, CRUDDeleteView):
    pass


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