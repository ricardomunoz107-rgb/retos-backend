from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import path, reverse

from .models import Categoria, Envio, Reto, RetoResuelto
from .reportes import obtener_registro_participantes

admin.site.register(Categoria)
admin.site.register(Reto)
admin.site.register(Envio)


@admin.register(RetoResuelto)
class RetoResueltoAdmin(admin.ModelAdmin):
    change_list_template = "admin/retos/retoresuelto/change_list.html"
    list_display = ("usuario", "reto", "puntos_obtenidos", "fecha_resolucion")
    list_select_related = ("reto",)
    list_filter = ("fecha_resolucion", "reto")
    search_fields = ("usuario", "reto__titulo")
    date_hierarchy = "fecha_resolucion"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "registro-participantes/",
                self.admin_site.admin_view(self.registro_participantes_view),
                name="registro_participantes",
            ),
        ]
        return custom_urls + urls

    def registro_participantes_view(self, request):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied

        contexto = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Registro de participantes",
            "registro_participantes": obtener_registro_participantes(),
            "changelist_url": reverse("admin:retos_retoresuelto_changelist"),
        }
        return render(request, "admin/retos/retoresuelto/registro_participantes.html", contexto)
