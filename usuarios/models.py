from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.db import models


class Usuario(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False) #valida que no se duplique el email

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username


class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )

    foto_de_perfil = models.ImageField(
        upload_to="perfiles/fotos/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
        blank=True, #permite que quede quede vacio en el formulario
        null=True, # permite que si queda vacio se guarde el valor null y no un string que es dificil de representar en este caso
    )

    biografia = models.TextField(null=False, blank=True) #permite que se guarde vacio desde el formulario pero no que guarde el valor nul, en este caso queda vacio con strings ""

    generos_favoritos = models.ManyToManyField( #relacion muchos a muchos (N:M)
        "peliculas.Genero",
        blank=True,
        related_name="usuarios_favoritos", #se accede desde genero: genero.usuarios_favoritos 
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
        cantidad_palabras = len(self.biografia.split())
        if cantidad_palabras > 500:
            raise ValidationError(
                {"biografia": "La biografía no puede superar las 500 palabras."}
            )

    def __str__(self):
        return f"Perfil de {self.usuario.username}"