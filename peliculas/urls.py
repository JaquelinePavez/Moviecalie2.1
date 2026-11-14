from django.urls import path

from . import views_cbv, views_fbv

app_name = "peliculas"

urlpatterns = [
    # vistas basadas en funciones
    path("<int:pk>/editar/", views_fbv.editar_resenas, name="editar_resenas"),
    path(
        "<int:pk>/resenas/eliminar/",
        views_fbv.eliminar_resena,
        name="eliminar_resena",
    ),
    path(
        "<int:id>/resenas/agregar/",
        views_fbv.agregar_resena,
        name="agregar",
    ),
    path("<int:id>/resenas/", views_fbv.detalle, name="detalle"),
    path("catalogo/", views_fbv.catalogo_peliculas, name="catalogo"),

    # vistas basadas en clases
    path(
        "cbv/catalogo/",
        views_cbv.PeliculaCatalogo.as_view(),
        name="catalogo_cbv",
    ),
    path(
        "cbv/peliculas/<int:pk>/",
        views_cbv.PeliculaDetalle.as_view(),
        name="detalle_pelicula_cbv",
    ),
    path(
        "cbv/peliculas/<int:id>/resenas/nueva/",
        views_cbv.ResenaCrear.as_view(),
        name="crear_resena_cbv",
    ),
    path(
        "cbv/resenas/<int:pk>/editar/",
        views_cbv.ResenaEditar.as_view(),
        name="editar_resenas_cbv",
    ),
    path(
        "cbv/resenas/<int:pk>/eliminar/",
        views_cbv.ResenaEliminar.as_view(),
        name="eliminar_resena_cbv",
    ),
]
