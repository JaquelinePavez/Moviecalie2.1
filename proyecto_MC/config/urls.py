from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),

    #aca esta url raíz "/" seria el inicio general del proyecto.
    path("", views.inicio, name="inicio"),
    path("peliculas/", include("peliculas.urls")),
]