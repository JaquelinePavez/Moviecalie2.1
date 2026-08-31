from django.urls import path
from . import views

app_name = "peliculas"

urlpatterns = [ 
    path("agregar/", views.agregar_pelicula, name="agregar"),
    path("<int:id>/", views.detalle_pelicula, name="detalle"),
    path("<int:id>/resenas/", views.detalle_resenas_pelicula, name="resenas_pelicula"),
]



#-------Reseñas ------------# 
#se puede implementar de esta manera pensando para cuando 
# crezca el archivo y agregemos eliminar, editar reseñas 
# sea mas facil ubicar el bloque---#
    #path("<int:id>/resenas/", include("peliculas.resenas_urls"))
    # creando un archivo nuevo resenas_url.py con:
    # peliculas/resenas_urls.py
    #urlpatterns = [
    #path("<int:id>/", views.detalle_resenas_pelicula, name="resenas_pelicula"),  # ← acá está el duplicado]