from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet,
    EnvioViewSet,
    RetoViewSet,
    detalle_reto,
    home,
    jugar,
    resolver_reto,
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'retos', RetoViewSet)
router.register(r'envios', EnvioViewSet)

urlpatterns = [
    path("", home, name="home"),
    path("jugar/", jugar, name="jugar"),
    path("jugar/<int:reto_id>/", detalle_reto, name="detalle_reto"),
    path("jugar/<int:reto_id>/resolver/", resolver_reto, name="resolver_reto"),
    path("api/", include(router.urls)),
]