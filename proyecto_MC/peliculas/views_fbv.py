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

def detalle(request, id):
    pelicula = get_object_or_404(Pelicula, id=id)  # si un id de una pelicula no se encuentra, devuelve 404
    # ANTES: promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"]  # calcula un valor resumen del promedio de todas las resenas de una pelicula
    # LO COMENTO PORQUE SI NO HAY RESEÑAS DEVUELVE None y tiene que mostrar 0
    promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"] or 0

    ya_comento = False
    if request.user.is_authenticated:
        ya_comento = Resena.objects.filter(pelicula=pelicula, autor=request.user).exists()
    if request.method == "GET":  # permite que un usuario no autenticado pueda visualizar las resenas
        form = ResenaForm()  # dibuja el formulario vacio
        contexto = {
            "pelicula": pelicula,
            "titulo_pagina": "Agregar reseña",
            "resenas": pelicula.resenas.order_by("-id_resena"),
            "promedio_resenas": promedio_resenas,
            "form": form,
            "ya_comento": ya_comento
        }

        return render(request, "peliculas/detalle_pelicula.html", contexto)
    else: 
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        else:
            return redirect("peliculas:agregar", id=id)

@login_required
def agregar_resena(request, id):
    pelicula = get_object_or_404(Pelicula, id=id)
    # ANTES: promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"]
    # LO COMENTO PORQUE SI NO HAY RESEÑAS DEVUELVE None y tiene que mostrar 0
    promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"] or 0    
    form = ResenaForm(request.POST)

    #comprueba si el usuario ya escribió una reseña para esta película
    ya_tiene_resena = Resena.objects.filter(pelicula=pelicula, autor=request.user).exists()

    if ya_tiene_resena:
        # Agregamos un error general (non_field_error) al formulario
        form.add_error(None, "Ya has publicado una reseña para esta película.")

    elif form.is_valid():
        nueva_resena = form.save(commit=False)
        nueva_resena.pelicula = pelicula
        nueva_resena.autor = request.user

        try:
            nueva_resena.full_clean()
        except ValidationError as errores:
            form.add_error(None, errores.messages)
        else:
            nueva_resena.save()
            messages.success(request, "Tu reseña se publicó correctamente.")
            return redirect("peliculas:detalle", id=pelicula.id)

    contexto = {
        "pelicula": pelicula,
        "resenas": pelicula.resenas.order_by("-id_resena"),
        "promedio_resenas": promedio_resenas,
        "form": form,
        "titulo_pagina": "Agregar reseña",
        "ya_comento": ya_tiene_resena,
    }

    return render(request, "peliculas/detalle_pelicula.html", contexto)

@login_required # El usuario debe estar autenticado sí o sí 
@require_http_methods(["GET", "POST"])
def editar_resenas(request, pk):
    #obtenemos la reseña asegurando que pertenezca al usuario logueado
    resena = get_object_or_404(Resena, pk=pk, autor=request.user)
    pelicula = resena.pelicula
    # ANTES: promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"]
    # LO COMENTO PORQUE SI NO HAY RESEÑAS DEVUELVE None y tiene que mostrar 0
    promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"] or 0    
    resenas_listado = pelicula.resenas.order_by("-id_resena")
    if request.method == "POST":
        form = ResenaForm(request.POST, instance=resena)
        if form.is_valid():
            with transaction.atomic():
                resena = form.save()
            messages.success(request, "La reseña se actualizó correctamente.")
            
            return redirect("peliculas:detalle", id=resena.pelicula.pk)
    else:
        form = ResenaForm(instance=resena)
    
    contexto = {
        "form": form,
        "titulo_pagina": "Editar reseña",
        "resena": resena,
        "pelicula": resena.pelicula, 
        "resenas": resenas_listado,          
        "promedio_resenas": promedio_resenas, 
        "ya_comento": False,
    }
    
    return render(request, "peliculas/detalle_pelicula.html", contexto)

@login_required
@require_http_methods(["GET", "POST"])
def eliminar_resena(request, pk):

    # Solo se elimina la reseña cuando se recibe una petición POST.
    if request.method == "POST":
        # Busca la reseña y verifica que pertenezca al usuario que inició sesión.
            # Si no existe o no pertenece al usuario, devuelve un error 404.
        resena = get_object_or_404(Resena, pk=pk, autor=request.user)

        # Guardamos el ID de la película antes de eliminar la reseña.
        pelicula_id = resena.pelicula_id

        # Elimina la reseña de la base de datos.
        resena.delete()
        messages.success(request, "La reseña se eliminó.")

        # Redirige a las reseñas de la película.
        return redirect("peliculas:detalle", id=pelicula_id)