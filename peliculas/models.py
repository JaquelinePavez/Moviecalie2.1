import django.core.validators
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.deletion import ProtectedError


class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=100)
    anio_de_nacimiento = models.DateField()

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Actor(Persona):
    class Meta:
        verbose_name = "Actor"
        verbose_name_plural = "Actores"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "nombre",
                    "apellido",
                    "nacionalidad",
                    "anio_de_nacimiento",
                ],
                name="actor_unico"
            )
        ]


    def delete(self, *args, **kwargs):
        """Sobrescribo el método delete para que no se pueda borrar un actor"""
        for pelicula in self.peliculas.all():
            # si esta pelicula tiene un solo actor, no lo dejo borrar
            if pelicula.actores.count() == 1:
                msg = (
                    f"No se puede eliminar a {self} porque es el único "
                    f"{self._meta.verbose_name.lower()} de {pelicula.titulo}"
                )
                # lanzo ProtectedError, igual que haría on_delete=PROTECT
                raise ProtectedError(msg, {pelicula})
        # si no es el unico en ninguna, lo borro
        return super().delete(*args, **kwargs)


class Director(Persona):
    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directores"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "nombre",
                    "apellido",
                    "nacionalidad",
                    "anio_de_nacimiento"
                ],

                name="director_unico"
            )
        ]


    def delete(self, *args, **kwargs):
        # reviso las peliculas donde aparece el director
        for pelicula in self.peliculas.all():
            # si esta pelicula tiene un solo director, no lo dejo borrar
            if pelicula.directores.count() == 1:
                msg = (
                    f"No se puede eliminar a {self} porque es el único "
                    f"{self._meta.verbose_name.lower()} de {pelicula.titulo}"
                )
                # lanzo ProtectedError, igual que haría on_delete=PROTECT
                raise ProtectedError(msg, {pelicula})
        return super().delete(*args, **kwargs)


class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    class Clasificacion(models.TextChoices):
        ATP = "ATP", "Apta para todo público"
        MAS_13 = "M13", "Apta para mayores de 13 años"
        MAS_16 = "M16", "Apta para mayores de 16 años"
        MAS_18 = "M18", "Apta para mayores de 18 años"

    titulo = models.CharField(max_length=150, null=False, blank=False)
    sinopsis = models.TextField(null=False, blank=False)
    duracion_minutos = models.PositiveIntegerField(null=False, blank=False)
    fecha_estreno = models.DateField(null=False, blank=False)
    url_trailer = models.URLField(blank=True)

    clasificacion = models.CharField(
        max_length=5,
        choices=Clasificacion.choices,
        default=Clasificacion.ATP,
           )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    imagen_portada = models.ImageField(
        upload_to="peliculas/posters/",
        validators=[
            django.core.validators.FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"]
            )
        ],
        )

    calificacion_promedio = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )

    # Una película puede tener varios actores
    actores = models.ManyToManyField(
        Actor,
        related_name="peliculas",
        blank=False)

    # Una película puede tener varios directores
    directores = models.ManyToManyField(
        Director,
        related_name="peliculas",
        blank=False )

    # Una película puede tener varios géneros.
    generos = models.ManyToManyField(
        Genero,
        related_name="peliculas",
        blank=True
    )

    class Meta:
        verbose_name = "Película"
        verbose_name_plural = "Películas"
        ordering = ["-fecha_estreno", "titulo"]

        # ÍNDICES EXPLÍCITOS PARA BÚSQUEDAS Y FILTROS FRECUENTES
        indexes = [
            models.Index(
                fields=['-fecha_estreno'],
                name='idx_pelicula_fecha_estreno',
            ),
            models.Index(
                fields=['-calificacion_promedio'],
                name='idx_pelicula_calif_desc',
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["titulo", "fecha_estreno"],
                name="pelicula_unica_por_titulo_y_fecha",
            ),

            #condiciones que debe cumplir los datos
            models.CheckConstraint(
                condition=~Q(titulo=""),
                name="pelicula_titulo_no_vacio",
            ),
            models.CheckConstraint(
                condition=~Q(sinopsis=""),
                name="pelicula_sinopsis_no_vacia",
            ),
            models.CheckConstraint(
                condition=Q(duracion_minutos__gt=0),
                name="pelicula_duracion_positiva",
            ),
            models.CheckConstraint(
                condition=Q(fecha_estreno__gte="1888-01-01"),
                name="pelicula_fecha_estreno_valida",
            ),
            models.CheckConstraint(
                condition=(
                    Q(calificacion_promedio__gte=0)
                    & Q(calificacion_promedio__lte=10)
                ),
                name="pelicula_calificacion_en_rango",
            ),
        ]

    def __str__(self):
        return f"{self.titulo} ({self.fecha_estreno.year})"

    @property
    def trailer_embed_url(self):
        """Devuelve la URL embed del tráiler para usarla en un iframe."""
        if not self.url_trailer:
            return None
        url = self.url_trailer.strip()

        # Si ya es embed, devolverla tal cual limpia
        if "youtube.com/embed/" in url:
            return url.split("?")[0]

        video_id = None
        if "youtu.be/" in url:
            video_id = (
                url.split("youtu.be/")[-1]
                .split("?")[0]
                .split("&")[0]
                .split("/")[0]
            )
        elif "watch?v=" in url:
            video_id = url.split("watch?v=")[-1].split("&")[0].split("?")[0]

        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None


class Resena(models.Model):
    id_resena = models.AutoField(primary_key=True,)
    pelicula: models.ForeignKey = models.ForeignKey(
        Pelicula,
        on_delete=models.CASCADE,
        related_name="resenas",
        null=False,
        blank=False,
    )
    texto = models.TextField(null=False,blank=False,)
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )

    # Un usuario puede tener muchas reseñas.
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resenas")

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        constraints = [
            models.UniqueConstraint(
                fields=["pelicula", "autor"],
                name="unica_resena_por_usuario_y_pelicula",
                ),
            models.CheckConstraint(
                condition=Q(calificacion__gte=0) & Q(calificacion__lte=10.0),
                name = "resena_calificacion_en_rango",
            ),
        ]

    def clean(self):
        """Comprueba que el texto de la reseña tenga entre 2 y 500 palabras."""
        cantidad_palabras = len(self.texto.split())
        if cantidad_palabras < 2 or cantidad_palabras > 500:
            raise ValidationError(
                {
                    "texto": (
                        "El texto de la reseña debe tener entre 2 y 500 "
                        "palabras."
                    )
                }
            )

    def __str__(self):
        return f"Reseña de {self.autor.username} para {self.pelicula.titulo}"
