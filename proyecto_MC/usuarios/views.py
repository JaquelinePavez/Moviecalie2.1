#from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import RegistroForm 
from django.contrib.auth.models import Group

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import redirect_to_login
from django.views.decorators.http import require_http_methods, require_POST


@require_http_methods(["GET", "POST"])
def registro_usuario(request):

    if request.method == "GET":
        formulario = RegistroForm()  # formulario vacío
        contexto = {"formulario": formulario}
        return render(request, "usuarios/registro.html", contexto)

    if request.method == "POST":
        formulario = RegistroForm(request.POST)  # formulario con los datos enviados, para validarlos
        if formulario.is_valid():
            usuario = formulario.save()
            #el que decide el rol es el servidor, no el formulario, así nadie puede elegirse privilegios.
            grupo, _ = Group.objects.get_or_create(name="Criticos")

            usuario.groups.add(grupo)
            messages.success(request, "Cuenta creada. Ya podés iniciar sesión.")
            return redirect("usuarios:login")
        else:
            contexto = {"formulario": formulario}
            return render(request, "usuarios/registro.html", contexto)

        