from django.urls import path
from . import views

app_name = "peliculas"

urlpatterns = [ 
    path("<int:pk>/editar/", views.editar_resenas, name="editar_resenas"),

    #agregue la vista basada en clases
    path("<int:pk>/resenas/eliminar/", views.ResenaEliminar.as_view(), name="resena_eliminar"),
    
    path("<int:id>/resenas/agregar/", views.agregar_resena, name="agregar"),
    path("<int:id>/resenas/", views.detalle, name="detalle"), #cambie name= resenas_peliculas por detalle y detalle_resena_pelicula por detalle
    path('catalogo/', views.catalogo_peliculas, name='catalogo'),
]