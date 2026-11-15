from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .comun import RUTAS_FBV, contexto_resenas
from .forms import FiltroPeliculaForm, ResenaForm
from .models import Pelicula, Resena


@require_http_methods(["GET"])
def catalogo_peliculas(request):
    """Renderiza el catálogo de películas con la
    opción de filtrarlas según los criterios del formulario"""
    queryset = (
    Pelicula.objects.prefetch_related(
        'generos', 'actores', 'directores'
    )
)
    form = FiltroPeliculaForm(request.GET)

    if form.is_valid():
        queryset = form.filtrar(queryset)
    else:
        queryset = queryset.order_by('-fecha_estreno')

    context = {
        'form': form,
        'peliculas': queryset,
        'rutas': RUTAS_FBV,
    }
    return render(request, 'peliculas/catalogo.html', context)


@require_http_methods(["GET"])
def detalle(request, id):
    """Renderiza la página de detalle de una película, incluyendo
    sus reseñas y el formulario para agregar una nueva reseña si
    el usuario está autenticado y no ha comentado aún."""
    pelicula = get_object_or_404(Pelicula, id=id)

    ya_comento = False
    if request.user.is_authenticated:
        ya_comento = (
            Resena.objects.filter(
                pelicula=pelicula, autor=request.user
            ).exists()
        )
    if request.method == "GET":
        contexto = contexto_resenas(
            pelicula,
            ResenaForm(),
            "Agregar reseña",
            ya_comento,
            RUTAS_FBV,
        )
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
    """Permite a un usuario autenticado agregar una reseña a una película."""
    if request.method == "GET":
         return redirect("peliculas:detalle", id=id)

    pelicula = get_object_or_404(Pelicula, id=id)
    form = ResenaForm(request.POST)
    ya_tiene_resena = (
        Resena.objects.filter(
            pelicula=pelicula, autor=request.user
        ).exists()
    )

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

    contexto = contexto_resenas(
        pelicula,
        form,
        "Agregar reseña",
        ya_tiene_resena,
        RUTAS_FBV,
    )

    return render(request, "peliculas/detalle_pelicula.html", contexto)


@login_required
@permission_required("peliculas.change_resena", raise_exception=True)
@require_http_methods(["GET", "POST"])
def editar_resenas(request, pk):
    """Permite a un usuario autenticado editar su reseña de una película."""
    resena = get_object_or_404(Resena, pk=pk, autor=request.user)
    pelicula = resena.pelicula

    if request.method == "POST":
        form = ResenaForm(request.POST, instance=resena)
        if form.is_valid():
            with transaction.atomic():
                resena = form.save()
            messages.success(request, "La reseña se actualizó correctamente.")
        return redirect("peliculas:detalle", id=resena.pelicula.pk)
    else:
        form = ResenaForm(instance=resena)

    contexto = contexto_resenas(
        pelicula,
        form,
        "Editar reseña",
        False,
        RUTAS_FBV,
    )
    contexto["resena"] = resena
    return render(request, "peliculas/detalle_pelicula.html", contexto)


@login_required
@permission_required("peliculas.delete_resena", raise_exception=True)
@require_POST
def eliminar_resena(request, pk):
    """Permite a un usuario autenticado eliminar su reseña de una película."""
    if request.method == "POST":
        resena = get_object_or_404(Resena, pk=pk, autor=request.user)
        pelicula_id = resena.pelicula_id
        resena.delete()
        messages.success(request, "La reseña se eliminó.")
        return redirect("peliculas:detalle", id=pelicula_id)
