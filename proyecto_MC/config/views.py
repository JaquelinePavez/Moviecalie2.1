from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from peliculas.models import Pelicula # Importe la lista de películas que definimos


def inicio(request):
    peliculas = Pelicula.objects.all()
    contexto = {
        "titulo_pagina": "Inicio",
        "peliculas": peliculas,
    }
    return render(request, "inicio.html", contexto)


def registro_usuario(request):
    if request.method == "GET":
        formulario = UserCreationForm() #UserCreationForm crea un formulario vacio
        contexto = {"formulario": formulario}
        return render(request, "registro.html", contexto)

    if request.method == "POST":
        formulario = UserCreationForm(request.POST) #crea el formulario con los datos que el usuario envio para poder validarlo
        if formulario.is_valid(): #is_valid() corre todas las validaciones del formulario (usuario único, contraseñas
            nuevo_usuario = formulario.save() #.save crea el usuario en la base de dato y lo devuelve
            login(request, nuevo_usuario) #funcion que crea la sesion
            return redirect("peliculas:catalogo") #arma la url y devuelve una respuesta de redireccion 
             # logueamos automáticamente al usuario recién creado,
            # así no tiene que volver a escribir usuario/contraseña en otra pantalla
        else:
            contexto = {"formulario": formulario}
            return render(request, "registro.html", contexto)



