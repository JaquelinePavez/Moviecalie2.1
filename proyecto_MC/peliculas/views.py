from django.shortcuts import render
from django.shortcuts import redirect

peliculas = [
    {
        "id": 1,
        "imagen": "https://www.cinematerial.com/p/297x/l94wgadr/f1-the-movie-movie-poster-md.jpg?v=1748905004",
        "titulo": "F1: La Película",
        "anio": "2025",
        "duracion": "155",
        "calificacion": "8.0",
        "sinopsis": "Un piloto retirado vuelve a las pistas para mentorear a un joven talento.",
        "genero": "Drama, Acción",
        "reparto": "Brad Pitt, Damson Idris, Kerry Condon",
        "clasificacion": "PG-13",
        "plataforma": "Cines",
    },
    {
    
        "id": 2,
        "imagen": "https://cloudfront-us-east-1.images.arcpublishing.com/infobae/H2DVBWCFAZGYDFWWN4TEASWRZI.jpg",
        "titulo": "Oppenheimer",
        "anio": "2023",
        "duracion": "180",
        
        "calificacion": "8.9",
        "sinopsis": "En tiempos de guerra, el físico J. Robert Oppenheimer lidera el Proyecto Manhattan, una iniciativa secreta para desarrollar la primera bomba atómica de la historia.",
        "genero": "Biografía, Drama, Historia",
        "reparto": "Cillian Murphy, Emily Blunt, Matt Damon, Robert Downey Jr.",
        "clasificacion": "R",
        "plataforma": "Max"
    }
    
]

# Movi la vista inicio() a proyecto_MC/views.py,
# por que es el inicio general del proyecto.

# Las demás vistas estan bien en aplicación porque son funcionalidades específicas de películas.

#refactorizamos
def agregar_pelicula(request):

    # GET: mostrar el formulario
    if request.method == "GET":
        contexto = {"titulo_pagina": "Agregar nueva pelicula"}
        return render(request, "peliculas/agregar.html", contexto)

    # POST: procesar los datos enviados por el formulario
    if request.method == "POST":
        id_mas_alto = 0

        for p in peliculas:
            if p["id"] > id_mas_alto:
                id_mas_alto = p["id"]

        proximo_id = id_mas_alto + 1

        pelicula = {
            "id": proximo_id,
            "imagen": request.POST.get("imagen"),
            "titulo": request.POST.get("titulo"),
            "anio": request.POST.get("anio"),
            "duracion": request.POST.get("duracion"),
            "calificacion": request.POST.get("calificacion"),
            "sinopsis": request.POST.get("sinopsis"),
            "genero": request.POST.get("genero"),
            "reparto": request.POST.get("reparto"),
            "clasificacion": request.POST.get("clasificacion"),
            "plataforma": request.POST.get("plataforma"),
        }

        peliculas.append(pelicula)
        return redirect("peliculas:detalle", id=pelicula["id"])
    

def detalle_pelicula(request, id):
    # busco la pelicula por id dentro de la lista en memoria
    pelicula = None
    for p in peliculas:
        if p["id"] == id:
            pelicula = p
            break

    # separo el reparto en una lista para poder recorrerla con {% for %}
    reparto = []
    if pelicula and pelicula["reparto"]:
        reparto = [nombre.strip() for nombre in pelicula["reparto"].split(",") if nombre.strip()]

    contexto = {
        "titulo_pagina": "Detalle de la pelicula",
        "pelicula": pelicula,
        "reparto": reparto,
    }
    return render(request, "peliculas/detalle.html", contexto)

#------------------------------------------------------------------------------------------------#
# Lista global temporal (simula la base de datos) para que persista la informacion
RESENAS_LISTA = [
    {
        'pelicula_id': 1,
        'usuario': 'George_Allison',
        'calificacion': '9.0 / 10',
        'foto_usuario': 'recursos/imagenes/usuarios/usuario_1.jpg',
        'titulo': 'BUENISIMA',
        'contenido': 'F1 es un espectáculo visual imponente que redefine el cine de automovilismo...',
        'reportes': 0,
        'comentarios_count': 50
    },
    {
        'pelicula_id': 1,
        'usuario': 'Cinefilo88',
        'calificacion': '3.0 / 10',
        'foto_usuario': 'recursos/imagenes/usuarios/usuario_2.jpg',
        'titulo': 'REPETITIVA',
        'contenido': 'Aunque la acción es impecable, la banda sonora de Hans Zimmer se siente algo repetitiva...',
        'reportes': 2,
        'comentarios_count': 5
    }
]

def detalle_resenas_pelicula(request, id):

    # Buscar la película
    pelicula = None
    for peli in peliculas:
        if peli["id"] == id:
            pelicula = peli
            break

    # GET: mostrar las reseñas de la película
    if request.method == "GET":
        resenas_de_esta_pelicula = []
        for resena in RESENAS_LISTA:
            if resena.get("pelicula_id") == id:
                resenas_de_esta_pelicula.append(resena)

        contexto = {
            "pelicula": pelicula,
            "resenas": resenas_de_esta_pelicula
        }
        return render(request, "peliculas/resenas_usuarios.html", contexto)

    # POST: agregar una nueva reseña
    if request.method == "POST":
        nueva_resena = {
            "pelicula_id": id,
            "usuario": request.POST.get("usuario", "Usuario Anónimo"),
            "calificacion": f"{request.POST.get('calificacion', '10')} / 10",
            "foto_usuario": "recursos/imagenes/usuarios/usuario_3.jpg",
            "titulo": request.POST.get("titulo"),
            "contenido": request.POST.get("contenido"),
            "reportes": 0,
            "comentarios_count": 0
        }

        RESENAS_LISTA.insert(0, nueva_resena)
        return redirect("peliculas:resenas_pelicula", id=id)
