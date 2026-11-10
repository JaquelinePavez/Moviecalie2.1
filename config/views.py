from django.shortcuts import render
from peliculas.models import Pelicula


def inicio(request):
    peliculas = Pelicula.objects.all()
    contexto = {
        "titulo_pagina": "Inicio",
        "peliculas": peliculas,
    }
    return render(request, "inicio.html", contexto)


"""Intención de mudar el inicio de la pagina al catalogo para una mejor visualización
debido que ambas paginas realizan lo mismo."""

