from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator #controla extensiones de archivos
from django.db import models #me da las herramientas para crear los modelos
#me ayuda a construir condiciones
from django.db.models import Q

# Modelo para guardar los actores
class Actor(models.Model): 
    nombre = models.CharField(max_length=100) 
    apellido = models.CharField(max_length=100)
    edad = models.PositiveIntegerField(null=True, blank=True) #Prueba de campo opcional.

    class Meta: 
        constraints = [
            models.UniqueConstraint( 
            fields=["nombre", "apellido"], 
            name="actor_unico" 
            ) 
        ]

    def __str__(self): 
        return f"{self.nombre} {self.apellido}"

    #*args = Otros parámetros que pueden venir
    #**kwargs= Otros parámetros con nombre que pueden venir
    def delete(self, *args, **kwargs):
        # Revisamos las películas donde aparece el actor
        for pelicula in self.peliculas.all():

            #Si esta película tiene un solo actor
            if pelicula.actores.count() == 1:

                # No dejamos eliminar al actor
                raise ValidationError(
                    f"No se puede eliminar a {self} porque es el único actor de "
                    f"{pelicula.titulo}"
                )

        # Si no es el único actor en ninguna película, se puede borrar
        super().delete(*args, **kwargs)

# Modelo para guardar los directores
class Director(models.Model): 
    nombre = models.CharField(max_length=100) 
    apellido = models.CharField(max_length=100) 
    class Meta: 
        constraints = [ 
            models.UniqueConstraint( 
            fields=["nombre", "apellido"], 
            name="director_unico" 
            ) 
        ] 

    def __str__(self): 
        return f"{self.nombre} {self.apellido}"

    def delete(self, *args, **kwargs):
        # Revisamos las películas donde aparece el director
        for pelicula in self.peliculas.all():

            #Si esta película tiene un solo director
            if pelicula.directores.count() == 1:

                # No dejamos eliminar al director
                raise ValidationError(
                    f"No se puede eliminar a {self} porque es el único director de "
                    f"{pelicula.titulo}"
                )

        # Si no es el único director en ninguna película, se puede borrar
        super().delete(*args, **kwargs)


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

    titulo = models.CharField(max_length=150) 
    sinopsis = models.TextField() #django establece de manera predeterminado los valores por defecto null=false y blank=false no requiere, se puede o no colocar
    duracion_minutos = models.PositiveIntegerField()
    fecha_estreno = models.DateField() #guarda solo fechas (sin hora)
    url_trailer = models.URLField(blank=True)
    clasificacion = models.CharField(
        max_length=5,
        choices=Clasificacion.choices,
           )
    fecha_registro = models.DateTimeField(auto_now_add=True) #colca y guarda automaticamente la fecha y la hora actual
   
    imagen_portada = models.ImageField(  
        upload_to="peliculas/posters/",  #upload_to le dice a Django en qué carpeta, dentro de MEDIA_ROOT, guardar los archivos subidos.
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
        )                           #validators es una lista de funciones/clases que Django ejecuta antes de aceptar el valor 
                                    #— acá usamos una ya hecha por el framework en vez de escribir la nuestra, 
                                    #porque el caso ("solo estos 4 formatos") es común y ya está resuelto.

    calificacion = models.DecimalField(max_digits=3, decimal_places=1)
    #max_digits=3 es el total de dígitos que se guardan (contando antes y después de la coma), y decimal_places=1 cuántos van después de la coma. Con estos valores, el rango representable va de 0.0 a 99.9

    # Una película puede tener varios actores 
    actores = models.ManyToManyField(Actor, related_name="peliculas" ) 
    # Una película puede tener varios directores 
    directores = models.ManyToManyField(Director, related_name="peliculas" )

    #empezamos a configurar el comportamiento y las reglas
    class Meta:
        #le dice a Django "cuando alguien pida Pelicula.objects.all() 
        # sin especificar un orden, devolveme los resultados ordenados así por defecto". 
        # El - adelante de fecha_estreno significa orden descendente (más nuevas primero); 
        # titulo funciona como criterio de desempate cuando dos películas comparten fecha.
        ordering = ["-fecha_estreno", "titulo"]

        constraints = [  #Lista de reglas que Django traduce en restricciones reales de la base de datos
            models.UniqueConstraint( #combinacion unica de titulo y fecha de estreno
                fields=["titulo", "fecha_estreno"],
                name="pelicula_unica_por_titulo_y_fecha", #Se coloca un name unico, para que la base de datos pueda identificar que regla se violo si falla
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
                condition=Q(calificacion__gte=0.1) & Q(calificacion__lte=10),
                name="pelicula_calificacion_en_rango",
            ),
        ]

    def __str__(self):   #le dice a python como convertir un objeto pelicula en texto legible
        
           return f"{self.titulo} ({self.fecha_estreno.year})"


class Resena(models.Model):
    id_resena = models.AutoField(primary_key=True,)
    pelicula_id = models.ForeignKey(Pelicula,on_delete=models.CASCADE,related_name="resenas",null=False, blank=False,)
    nombre_usuario= models.CharField(max_length=100, null=False, blank=False,)
    texto = models.TextField(null=False,blank=False,)
    calificacion = models.DecimalField(max_digits=3, decimal_places=1,null=False,blank=False,)
    class Meta: #restricciones
        constraints = [
            models.UniqueConstraint(
                fields=["pelicula_id", "nombre_usuario"], name="unica_reseña_por_usuario_y_pelicula",
                ),
            models.CheckConstraint(
                condition=Q(calificacion__gte=0.1) & Q(calificacion__lte=10.0), name = "resena_calificacion_en_rango",
            ),
        ]
    #validacion de palabras del texto para contar la cantidad de palabras
    def clean(self):
        cantidad_palabras = len(self.texto.split()) #divide el texto en una lista de palabras, separando por espacios en blanco. y cuenta cuantos elementos(palabras) hay en total
        if cantidad_palabras < 2 or cantidad_palabras > 15000:
            raise ValidationError(
                {"texto": "El texto de la reseña debe tener entre 2 y 15.000 palabras."} #le indica con un mensaje el error y "texto" le indica a que campo especifico asociar el error, esto ayuda a que en el formulario le aparesca abajo del campo texto el mensaje de error
            )

    def __str__(self):
        return f"Reseña de {self.nombre_usuario} para {self.pelicula_id.titulo}"