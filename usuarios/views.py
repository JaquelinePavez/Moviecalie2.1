from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import RegistroForm


@require_http_methods(["GET", "POST"])
def registro_usuario(request):
    """
    Se encarga de registrar nuevos usuarios.
    Muestra el formulario de registro, valida los datos ingresados
    y, si todo está correcto, crea la cuenta y le asigna un grupo.
    """

    if request.method == "GET":
        formulario = RegistroForm()
        contexto = {"formulario": formulario}
        return render(request, "usuarios/registro.html", contexto)

    if request.method == "POST":
        formulario = RegistroForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            grupo, _ = Group.objects.get_or_create(name="Criticos")

            usuario.groups.add(grupo)
            messages.success(request, "Cuenta creada. Ya podés iniciar sesión.")
            return redirect("usuarios:login")
        else:
            contexto = {"formulario": formulario}
            return render(request, "usuarios/registro.html", contexto)
