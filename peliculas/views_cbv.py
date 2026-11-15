from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .comun import RUTAS_CBV, contexto_resenas
from .forms import FiltroPeliculaForm, ResenaForm
from .models import Pelicula, Resena


class PeliculaCatalogo(ListView):
    """Muestra el catálogo de películas con filtros."""
    model = Pelicula
    template_name = "peliculas/catalogo.html"
    context_object_name = "peliculas"

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related(
            "generos",
            "actores",
            "directores",
        )
        self.form = FiltroPeliculaForm(self.request.GET)

        if self.form.is_valid():
            return self.form.filtrar(queryset)
        return queryset.order_by("-fecha_estreno")

    def get_context_data(self, **kwargs):
        datos = super().get_context_data(**kwargs)
        datos["form"] = self.form
        datos["rutas"] = RUTAS_CBV
        return datos


class PeliculaDetalle(DetailView):
    """Muestra el detalle de una película y sus reseñas."""
    model = Pelicula
    template_name = "peliculas/detalle_pelicula.html"
    context_object_name = "pelicula"

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            "generos",
            "actores",
            "directores",
        )

    def get_context_data(self, **kwargs):
        datos = super().get_context_data(**kwargs)
        ya_comento = (
            self.request.user.is_authenticated
            and self.object.resenas.filter(
                autor=self.request.user
            ).exists()
        )
        datos.update(
            contexto_resenas(
                self.object,
                ResenaForm(),
                "Agregar reseña",
                ya_comento,
                RUTAS_CBV,
            )
        )
        return datos


class ResenasPropiasMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Requiere autenticación y limita el acceso a reseñas propias."""
    model = Resena

    def get_queryset(self):
        """Filtra el conjunto de reseñas para que solo incluya
        las reseñas del usuario autenticado."""
        return super().get_queryset().filter(autor=self.request.user)

class ResenaCrear(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Permite a un usuario autenticado crear una reseña para una película."""
    permission_required = "peliculas.add_resena"
    http_method_names = ["get", "post", "head", "options"]
    model = Resena
    form_class = ResenaForm
    template_name = "peliculas/detalle_pelicula.html"
    extra_context = {"titulo_pagina": "Nueva reseña"}

    def get_pelicula(self):
        if not hasattr(self, "pelicula"):
            self.pelicula = get_object_or_404(
                Pelicula,
                id=self.kwargs["id"],
            )
        return self.pelicula

    def get_context_data(self, **kwargs):
        datos = super().get_context_data(**kwargs)
        pelicula = self.get_pelicula()
        ya_comento = Resena.objects.filter(
            pelicula=pelicula,
            autor=self.request.user,
        ).exists()
        datos.update(
            contexto_resenas(
                pelicula,
                datos["form"],
                self.extra_context["titulo_pagina"],
                ya_comento,
                RUTAS_CBV
            )
        )
        return datos

    def form_valid(self, form):
        """Asigna el autor y la película a la reseña antes de guardarla."""
        pelicula = self.get_pelicula()
        ya_tiene_resena = Resena.objects.filter(
            pelicula=pelicula,
            autor=self.request.user,
        ).exists()
        if ya_tiene_resena:
            form.add_error(
                None,
                "Ya has publicado una reseña para esta película.",
            )
            return self.form_invalid(form)

        form.instance.autor = self.request.user
        form.instance.pelicula = pelicula
        with transaction.atomic():
            respuesta = super().form_valid(form)

        messages.success(self.request, "La reseña se creó correctamente.")
        return respuesta

    def get_success_url(self):
        """Redirige al detalle de la película después de crear la reseña."""
        return reverse_lazy(
            "peliculas:detalle_pelicula_cbv",
            kwargs={"pk": self.object.pelicula_id},
        )


class ResenaEditar(ResenasPropiasMixin, UpdateView):
    """Permite a un usuario autenticado editar su reseña de una película."""
    permission_required = "peliculas.change_resena"
    http_method_names = ["get", "post", "head", "options"]
    form_class = ResenaForm
    template_name = "peliculas/detalle_pelicula.html"
    extra_context = {"titulo_pagina": "Editar reseña"}

    def get_context_data(self, **kwargs):
        datos = super().get_context_data(**kwargs)
        datos.update(
            contexto_resenas(
                self.object.pelicula,
                datos["form"],
                self.extra_context["titulo_pagina"],
                False,
                RUTAS_CBV
            )
        )
        datos["resena"] = self.object
        return datos

    def form_valid(self, form):
        """Actualiza la reseña y muestra un mensaje de éxito."""
        respuesta = super().form_valid(form)
        messages.success(self.request, "La reseña se actualizó correctamente.")
        return respuesta

    def get_success_url(self):
        """Redirige al detalle de la película después de editar la reseña."""
        return reverse_lazy(
            "peliculas:detalle_pelicula_cbv",
            kwargs={"pk": self.object.pelicula_id},
        )


class ResenaEliminar(ResenasPropiasMixin, DeleteView):
    """Permite a un usuario autenticado eliminar su reseña de una película."""
    permission_required = "peliculas.delete_resena"
    http_method_names = ["post"]
    context_object_name = "resena"

    def form_valid(self, form):
        """Elimina la reseña y muestra un mensaje de éxito."""
        respuesta = super().form_valid(form)
        messages.success(self.request, "La reseña se eliminó.")
        return respuesta

    def get_success_url(self):
        """Redirige al detalle de la película después de eliminar la reseña."""
        return reverse_lazy(
            "peliculas:detalle_pelicula_cbv",
            kwargs={"pk": self.object.pelicula_id},
        )
