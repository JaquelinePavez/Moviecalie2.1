from django.contrib import admin

from .models import Actor, Director, Genero, Pelicula, Resena

admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Genero)


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    """Admin para el modelo Pelicula."""

    # La calificación se calcula a partir de las reseñas:
    # se muestra, pero no se puede editar a mano.
    readonly_fields = ["calificacion_promedio"]


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

    def delete_queryset(self, request, queryset):
        """Borra las reseñas de a una para que se ejecute
        Resena.delete() y se recalcule la calificación."""
        for resena in queryset:
            resena.delete()