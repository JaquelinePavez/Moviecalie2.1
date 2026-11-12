from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import FiltroPeliculaForm, ResenaForm
from .models import (
    Pelicula,
    Resena,
)


@require_http_methods(["GET"])
def catalogo_peliculas(request):
    queryset = Pelicula.objects.prefetch_related(
        'generos', 'actores', 'directores')
    form = FiltroPeliculaForm(request.GET)

    if form.is_valid():
        queryset = form.filtrar(queryset)
    else:
        queryset = queryset.order_by('-fecha_estreno')

    context = {
        'form': form,
        'peliculas': queryset,
    }
    return render(request, 'peliculas/catalogo.html', context)

@require_http_methods(["GET"])
def detalle(request, id):
    pelicula = get_object_or_404(Pelicula, id=id)  
    promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"] or 0.1

    ya_comento = False
    if request.user.is_authenticated:
        ya_comento = Resena.objects.filter(pelicula=pelicula, autor=request.user).exists()
    if request.method == "GET":  
        form = ResenaForm() 
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
@permission_required("peliculas.add_resena", raise_exception=True)
@require_http_methods(["GET", "POST"])
def agregar_resena(request, id):
     
    if request.method == "GET":
         return redirect("peliculas:detalle", id=id)
    
    pelicula = get_object_or_404(Pelicula, id=id)
    promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"] or 0.1    
    form = ResenaForm(request.POST)
    ya_tiene_resena = Resena.objects.filter(pelicula=pelicula, autor=request.user).exists()

    if ya_tiene_resena:
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


@login_required
@permission_required("peliculas.change_resena", raise_exception=True)
@require_http_methods(["GET", "POST"])
def editar_resenas(request, pk):
    resena = get_object_or_404(Resena, pk=pk, autor=request.user)
    pelicula = resena.pelicula
    promedio_resenas = pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"] or 0.1    
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
@permission_required("peliculas.delete_resena", raise_exception=True)
@require_POST
def eliminar_resena(request, pk):
    if request.method == "POST":
        resena = get_object_or_404(Resena, pk=pk, autor=request.user)
        pelicula_id = resena.pelicula_id
        resena.delete()
        messages.success(request, "La reseña se eliminó.")
        return redirect("peliculas:detalle", id=pelicula_id)