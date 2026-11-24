from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet,
    CategoriaCreateView,
    CategoriaDeleteView,
    CategoriaDetailView,
    CategoriaListView,
    CategoriaUpdateView,
    EnvioCreateView,
    EnvioDeleteView,
    EnvioDetailView,
    EnvioListView,
    EnvioUpdateView,
    EnvioViewSet,
    RetoCreateView,
    RetoDeleteView,
    RetoDetailView,
    RetoListView,
    RetoResueltoCreateView,
    RetoResueltoDeleteView,
    RetoResueltoDetailView,
    RetoResueltoListView,
    RetoResueltoUpdateView,
    RetoResueltoViewSet,
    RetoUpdateView,
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
router.register(r'retos-resueltos', RetoResueltoViewSet)

urlpatterns = [
    path("", home, name="home"),
    path("jugar/", jugar, name="jugar"),
    path("jugar/<int:reto_id>/", detalle_reto, name="detalle_reto"),
    path("jugar/<int:reto_id>/resolver/", resolver_reto, name="resolver_reto"),
    path("gestion/categorias/", CategoriaListView.as_view(), name="gestion-categoria-list"),
    path("gestion/categorias/nueva/", CategoriaCreateView.as_view(), name="gestion-categoria-create"),
    path("gestion/categorias/<int:pk>/", CategoriaDetailView.as_view(), name="gestion-categoria-detail"),
    path("gestion/categorias/<int:pk>/editar/", CategoriaUpdateView.as_view(), name="gestion-categoria-update"),
    path("gestion/categorias/<int:pk>/eliminar/", CategoriaDeleteView.as_view(), name="gestion-categoria-delete"),
    path("gestion/retos/", RetoListView.as_view(), name="gestion-reto-list"),
    path("gestion/retos/nuevo/", RetoCreateView.as_view(), name="gestion-reto-create"),
    path("gestion/retos/<int:pk>/", RetoDetailView.as_view(), name="gestion-reto-detail"),
    path("gestion/retos/<int:pk>/editar/", RetoUpdateView.as_view(), name="gestion-reto-update"),
    path("gestion/retos/<int:pk>/eliminar/", RetoDeleteView.as_view(), name="gestion-reto-delete"),
    path("gestion/retos-resueltos/", RetoResueltoListView.as_view(), name="gestion-reto-resuelto-list"),
    path("gestion/retos-resueltos/nuevo/", RetoResueltoCreateView.as_view(), name="gestion-reto-resuelto-create"),
    path("gestion/retos-resueltos/<int:pk>/", RetoResueltoDetailView.as_view(), name="gestion-reto-resuelto-detail"),
    path("gestion/retos-resueltos/<int:pk>/editar/", RetoResueltoUpdateView.as_view(), name="gestion-reto-resuelto-update"),
    path("gestion/retos-resueltos/<int:pk>/eliminar/", RetoResueltoDeleteView.as_view(), name="gestion-reto-resuelto-delete"),
    path("gestion/envios/", EnvioListView.as_view(), name="gestion-envio-list"),
    path("gestion/envios/nuevo/", EnvioCreateView.as_view(), name="gestion-envio-create"),
    path("gestion/envios/<int:pk>/", EnvioDetailView.as_view(), name="gestion-envio-detail"),
    path("gestion/envios/<int:pk>/editar/", EnvioUpdateView.as_view(), name="gestion-envio-update"),
    path("gestion/envios/<int:pk>/eliminar/", EnvioDeleteView.as_view(), name="gestion-envio-delete"),
    path("api/", include(router.urls)),
]