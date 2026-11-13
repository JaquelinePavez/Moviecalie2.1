from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from .models import Perfil, Usuario


class UsuarioCreacionForm(UserCreationForm):
    """
    Formulario que se utiliza para crear nuevos usuarios
    desde el administrador de Django.
    """
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "email")


class UsuarioAdmin(UserAdmin):
    """
    Personaliza la administración de usuarios en Django.
    Permite definir qué campos aparecen al crear un usuario
    y cuáles pueden modificarse según los permisos.
    """
    add_form = UsuarioCreacionForm
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )


    def get_readonly_fields(self, request, obj=None):
        """
        Define qué campos se muestran como solo lectura.
        El superusuario puede editar todos los campos,
        mientras que el moderador tiene algunos campos bloqueados.
        """
        campos_normales = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            return campos_normales

        campos_de_solo_lectura = (
            "password", "username", "email", "first_name", "last_name",
            "is_staff", "is_superuser", "groups", "user_permissions",
            "last_login", "date_joined",
        )
        return campos_normales + campos_de_solo_lectura


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Perfil)
