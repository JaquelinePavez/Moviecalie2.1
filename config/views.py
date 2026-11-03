from django.shortcuts import render
from peliculas.models import Pelicula # Importe la lista de películas que definimos


def inicio(request):
    peliculas = Pelicula.objects.all()
    contexto = {
        "titulo_pagina": "Inicio",
        "peliculas": peliculas,
    }
    return render(request, "inicio.html", contexto)




