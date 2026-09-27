from django.contrib import admin
from .models import Pelicula, Actor, Director, Genero, Resena, Perfil

admin.site.register(Pelicula)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Genero)
admin.site.register(Resena)
admin.site.register(Perfil)