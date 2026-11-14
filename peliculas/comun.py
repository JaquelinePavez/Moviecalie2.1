from django.db.models import Avg


def promedio_resenas(pelicula):
    """Calcula el promedio de calificaciones de las reseñas de una película"""
    promedio = pelicula.resenas.aggregate(
        Avg("calificacion")
    )["calificacion__avg"]
    return promedio


def contexto_resenas(pelicula, form, titulo_pagina, ya_comento):
    """Genera el contexto para las vistas de detalle,
    agregar y editar reseñas"""
    return {
        "pelicula": pelicula,
        "titulo_pagina": titulo_pagina,
        "resenas": pelicula.resenas.order_by("-id_resena"),
        "promedio_resenas": promedio_resenas(pelicula),
        "form": form,
        "ya_comento": ya_comento,
    }
