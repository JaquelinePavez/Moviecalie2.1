#from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import RegistroForm 


def registro_usuario(request):

    if request.method == "GET":
        formulario = RegistroForm()  # formulario vacío
        contexto = {"formulario": formulario}
        return render(request, "usuarios/registro.html", contexto)

    if request.method == "POST":
        formulario = RegistroForm(request.POST)  # formulario con los datos enviados, para validarlos
        if formulario.is_valid():  # corre las validaciones, incluida clean_email
            # Guarda el usuario con la contraseña procesada de forma segura.
            formulario.save()
            messages.success(request, "Cuenta creada. Ya podés iniciar sesión.")

            # No iniciamos sesión automáticamente, debe ingresar con su cuenta recién creada.
            return redirect("usuarios:login")
           
            #nuevo_usuario = formulario.save()  # crea el Usuario con la contraseña hasheada
            # Ya no usamos login() porque el registro no inicia la sesión automáticamente.
            #login(request, nuevo_usuario)  # crea la sesión
            #return redirect("peliculas:catalogo")
        else:
            contexto = {"formulario": formulario}
            return render(request, "usuarios/registro.html", contexto)

        