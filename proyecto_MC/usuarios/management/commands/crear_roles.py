from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Crea los grupos y les asigna permisos"

    def handle(self, *args, **opciones):
        # Defino los grupos con sus respectivos permisos.
        roles = {
            "Criticos": ["view_resena", "add_resena", "change_resena", "delete_resena"],
            "Moderadores": ["view_resena", "delete_resena", "view_usuario", "change_usuario"],
            "Catalogadores": [
                "view_pelicula", "add_pelicula", "change_pelicula",
                "view_actor", "add_actor", "change_actor",
                "view_director", "add_director", "change_director",
                "view_genero", "add_genero", "change_genero"
            ]
        }

        # Recorro los grupos y sus permisos.
        for nombre, codigos in roles.items():
            # Busco el grupo o lo creo si no existe.
            grupo, _ = Group.objects.get_or_create(name=nombre)

            # Busco los permisos y se los asigno al grupo.
            permisos = Permission.objects.filter(codename__in=codigos)
            grupo.permissions.set(permisos)

            # Muestro cuántos permisos tiene el grupo.
            self.stdout.write(f"{nombre}: {permisos.count()} permisos")
