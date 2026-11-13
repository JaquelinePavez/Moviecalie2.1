import django.contrib.auth.models
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Comando que permite crear los grupos de usuarios
    y asignarles los permisos correspondientes.
    """

    help = "Crea los grupos y les asigna permisos"


    def handle(self, *args, **opciones):
        """
        Define los grupos, busca los permisos correspondientes
        y se los asigna a cada uno. También muestra en la consola
        la cantidad de permisos que tiene cada grupo.
        """
        # Defino los grupos con sus respectivos permisos.
        roles = {
            "Criticos": [
                "view_resena",
                "add_resena",
                "change_resena",
                "delete_resena",
            ],
            "Moderadores": [
                "view_resena",
                "delete_resena",
                "view_usuario",
                "change_usuario",
            ],
            "Catalogadores": [
                "view_pelicula",
                "add_pelicula",
                "change_pelicula",
                "view_actor",
                "add_actor",
                "change_actor",
                "view_director",
                "add_director",
                "change_director",
                "view_genero",
                "add_genero",
                "change_genero"
            ]
        }

        for nombre, codigos in roles.items():

            grupo, _ = (
                django.contrib.auth.models.Group.objects.get_or_create(
                    name=nombre
                )
            )

            permisos = (
                django.contrib.auth.models.Permission.objects.filter(
                    codename__in=codigos
                )
            )
            grupo.permissions.set(permisos)

            self.stdout.write(f"{nombre}: {permisos.count()} permisos")
