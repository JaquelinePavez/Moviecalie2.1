from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario que hereda los campos y funcionalidades
    que Django ya tiene para manejar usuarios.
    """
    email = models.EmailField(unique=True, null=False, blank=False)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        """
        Devuelve el nombre de usuario para identificarlo
        cuando se muestra en el administrador de Django.
        """
        return self.username


class Perfil(models.Model):
    """
    Modelo que guarda información adicional de cada usuario,
    como su foto, biografía y sus preferencias.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )

    foto_de_perfil = models.ImageField(
        upload_to="perfiles/fotos/",
        validators=[FileExtensionValidator
                    (allowed_extensions=["jpg", "jpeg", "png", "webp"])],
                    blank=True,
                    null=True,
    )

    biografia = models.TextField(null=False, blank=True)

    generos_favoritos = models.ManyToManyField( #relacion muchos a muchos (N:M)
        "peliculas.Genero",
        blank=True,
        related_name="usuarios_favoritos",
    )

    resenas_favoritas = models.ManyToManyField( #
        "peliculas.Resena",
        blank=True,
        related_name="usuarios_favoritos",
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"


    def clean(self):
        """
        Comprueba que la biografía no supere las 500 palabras.
        Si supera ese límite, muestra un error de validación.
        """
        cantidad_palabras = len(self.biografia.split())
        if cantidad_palabras > 500:
            raise ValidationError(
            {"biografia": "La biografía no puede superar las 500 palabras."}
            )


    def __str__(self):
        """
        Devuelve el nombre del usuario al que pertenece el perfil.
        """
        return f"Perfil de {self.usuario.username}"
