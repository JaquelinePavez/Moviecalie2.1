from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistroForm 


def registro_usuario(request):

    if request.method == "GET":
        formulario = RegistroForm()  # formulario vacío
        contexto = {"formulario": formulario}
        return render(request, "usuarios/registro.html", contexto)

    if request.method == "POST":
        formulario = RegistroForm(request.POST)  # formulario con los datos enviados, para validarlos
        if formulario.is_valid():  # corre las validaciones, incluida clean_email
            nuevo_usuario = formulario.save()  # crea el Usuario con la contraseña hasheada
            login(request, nuevo_usuario)  # crea la sesión
            return redirect("peliculas:catalogo")
        else:
            contexto = {"formulario": formulario}
            return render(request, "usuarios/registro.html", contexto)