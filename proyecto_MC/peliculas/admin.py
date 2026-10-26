from django.contrib import admin
from .models import Pelicula, Actor, Director, Genero, Resena

# Catálogo: datos compartidos, admin común.
admin.site.register(Pelicula)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Genero)


# En el admin las reseñas solo se VEN y se ELIMINAN (moderación).
# Editarlas lo hace el autor desde el sitio público.
@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ("pelicula", "autor", "calificacion")

    # Nadie edita reseñas desde el admin.
    def has_change_permission(self, request, obj=None):
        return False

    # Nadie crea reseñas desde el admin
    def has_add_permission(self, request):
        return False

    # Eliminar: se deja el comportamiento normal de Django. Puede eliminar quien
    # tenga el permiso delete_resena (Moderadores y superusuario).
    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj)