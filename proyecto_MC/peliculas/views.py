from .models import Pelicula, Genero, Actor, Director, Resena #importa desde el modulo models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q, Avg  # agregamos Avg
from django.db.models.deletion import ProtectedError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db import transaction
from .forms import ResenaForm
from .models import Pelicula, Resena
from django.views.decorators.http import require_http_methods

def catalogo_peliculas(request):
    # Optimiza consultas separadas cargando las relaciones en una sola query
    queryset = Pelicula.objects.prefetch_related('generos', 'actores', 'directores').all()

    # Parámetros GET : Request.GET (es un diccionario de parametros que recibe desde la URL)
    query_busqueda = request.GET.get('q', '').strip() #.get busca la clave 'q' .strip borra espacios en blanco
    genero_id = request.GET.get('genero')
    clasificacion_seleccionada = request.GET.get('clasificacion')
    actor_id = request.GET.get('actor')
    director_id = request.GET.get('director')
    anio_desde = request.GET.get('anio_desde')
    anio_hasta = request.GET.get('anio_hasta')
    min_calificacion = request.GET.get('min_calificacion')
    orden = request.GET.get('orden', '-fecha_estreno')  # Orden por defecto

    # 1. Búsqueda de texto: si el usuario escribio algo busca el texto 
    if query_busqueda:
        queryset = queryset.filter(titulo__icontains=query_busqueda)

    # 2. Filtro exacto por género
    if genero_id and genero_id.isdigit(): #verifica que sea un numero
        queryset = queryset.filter(generos__id=genero_id) #el doble__ se utiliza para atravesar las relaciones
        #filtra pelicula entre todos sus generos relacionados, exista uno con ese id

    # 3. Filtro exacto por clasificación
    if clasificacion_seleccionada:
        queryset = queryset.filter(clasificacion=clasificacion_seleccionada)

    # 4. Filtro exacto por actor
    if actor_id and actor_id.isdigit():
        queryset = queryset.filter(actores__id=actor_id)

    # 5. Filtro exacto por director
    if director_id and director_id.isdigit():
        queryset = queryset.filter(directores__id=director_id)

    # 6. Rango de años, convertido a fechas límite para aprovechar el índice de fecha_estreno
    if anio_desde and anio_desde.isdigit():
        queryset = queryset.filter(fecha_estreno__gte=f"{anio_desde}-01-01")
    if anio_hasta and anio_hasta.isdigit():
        queryset = queryset.filter(fecha_estreno__lte=f"{anio_hasta}-12-31")

    # 7. Calificación mínima
    if min_calificacion and min_calificacion.replace('.', '', 1).isdigit():
        queryset = queryset.filter(calificacion_promedio__gte=float(min_calificacion))

    # 8. Ordenamiento dinámico
    opciones_orden = { #diccionario que traduce la url con el nombre del campo que django necesita usar
        'calificacion_desc': '-calificacion_promedio',
        'calificacion_asc': 'calificacion_promedio',
        'fecha_desc': '-fecha_estreno',
        'fecha_asc': 'fecha_estreno',
        'titulo_asc': 'titulo',
    }
    criterio_orden = opciones_orden.get(orden, '-fecha_estreno') #devuelve un valor por defecto si no encuentra ninguna de las claves ya conocidas
    queryset = queryset.distinct().order_by(criterio_orden)#elimina repeticiones antes de ordenar

    context = {
        'peliculas': queryset,
        'generos': Genero.objects.all(),
        'clasificaciones': Pelicula.Clasificacion.choices,
        'actores': Actor.objects.all(),
        'directores': Director.objects.all(),
        'query_busqueda': query_busqueda,
        'genero_seleccionado': int(genero_id) if genero_id and genero_id.isdigit() else None,
        'clasificacion_seleccionada': clasificacion_seleccionada or '',
        'actor_seleccionado': int(actor_id) if actor_id and actor_id.isdigit() else None,
        'director_seleccionado': int(director_id) if director_id and director_id.isdigit() else None,
        'anio_desde': anio_desde or '',
        'anio_hasta': anio_hasta or '',
        'min_calificacion': min_calificacion or '',
        'orden_seleccionado': orden,
    }
    return render(request, 'peliculas/catalogo.html', context)


def detalle_resenas_pelicula(request, id):
    pelicula = get_object_or_404(Pelicula, id=id)  # si un id de una pelicula no se encuentra, devuelve 404
    promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"]  # calcula un valor resumen del promedio de todas las resenas de una pelicula

    if request.method == "GET":  # permite que un usuario no autenticado pueda visualizar las resenas
        form = ResenaForm()  # dibuja el formulario vacio
        contexto = {
            "pelicula": pelicula,
            "titulo_pagina": "Agregar reseña",
            "resenas": pelicula.resenas.order_by("-id_resena"),
            "promedio_resenas": promedio_resenas,
            "form": form,
        }

        return render(request, "peliculas/resenas_usuarios.html", contexto)

    if request.method == "POST":  # para publicar requiere sesion
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        form = ResenaForm(request.POST)  # envia la peticion para validar los datos

        if form.is_valid():  # si es valido devuelve True, sino devuelve False
            nueva_resena = form.save(commit=False)  # obtiene los datos validados pero no los guarda aun
            calificacion = form.cleaned_data["calificacion"]  # limpia los datos y los guarda con su tipo correspondiente
            texto = form.cleaned_data["texto"]

            nueva_resena = Resena(  # crea el objeto con los datos ya validados
                pelicula=pelicula,
                autor=request.user,  # Django llena automáticamente con el usuario real que está logueado en esa sesión
                calificacion=calificacion,
                texto=texto,
            )

            try:  # dispara las validaciones para el conteo de palabras definido en models con clean()
                nueva_resena.full_clean()
            except ValidationError as errores:  # si algo falla
                form.add_error(None, errores.messages)  # agrega los errores al formulario
            else:
                nueva_resena.save()  # lo guarda en la BBDD
                messages.success(request, "Tu reseña se publicó correctamente.")
                return redirect("peliculas:resenas_pelicula", id=pelicula.id)

        contexto = {
            "pelicula": pelicula,
            "resenas": pelicula.resenas.order_by("-id_resena"),
            "promedio_resenas": promedio_resenas,
            "form": form,
            "titulo_pagina": "Agregar reseña",
        }

        return render(request, "peliculas/resenas_usuarios.html", contexto)

@login_required # El usuario debe estar autenticado sí o sí 
@require_http_methods(["GET", "POST"])
def editar_resenas(request, pk):
    #obtenemos la reseña asegurando que pertenezca al usuario logueado
    resena = get_object_or_404(Resena, pk=pk, autor=request.user)
    
    if request.method == "POST":
        form = ResenaForm(request.POST, instance=resena)
        if form.is_valid():
            with transaction.atomic():
                resena = form.save()
            messages.success(request, "La reseña se actualizó correctamente.")
            
            return redirect("peliculas:resenas_pelicula", id=resena.pelicula.pk)
    else:
        form = ResenaForm(instance=resena)
    
    contexto = {
        "form": form,
        "titulo_pagina": "Editar reseña",
        "resena": resena,
        "pelicula": resena.pelicula, 
    }
    
    return render(request, "peliculas/resenas_usuarios.html", contexto)



# Mixin: pide sesión y limita el conjunto a las reseñas del usuario
class ResenasPropiasMixin(LoginRequiredMixin):
    model = Resena

    def get_queryset(self):
        return super().get_queryset().filter(autor=self.request.user)



class ResenaEliminar(ResenasPropiasMixin, DeleteView):
    http_method_names = ["get", "post", "head", "options"]
    template_name = "peliculas/confirmar_eliminacion.html"
    context_object_name = "resena"
    #success_url = reverse_lazy("peliculas:resenas_pelicula")
    
    def get_success_url(self):
         # Después de eliminar la reseña, vuelve a la página de reseñas de la película
        return reverse_lazy("peliculas:resenas_pelicula", kwargs={"id": self.object.pelicula_id})

    def form_valid(self, form):
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Hay datos relacionados que impiden eliminarla.")
            return redirect("peliculas:detalle_resena", pk=self.object.pk)
        messages.success(self.request, "La reseña se eliminó.")
        return respuesta 