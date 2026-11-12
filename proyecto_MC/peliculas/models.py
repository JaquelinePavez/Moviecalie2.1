from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q


class Actor(models.Model):
    """Modelo para guardar los actores."""

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=100)
    anio_de_nacimiento = models.DateField()

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
                name="actor_unico",
            )
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def delete(self, *args, **kwargs):
        """No permite borrar al actor si es el único de alguna película."""
        # Se revisan las películas donde aparece el actor
        for pelicula in self.peliculas.all():
            if pelicula.actores.count() == 1:
                raise ValidationError(
                    f"No se puede eliminar a {self} porque es el único "
                    f"actor de {pelicula.titulo}"
                )
        # Si no es el único en ninguna, se borra
        return super().delete(*args, **kwargs)


class Director(models.Model):
    """Modelo para guardar los directores."""

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=100)
    anio_de_nacimiento = models.DateField()

    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directores"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "nombre",
                    "apellido",
                    "nacionalidad",
                    "anio_de_nacimiento",
                ],
                name="director_unico",
            )
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def delete(self, *args, **kwargs):
        """No permite borrar al director si es el único de alguna película."""
        # Se revisan las películas donde aparece el director
        for pelicula in self.peliculas.all():
            if pelicula.directores.count() == 1:
                raise ValidationError(
                    f"No se puede eliminar a {self} porque es el único "
                    f"director de {pelicula.titulo}"
                )
        # Si no es el único en ninguna, se borra
        return super().delete(*args, **kwargs)


