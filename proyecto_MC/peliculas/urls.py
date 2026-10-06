from django.urls import path
from . import views

app_name = "peliculas"

urlpatterns = [ 
    path("editar/<int:pk>/", views.editar_resenas, name="editar_resenas"),
    #path("<int:id>/", views.detalle_pelicula, name="detalle"),
    path("<int:id>/resenas/", views.detalle_resenas_pelicula, name="resenas_pelicula"),
    path('catalogo/', views.catalogo_peliculas, name='catalogo'),
]

