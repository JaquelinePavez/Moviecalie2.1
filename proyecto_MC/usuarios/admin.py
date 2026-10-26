from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Perfil

# Formulario de alta que usa el admin (pantalla "Añadir usuario").
class UsuarioCreacionForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "email")


# Admin del usuario: se hereda de UserAdmin (no de ModelAdmin genérico)
# porque Usuario hereda de AbstractUser.
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreacionForm      # formulario para crear
    add_fieldsets = (                   # campos de la pantalla de alta
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )


# Nombre fijo de Django: lista de campos que se ven pero NO se pueden editar.
    def get_readonly_fields(self, request, obj=None):
        campos_normales = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            return campos_normales          # el superusuario edita todo

        # Moderador: todo en solo lectura, menos "is_active" (Activo), que es el que bloquea
        campos_de_solo_lectura = (
            "password", "username", "email", "first_name", "last_name",
            "is_staff", "is_superuser", "groups", "user_permissions",
            "last_login", "date_joined",
        )
        return campos_normales + campos_de_solo_lectura


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Perfil)