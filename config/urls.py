from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

"""Url generales del proyecto."""
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.inicio, name="inicio"),   
    path("peliculas/", include("peliculas.urls")),
    path("usuarios/", include("usuarios.urls")),
]


"""
Sirve archivos media únicamente durante el desarrollo local /
esto es para que las imagenes que se van subiendo en el desarrollo local se puedan visualizar bien 
"""


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)