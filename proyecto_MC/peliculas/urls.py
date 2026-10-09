from django.urls import path
from . import views_cbv
from . import views_fbv

app_name = "peliculas"

urlpatterns = [ 
        #vistas basadas en funciones
    path("<int:pk>/editar/", views_fbv.editar_resenas, name="editar_resenas"),
    # Antes:
    # path("<int:pk>/resenas/eliminar/", views_fbv.eliminar_reseña, name="resena"),
    path("resenas/<int:pk>/eliminar/", views_fbv.eliminar_resena, name="resena_eliminar"),
    path("<int:id>/resenas/agregar/", views_fbv.agregar_resena, name="agregar"),
    path("<int:id>/resenas/", views_fbv.detalle, name="detalle"), #cambie name= resenas_peliculas por detalle y detalle_resena_pelicula por detalle
    path('catalogo/', views_fbv.catalogo_peliculas, name='catalogo'),
    
    #vistas basadas en clases
    path("<int:id>/resenas/", views_cbv.ResenaLista.as_view(), name="resenas_pelicula_cbv"),
    path("<int:id>/resenas/nueva/", views_cbv.ResenaCrear.as_view(), name="crear_resena_cbv"),
    path("resenas/<int:pk>/", views_cbv.ResenaDetalle.as_view(), name="detalle_resena_cbv"),
    path("<int:pk>/editar/", views_cbv.ResenaEditar.as_view(), name="editar_resenas_cbv"),
    path("<int:pk>/resenas/eliminar/", views_cbv.ResenaEliminar.as_view(), name="eliminar_resena_cbv"),
]