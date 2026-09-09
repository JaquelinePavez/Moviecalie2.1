from django.core.validators import FileExtensionValidator #clase de Django para validar un archivo subido tenga 
                                                        #la extension permitida como en imagen_portada
from django.db import models #da acceso a model de la clase base
from django.db.models import Q #se usa para contruir las condiciones de los checkconstraint


class Pelicula(models.Model): #Al heredar de models.Model, le estás diciendo a Django 
                                #"esta clase de Python representa una tabla de base de datos". 
                                #Django, por detrás, va a generar el SQL necesario (CREATE TABLE pelicula (...)) 
                                #la primera vez que corras las migraciones.
                                #no se declara ningun campo de identificado: Django lo agrega automaticamente

                                
    class Clasificacion(models.TextChoices):#tiene dos partes ATP es el valor que se guarda en la bse de datos y 
                                            #Apta para todo publico es el texto legible que se 
                                            #muestra en formularios y en el admin djnago
        ATP = "ATP", "Apta para todo público"
        MAS_13 = "M13", "Apta para mayores de 13 años"
        MAS_16 = "M16", "Apta para mayores de 16 años"
        MAS_18 = "M18", "Apta para mayores de 18 años"

#los campos se definieron con un tipo de dato ya explicado en los puntos anteriores con las especificaciones necesarias

    titulo = models.CharField(max_length=150) 
    sinopsis = models.TextField() #django establece de manera predeterminado los valores por defecto null=false y blank=false no requiere, se puede o no colocar
    duracion_minutos = models.PositiveIntegerField()
    fecha_estreno = models.DateField() #guarda solo fechas (sin hora)
    url_trailer = models.URLField(blank=True)
    clasificacion = models.CharField(
        max_length=5,
        choices=Clasificacion.choices,
           )
    fecha_registro = models.DateTimeField(auto_now_add=True)
   
    imagen_portada = models.ImageField(  
        upload_to="peliculas/posters/",  #upload_to le dice a Django en qué carpeta, dentro de MEDIA_ROOT, guardar los archivos subidos.
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
    )  #validators es una lista de funciones/clases que Django ejecuta antes de aceptar el valor — acá usamos una ya hecha por el framework en vez de escribir la nuestra, porque el caso ("solo estos 4 formatos") es común y ya está resuelto.

    calificacion = models.DecimalField(max_digits=3, decimal_places=1)
#max_digits=3 es el total de dígitos que se guardan (contando antes y después de la coma), y decimal_places=1 cuántos van después de la coma. Con estos valores, el rango representable va de 0.0 a 99.9


    class Meta:   #le dice a Django "cuando alguien pida Pelicula.objects.all() sin especificar un orden, devolveme los resultados ordenados así por defecto". El - adelante de fecha_estreno significa orden descendente (más nuevas primero); titulo funciona como criterio de desempate cuando dos películas comparten fecha.
        ordering = ["-fecha_estreno", "titulo"]

        constraints = [  #Lista de reglas que Django traduce en restricciones reales de la base de datos
            models.UniqueConstraint(
                fields=["titulo", "fecha_estreno"],
                name="pelicula_unica_por_titulo_y_fecha", #Se coloca un name unico, para que la base de datos pueda identificar que regla se violo si falla
            ),
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
