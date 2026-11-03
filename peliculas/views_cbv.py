from .models import Pelicula, Genero, Actor, Director, Resena #importa desde el modulo models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q, Avg  # agregamos Avg
from django.db.models.deletion import ProtectedError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db import transaction
from .forms import ResenaForm
from .models import Pelicula, Resena
from django.views.decorators.http import require_http_methods

# Mixin: pide sesión y limita el conjunto a las reseñas del usuario
class ResenasPropiasMixin(LoginRequiredMixin):
    model = Resena

    def get_queryset(self):
        return super().get_queryset().filter(autor=self.request.user)

class ResenaLista(ListView):
    # Permite consultar la lista, pero no modificar datos mediante otros métodos
    http_method_names = ["get", "head", "options"]
    model = Resena
    template_name = "peliculas/resenas_usuarios.html"
    context_object_name = "resenas"

    def get_queryset(self):
        # Busca la película por su ID; si no existe, devuelve un error 404
        self.pelicula = get_object_or_404(Pelicula, id=self.kwargs["id"])

        # Obtiene las reseñas de esa película, carga sus autores y las ordena por ID descendente
        return self.pelicula.resenas.select_related("autor").order_by("-id_resena")

    def get_context_data(self, **kwargs):
        # Obtiene los datos que se enviarán a la plantilla
        datos = super().get_context_data(**kwargs)

        # Agrega la película y el promedio de las calificaciones de sus reseñas al contexto
        datos["pelicula"] = self.pelicula
        # ANTES: datos["promedio_resenas"] = self.pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"]
        # LO COMENTO PORQUE SI NO HAY RESEÑAS DEVUELVE None y tiene que mostrar 0
        datos["promedio_resenas"] = self.pelicula.resenas.aggregate(Avg("calificacion"))["calificacion__avg"] or 0
        return datos
        


class ResenaDetalle(DetailView):
    # Solo permite consultar los datos de una reseña
    http_method_names = ["get", "head", "options"]
    model = Resena
    template_name = "peliculas/detalle_resena.html"
    context_object_name = "resena"


# ALTA: crea una reseña; el autor sale de la sesión y la película de la URL
class ResenaCrear(LoginRequiredMixin, CreateView):
    http_method_names = ["get", "post", "head", "options"]
    model = Resena
    form_class = ResenaForm
    template_name = "peliculas/formulario_resena.html"
    extra_context = {"titulo_pagina": "Nueva reseña"}

    def form_valid(self, form):
        # Asigna automáticamente el usuario conectado como autor de la reseña
        form.instance.autor = self.request.user

        # Busca la película indicada en la URL y la asigna a la reseña
        form.instance.pelicula = get_object_or_404(Pelicula, id=self.kwargs["id"])

        # Guarda la reseña dentro de una transacción para mantener la integridad de los datos
        with transaction.atomic():
            respuesta = super().form_valid(form)

        # Muestra un mensaje de confirmación después de crear la reseña
        messages.success(self.request, "La reseña se creó correctamente.")
        return respuesta

    def get_success_url(self):
        # Redirige al detalle de la reseña recién creada
        return reverse("peliculas:detalle_resena", kwargs={"pk": self.object.pk})

# EDICIÓN: permite modificar únicamente las reseñas del usuario conectado
class ResenaEditar(ResenasPropiasMixin, UpdateView):
    http_method_names = ["get", "post", "head", "options"]
    form_class = ResenaForm
    template_name = "peliculas/formulario_resena.html"
    extra_context = {"titulo_pagina": "Editar reseña"}

    def form_valid(self, form):
        # Guarda los cambios de la reseña si el formulario es válido
        respuesta = super().form_valid(form)

        # Informa que la reseña se actualizó correctamente
        messages.success(self.request, "La reseña se actualizó correctamente.")
        return respuesta

    def get_success_url(self):
        # Redirige al detalle de la reseña editada
        return reverse("peliculas:detalle_resena", kwargs={"pk": self.object.pk})

# ELIMINACIÓN: permite borrar únicamente las reseñas del usuario conectado
class ResenaEliminar(ResenasPropiasMixin, DeleteView):
    http_method_names = ["get", "post", "head", "options"]
    template_name = "peliculas/confirmar_eliminacion.html"
    context_object_name = "resena"
    # success_url = reverse_lazy("peliculas:resenas_pelicula")

    def form_valid(self, form):
        # Ejecuta la eliminación de la reseña y obtiene la respuesta correspondiente
        respuesta = super().form_valid(form)

        # Muestra un mensaje de confirmación después de eliminar la reseña
        messages.success(self.request, "La reseña se eliminó.")
        return respuesta

    def get_success_url(self):
        # Después de eliminar la reseña, vuelve al detalle de la película a la que pertenecía
        return reverse_lazy("peliculas:detalle", kwargs={"id": self.object.pelicula_id})