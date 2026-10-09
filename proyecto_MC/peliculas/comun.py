
#diccionario común para las clases definidas en la vistas 
contexto = {
            "pelicula": pelicula,
            "titulo_pagina": "Agregar reseña",
            "resenas": pelicula.resenas.order_by("-id_resena"),
            "promedio_resenas": promedio_resenas,
            "form": form,
        }
