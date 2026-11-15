from django.contrib import admin

from .models import Actor, Director, Genero, Pelicula, Resena

admin.site.register(Pelicula)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Genero)


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    """Admin para el modelo Resena."""
    list_display = ("pelicula", "autor", "calificacion")
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj)
