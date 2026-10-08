from django.urls import path
from . import views

app_name = "peliculas"

urlpatterns = [ 
    path("<int:pk>/editar/", views.editar_resenas, name="editar_resenas"),

    #agregue la vista basada en clases
    path("<int:pk>/resenas/eliminar/", views.ResenaEliminar.as_view(), name="resena_eliminar"),
    
    #path("<int:id>/", views.detalle_pelicula, name="detalle"),
    path("<int:id>/resenas/", views.detalle_resenas_pelicula, name="resenas_pelicula"),
    path('catalogo/', views.catalogo_peliculas, name='catalogo'),
]