class Genero(models.Model):
    """
    Modelo para guardar los géneros.

    Un género puede estar asociado a varias películas y una película puede
    tener varios géneros (relación Muchos a Muchos).
    """

    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    """
    Modelo para guardar las películas.

    Al heredar de models.Model, Django trata esta clase como una tabla de
    la base de datos y genera el SQL (CREATE TABLE ...) al correr las
    migraciones. No se declara un campo identificador: Django agrega "id"
    automáticamente.
    """

    class Clasificacion(models.TextChoices):
        """
        Clasificación por edades.

        Cada opción tiene dos partes: el valor que se guarda en la base de
        datos (ej. "ATP") y el texto legible que se muestra en los
        formularios (ej. "Apta para todo público").
        """

        ATP = "ATP", "Apta para todo público"
        MAS_13 = "M13", "Apta para mayores de 13 años"
        MAS_16 = "M16", "Apta para mayores de 16 años"
        MAS_18 = "M18", "Apta para mayores de 18 años"

    titulo = models.CharField(max_length=150, null=False, blank=False)
    # Django usa null=False y blank=False por defecto; se pueden omitir
    sinopsis = models.TextField(null=False, blank=False)
    duracion_minutos = models.PositiveIntegerField(null=False, blank=False)
    # Guarda solo la fecha (sin hora)
    fecha_estreno = models.DateField(null=False, blank=False)
    url_trailer = models.URLField(blank=True)
    clasificacion = models.CharField(
        max_length=5,
        choices=Clasificacion.choices,
        # Si no se indica la clasificación, se considera ATP
        default=Clasificacion.ATP,
    )
    # Guarda automáticamente la fecha y hora actuales al crear el registro
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # ImageField guarda la ruta del archivo. upload_to indica la carpeta,
    # dentro de MEDIA_ROOT, donde se guardan los archivos subidos.
    # validators es una lista de funciones/clases que Django ejecuta antes
    # de aceptar el valor; se usa una del framework porque el caso ("solo
    # estos 4 formatos") es común y ya está resuelto.
    imagen_portada = models.ImageField(
        upload_to="peliculas/posters/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"]
            )
        ],
    )

    # max_digits=3 es el total de dígitos guardados (antes y después de la
    # coma) y decimal_places=1 cuántos van después de la coma. Con estos
    # valores el rango representable es de 0.0 a 99.9.
    # default=0 se usa si no se carga una calificación.
    calificacion_promedio = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
    )

    # Cardinalidad de las relaciones.
    # Una película puede tener varios actores. blank=False obliga a cargar
    # al menos uno desde los formularios. related_name permite acceder a
    # la relación en sentido inverso: actor.peliculas.all()
    actores = models.ManyToManyField(
        Actor,
        related_name="peliculas",
        blank=False,
    )
    # Una película puede tener varios directores
    directores = models.ManyToManyField(
        Director,
        related_name="peliculas",
        blank=False,
    )
    # Una película puede tener varios géneros. blank=True permite que no
    # tenga géneros asignados. Desde un género se accede a sus películas
    # con genero.peliculas.all()
    generos = models.ManyToManyField(
        Genero,
        related_name="peliculas",
        blank=True,
    )

    class Meta:
        verbose_name = "Película"
        verbose_name_plural = "Películas"
        # Orden por defecto de Pelicula.objects.all(). El "-" indica orden
        # descendente (más nuevas primero) y titulo desempata cuando dos
        # películas comparten fecha.
        ordering = ["-fecha_estreno", "titulo"]

        # Índices para búsquedas y filtros frecuentes
        indexes = [
            # Búsquedas por fecha de estreno
            models.Index(
                fields=["-fecha_estreno"],
                name="idx_pelicula_fecha_estreno",
            ),
            # Obtener las mejores valoradas
            models.Index(
                fields=["-calificacion_promedio"],
                name="idx_pelicula_calif_desc",
            ),
        ]

        # Reglas que Django traduce en restricciones de la base de datos
        constraints = [
            # Impide dos filas con la misma combinación de campos. El name
            # único permite identificar qué regla se violó si falla.
            models.UniqueConstraint(
                fields=["titulo", "fecha_estreno"],
                name="pelicula_unica_por_titulo_y_fecha",
            ),
            # CheckConstraint valida una condición sobre los valores de
            # cada fila, a nivel de base de datos.
            models.CheckConstraint(
                condition=~Q(titulo=""),
                name="pelicula_titulo_no_vacio",
            ),
            models.CheckConstraint(
                condition=~Q(sinopsis=""),
                name="pelicula_sinopsis_no_vacia",
            ),
            # gt = mayor que
            models.CheckConstraint(
                condition=Q(duracion_minutos__gt=0),
                name="pelicula_duracion_positiva",
            ),
            # gte = mayor o igual
            models.CheckConstraint(
                condition=Q(fecha_estreno__gte="1888-01-01"),
                name="pelicula_fecha_estreno_valida",
            ),
            # Garantiza que ningún error de la aplicación, carga directa
            # en el Admin o script de migración pueda almacenar un valor
            # fuera del rango de 0.0 a 10.0.
            models.CheckConstraint(
                condition=(
                    Q(calificacion_promedio__gte=0)
                    & Q(calificacion_promedio__lte=10)
                ),
                name="pelicula_calificacion_en_rango",
            ),
        ]

    def __str__(self):
        """Convierte la película en texto legible: "Título (año)"."""
        return f"{self.titulo} ({self.fecha_estreno.year})"

    @property
    def trailer_embed_url(self):
        """
        Devuelve la URL del trailer en formato embebido (para un iframe).

        Devuelve None si no hay URL o si no se reconoce el formato.
        """
        if not self.url_trailer:
            return None
        url = self.url_trailer.strip()

        # Si ya es embed, se devuelve limpia (sin parámetros)
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
    """Modelo para guardar las reseñas de las películas."""

    id_resena = models.AutoField(primary_key=True)
    # on_delete=CASCADE: al borrar la película se borran sus reseñas
    pelicula = models.ForeignKey(
        Pelicula,
        on_delete=models.CASCADE,
        related_name="resenas",
        null=False,
        blank=False,
    )
    texto = models.TextField(null=False, blank=False)
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=False,
        blank=False,
    )
    # Relaciona la reseña con el usuario que la creó (referencia a la app
    # usuarios). Un usuario puede tener muchas reseñas.
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resenas",
    )

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        constraints = [
            models.UniqueConstraint(
                fields=["pelicula", "autor"],
                name="unica_reseña_por_usuario_y_pelicula",
            ),
            models.CheckConstraint(
                condition=(
                    Q(calificacion__gte=0.1) & Q(calificacion__lte=10.0)
                ),
                name="resena_calificacion_en_rango",
            ),
        ]

    def __str__(self):
        return f"Reseña de {self.autor.username} para {self.pelicula.titulo}"

    def clean(self):
        """
        Valida que el texto tenga entre 2 y 500 palabras.

        El error se asocia al campo "texto" para que el formulario muestre
        el mensaje debajo de ese campo.
        """
        # split() separa el texto por espacios en blanco y len() cuenta
        # cuántas palabras hay en total
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
