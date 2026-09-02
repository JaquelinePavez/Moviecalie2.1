from django.shortcuts import render
from peliculas.views import peliculas # Importe la lista de películas que definimos

  #refatorice a inicio moviendolo al proyecto porque es una página general del sitio y no una funcionalidad exclusivade la aplicación "peliculas".
def inicio(request):
    contexto = {"titulo_pagina": "Inicio",
                "peliculas": peliculas
                }
    return render(request, "peliculas/inicio.html", contexto)