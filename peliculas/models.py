from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator #controla extensiones de archivos
from django.db import models #me da las herramientas para crear los modelos
from django.conf import settings #para reseñas.autor
#from django.contrib.auth.models import User
#me ayuda a construir condiciones
from django.db.models import Q


#-------------------------------------------------------#
#           Modelo para guardar los actores             #
#-------------------------------------------------------#
class Actor(models.Model): 
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
                    "anio_de_nacimiento"
                ],
                name="actor_unico"
            )
        ]

    def __str__(self): 
        return f"{self.nombre} {self.apellido}"

    def delete(self, *args, **kwargs):
        # reviso las peliculas donde aparece el actor
        for pelicula in self.peliculas.all():
            # si esta pelicula tiene un solo actor, no lo dejo borrar
            if pelicula.actores.count() == 1:
                raise ValidationError(
                    f"No se puede eliminar a {self} porque es el único actor de "
                    f"{pelicula.titulo}"
                )
        # si no es el unico en ninguna, lo borro
        return super().delete(*args, **kwargs)


#-------------------------------------------------------#
#           Modelo para guardar los directores          #
#-------------------------------------------------------#

class Director(models.Model): 
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
                    "anio_de_nacimiento"
                ],

                name="director_unico"
            )
        ] 

    def __str__(self): 
        return f"{self.nombre} {self.apellido}"


    def delete(self, *args, **kwargs):
        # reviso las peliculas donde aparece el director
        for pelicula in self.peliculas.all():
            # si esta pelicula tiene un solo director, no lo dejo borrar
            if pelicula.directores.count() == 1:
                raise ValidationError(
                    f"No se puede eliminar a {self} porque es el único director de "
                    f"{pelicula.titulo}"
                )
        # si no es el unico en ninguna, lo borro
        return super().delete(*args, **kwargs)


#-------------------------------------------------------#
#           Modelo para guardar los generos             #
#-------------------------------------------------------#

# ============================================================
# DEFINICIÓN DE GÉNERO
# Un género puede estar asociado a varias películas y una
# película puede tener varios géneros. (Muchos a Muchos)

class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ============================================================


# ============================================================

#-------------------------------------------------------#
#           Modelo para guardar las peliculas           #
#-------------------------------------------------------#
class Pelicula(models.Model): #Al heredar de models.Model, le estás diciendo a Django 
                                #"esta clase de Python representa una tabla de base de datos". 
                                #Django, por detrás, va a generar el SQL necesario (CREATE TABLE pelicula (...)) 
                                #la primera vez que corras las migraciones.
                                #no se declara ningun campo de identificado: Django lo agrega automaticamente

                                
    class Clasificacion(models.TextChoices):#tiene dos partes ATP es el valor que se guarda en la bse de datos y 
                                            #Apta para todo publico es el texto legible que se 
                                            #muestra en formularios 
        ATP = "ATP", "Apta para todo público"
        MAS_13 = "M13", "Apta para mayores de 13 años"
        MAS_16 = "M16", "Apta para mayores de 16 años"
        MAS_18 = "M18", "Apta para mayores de 18 años"

    titulo = models.CharField(max_length=150, null=False, blank=False) 
    sinopsis = models.TextField(null=False, blank=False) #django establece de manera predeterminado los valores por defecto null=false y blank=false no requiere, se puede o no colocar
    duracion_minutos = models.PositiveIntegerField(null=False, blank=False)
    fecha_estreno = models.DateField(null=False, blank=False) #guarda solo fechas (sin hora)
    url_trailer = models.URLField(blank=True)

    #Esta parte es un método que devuelve la URL del trailer en formato embebido, para poder mostrarlo en un iframe.
    @property
    def trailer_embed_url(self):
        if not self.url_trailer:
            return None
        url = self.url_trailer.strip()

        # Si ya es embed, devolverla tal cual limpia
        if "youtube.com/embed/" in url:
            return url.split("?")[0]

        video_id = None
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0].split("&")[0].split("/")[0]
        elif "watch?v=" in url:
            video_id = url.split("watch?v=")[-1].split("&")[0].split("?")[0]

        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None
        #=============================================================

    clasificacion = models.CharField(
        max_length=5,
        choices=Clasificacion.choices,
        default=Clasificacion.ATP, #Si no me dicen la clasificación, voy a considerar ATP
           )
    fecha_registro = models.DateTimeField(auto_now_add=True) #colca y guarda automaticamente la fecha y la hora actual
   
    imagen_portada = models.ImageField(  #imageField guarda la ruta del archivo
        upload_to="peliculas/posters/",  #upload_to le dice a Django en qué carpeta, dentro de MEDIA_ROOT, guardar los archivos subidos.
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
        )                           #validators es una lista de funciones/clases que Django ejecuta antes de aceptar el valor 
                                    #— acá usamos una ya hecha por el framework en vez de escribir la nuestra, 
                                    #porque el caso ("solo estos 4 formatos") es común y ya está resuelto.

    calificacion_promedio = models.DecimalField( #max_digits=3 es el total de dígitos que se guardan (contando antes y después de la coma), y 
        # decimal_places=1 cuántos van después de la coma. Con estos valores, el rango representable va de 0.0 a 99.9
        max_digits=3, 
        decimal_places=1,
        default=0
    ) #Si no cargo una calificación
    #===================================#
    #       CARDINALIDAD                #
    #===================================#
    # RELACIÓN PELÍCULA / ACTORES
    # Una película puede tener varios actores 
    actores = models.ManyToManyField(
        Actor, 
        related_name="peliculas" , # permite acceder a la relación en sentido inverso
        blank=False) #obliga al usuario a cargar un actor desde formularios
    # RELACIÓN PELÍCULA / DIRECTORES
    # Una película puede tener varios directores 
    directores = models.ManyToManyField(
        Director, 
        related_name="peliculas",
        blank=False ) # permite acceder a la relación en sentido inverso

    # RELACIÓN PELÍCULA / GÉNERO
    # Una película puede tener varios géneros.
    # related_name="peliculas" permite acceder desde un género
    # a todas las películas asociadas:
    # genero.peliculas.all()
    generos = models.ManyToManyField(
        Genero,
        related_name="peliculas", # permite acceder a la relación en sentido inverso
        blank=True # permite que una película no tenga géneros asignados
    )
    # ============================================================

    #======================================#
    #      REGLAS Y RESTRICCIONES          #
    #======================================#
    class Meta:
        verbose_name = "Película"
        verbose_name_plural = "Películas"
        ordering = ["-fecha_estreno", "titulo"]  #le dice a Django "cuando alguien pida Pelicula.objects.all() 
                                                # sin especificar un orden, devolveme los resultados ordenados así por defecto". 
                                                # El - adelante de fecha_estreno significa orden descendente (más nuevas primero); 
                                                # titulo funciona como criterio de desempate cuando dos películas comparten fecha.

        # -------------------------------------------------------------
        # ÍNDICES EXPLÍCITOS PARA BÚSQUEDAS Y FILTROS FRECUENTES
        # -------------------------------------------------------------
        indexes = [
            models.Index(fields=['-fecha_estreno'], name='idx_pelicula_fecha_estreno'), #indice para busquedas por fecha de estrenos
            models.Index(fields=['-calificacion_promedio'], name='idx_pelicula_calif_desc'),#indice para obtener las mejores valoradas
            
        ]


        constraints = [  #Lista de reglas que Django traduce en restricciones reales de la base de datos
            models.UniqueConstraint( #uniqueconstraint impide que existan dos filas con la misma combinación de esos campos.
                fields=["titulo", "fecha_estreno"],
                name="pelicula_unica_por_titulo_y_fecha", #Se coloca un name unico, para que la base de datos pueda identificar que regla se violo si falla
            ),
            #condiciones que debe cumplir los datos
            models.CheckConstraint( #CheckConstraint` valida una condición sobre los valores de cada fila, a nivel de base de datos
                condition=~Q(titulo=""),
                name="pelicula_titulo_no_vacio",
            ),
            models.CheckConstraint(
                condition=~Q(sinopsis=""),
                name="pelicula_sinopsis_no_vacia",
            ),
            models.CheckConstraint(
                condition=Q(duracion_minutos__gt=0), #gt= mayor que 
                name="pelicula_duracion_positiva",
            ),
            models.CheckConstraint(
                condition=Q(fecha_estreno__gte="1888-01-01"), #gte = mayor o igual
                name="pelicula_fecha_estreno_valida",
            ),
            models.CheckConstraint(
                condition=Q(calificacion_promedio__gte=0) & Q(calificacion_promedio__lte=10),
                name="pelicula_calificacion_en_rango",
                # CheckConstraint garantiza que 
                #ningún error en la lógica de la aplicación, 
                #carga directa en el Admin o script de migración pueda jamás
                #almacenar un valor fuera del rango de 0.1 a 10.0 en esa tabla,
               
            ),
        ]

    def __str__(self):   #le dice a python como convertir un objeto pelicula en texto legible
        
           return f"{self.titulo} ({self.fecha_estreno.year})"

#-------------------------------------------------------#
#           Modelo para guardar reseñas                 #
#-------------------------------------------------------#

class Resena(models.Model):
    id_resena = models.AutoField(primary_key=True,)
    pelicula = models.ForeignKey(Pelicula,on_delete=models.CASCADE,related_name="resenas",null=False, blank=False,) #on_delete: todas sus reseñas se borran en cadena
    texto = models.TextField(null=False,blank=False,)
    calificacion = models.DecimalField(max_digits=3, decimal_places=1,null=False,blank=False,)
    
    #===================================#
    #       CARDINALIDAD                #
    #===================================#
    # Relaciona la reseña con el usuario que la creó.
    # Un usuario puede tener muchas reseñas.
  
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, #referencia hacia la app usuarios
        on_delete=models.CASCADE,
        related_name="resenas") #

    class Meta: #restricciones
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        constraints = [
            models.UniqueConstraint(
                fields=["pelicula", "autor"], 
                name="unica_reseña_por_usuario_y_pelicula",
                ),
            models.CheckConstraint(
                condition=Q(calificacion__gte=0.1) & Q(calificacion__lte=10.0), 
                name = "resena_calificacion_en_rango",
            ),
        ]
    #validacion de palabras del texto para contar la cantidad de palabras
    def clean(self):
        cantidad_palabras = len(self.texto.split()) #divide el texto en una lista de palabras, separando por espacios en blanco. y (len)cuenta cuantos elementos(palabras) hay en total
        if cantidad_palabras < 2 or cantidad_palabras > 500:
            raise ValidationError(
                {"texto": "El texto de la reseña debe tener entre 2 y 500 palabras."} #le indica con un mensaje el error y "texto" le indica a que campo especifico asociar el error, esto ayuda a que en el formulario le aparesca abajo del campo texto el mensaje de error
            )

    def __str__(self):
        return f"Reseña de {self.autor.username} para {self.pelicula.titulo}"

