from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from .forms import FiltroPeliculaForm
from .models import Actor, Pelicula, Resena

# Tres secciones, según la capa que se prueba:
#     1. MODELO     2. VISTAS     3. TEMPLATES
#
# Dentro de cada sección, tres tipos de prueba:
#     - Unitarios:      una pieza sola, aislada del resto.
#     - De integración: dos o más piezas trabajando juntas.
#     - Funcionales:    una operación completa, como la haría una
#                       persona: de la solicitud al resultado final.


def crear_pelicula(titulo="El vuelo", calificacion_promedio=None):
    """Crea y guarda una película con los datos mínimos obligatorios."""
    return Pelicula.objects.create(
        titulo=titulo,
        sinopsis="Una sinopsis de prueba.",
        duracion_minutos=138,
        fecha_estreno=date(2012, 11, 1),
        imagen_portada="poster.jpg",
        calificacion_promedio=calificacion_promedio,
    )


def crear_usuario(username="ana"):
    """Crea y guarda un usuario. No tiene permisos ni grupos."""
    return get_user_model().objects.create_user(
        username=username,
        email=f"{username}@mail.com",
        password="clave-segura-123",
    )

# =====================================================================
# 1. TESTS DEL MODELO
# Reglas que viven en models.py.
# =====================================================================


# ----- Unitarios -----------------------------------------------------
# El objeto se arma en memoria y no se guarda: no usan la base.


class PeliculaYResenaTests(TestCase):
    """Texto que muestra una película y límite de palabras de la reseña."""

    def test_muestra_titulo_y_anio_de_la_pelicula(self):
        pelicula = Pelicula(
            titulo="Titanic",
            fecha_estreno=date(1997, 12, 19),
        )
        self.assertEqual(str(pelicula), "Titanic (1997)")

    def test_acepta_resena_de_dos_palabras(self):
        resena = Resena(texto="Muy buena")
        resena.clean()

    def test_rechaza_resena_de_mas_de_500_palabras(self):
        resena = Resena(texto="palabra " * 501)
        with self.assertRaises(ValidationError):
            resena.clean()

    def test_rechaza_resena_de_una_sola_palabra(self):
        resena = Resena(texto="Buena")
        with self.assertRaises(ValidationError):
            resena.clean()


class TrailerPeliculaTests(TestCase):
    """Conversión del enlace del tráiler al formato embed de YouTube."""

    def test_convierte_enlace_de_youtube_a_formato_embed(self):
        pelicula = Pelicula(
            url_trailer="https://www.youtube.com/watch?v=abc123",
        )
        self.assertEqual(
            pelicula.trailer_embed_url,
            "https://www.youtube.com/embed/abc123",
        )

    def test_convierte_enlace_corto_de_youtube_a_formato_embed(self):
        pelicula = Pelicula(
            url_trailer="https://youtu.be/abc123",
        )
        self.assertEqual(
            pelicula.trailer_embed_url,
            "https://www.youtube.com/embed/abc123",
        )

    def test_conserva_enlace_que_ya_esta_en_formato_embed(self):
        pelicula = Pelicula(
            url_trailer="https://www.youtube.com/embed/abc123",
        )
        self.assertEqual(
            pelicula.trailer_embed_url,
            "https://www.youtube.com/embed/abc123",
        )

    def test_devuelve_none_si_no_hay_enlace_de_trailer(self):
        pelicula = Pelicula(url_trailer="")
        self.assertIsNone(pelicula.trailer_embed_url)

    def test_devuelve_none_si_el_enlace_no_es_de_youtube(self):
        pelicula = Pelicula(url_trailer="https://vimeo.com/123456")
        self.assertIsNone(pelicula.trailer_embed_url)


class ActorTests(TestCase):
    """Texto con el que se muestra un actor."""

    def test_muestra_nombre_y_apellido_del_actor(self):
        actor = Actor(nombre="Tim", apellido="Robbins")
        self.assertEqual(str(actor), "Tim Robbins")


# ----- De integración ------------------------------------------------
# El modelo junto con la base de datos: se guarda y se comprueba
# lo que quedó guardado o lo que la base rechazó.


class PeliculasModelsTest(TestCase):
    """Reglas del modelo que relacionan películas, reseñas y usuarios."""

    def setUp(self):
        self.pelicula = Pelicula.objects.create(
            titulo="El vuelo",
            sinopsis=(
                "Un piloto logra evitar que un vuelo se estrelle, "
                "pero la investigación del fallo revela algo inquietante."
            ),
            duracion_minutos=138,
            fecha_estreno=date(2012, 11, 1),
            imagen_portada="poster.jpg",
        )
        self.usuario = get_user_model().objects.create_user(
            username="ana",
            email="ana@mail.com",
            password="clave-segura-123",
        )

    def test_la_calificacion_es_el_promedio_de_las_resenas(self):
        Resena.objects.create(
            pelicula=self.pelicula,
            autor=self.usuario,
            texto=(
                "Una película que pone en juego todo, "
                "te deja mucho que pensar y analizar."
            ),
            calificacion=Decimal("6"),
        )
        otro_usuario = get_user_model().objects.create_user(
            username="jose",
            email="jose@mail.com",
            password="clave26-segura",
        )
        Resena.objects.create(
            pelicula=self.pelicula,
            autor=otro_usuario,
            texto="Muy buena, me gustó la trama y el suspenso lo es todo",
            calificacion=Decimal("8"),
        )
        self.pelicula.refresh_from_db()
        self.assertEqual(self.pelicula.calificacion_promedio, 7)

    def test_al_borrar_la_unica_resena_queda_sin_calificacion(self):
        resena = Resena.objects.create(
            pelicula=self.pelicula,
            autor=self.usuario,
            texto="Muy buena, me gustó la trama y el suspenso lo es todo",
            calificacion=Decimal("8.0"),
        )
        resena.delete()
        self.pelicula.refresh_from_db()
        self.assertIsNone(self.pelicula.calificacion_promedio)

    def test_no_se_permite_dos_resenas_del_mismo_usuario_en_una_misma_pelicula(
        self,
    ):
        Resena.objects.create(
            pelicula=self.pelicula,
            autor=self.usuario,
            texto=(
                "Una película que pone en juego todo, "
                "te deja mucho que pensar y analizar."
            ),
            calificacion=Decimal("9.3"),
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Resena.objects.create(
                    pelicula=self.pelicula,
                    autor=self.usuario,
                    texto="Genial la trama, muy buena",
                    calificacion=Decimal("8.5"),
                )


class CalificacionPeliculaTests(TestCase):
    """Restricción de la base: la calificación va de 0 a 10."""

    def setUp(self):
        self.pelicula = Pelicula(
            titulo="Película de prueba",
            sinopsis="Una sinopsis de prueba.",
            duracion_minutos=100,
            fecha_estreno=date(2020, 1, 1),
            imagen_portada="poster.jpg",
            calificacion_promedio=Decimal("5.0"),
        )

    def test_acepta_calificacion_cero(self):
        self.pelicula.calificacion_promedio = Decimal("0.0")
        self.pelicula.save()

    def test_acepta_calificacion_diez(self):
        self.pelicula.calificacion_promedio = Decimal("10.0")
        self.pelicula.save()

    def test_rechaza_calificacion_menor_que_cero(self):
        self.pelicula.calificacion_promedio = Decimal("-0.1")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.pelicula.save()

    def test_rechaza_calificacion_mayor_que_diez(self):
        self.pelicula.calificacion_promedio = Decimal("10.1")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.pelicula.save()

# =====================================================================
# 2. TESTS DE VISTAS
# Qué responde el servidor: código de respuesta, redirecciones,
# permisos y datos que la vista le pasa al template.
# =====================================================================


# ----- Unitarios -----------------------------------------------------
# El formulario que usa la vista del catálogo, probado solo,
# sin hacer ninguna solicitud.


class FiltroPeliculaFormTests(TestCase):
    """Validación del formulario de filtros del catálogo."""

    def test_rechaza_anio_desde_mayor_que_anio_hasta(self):
        datos = {'anio_desde': 2020, 'anio_hasta': 2010}
        form = FiltroPeliculaForm(datos)
        es_valido = form.is_valid()
        self.assertFalse(es_valido)
        self.assertIn(
            'El año "desde" no puede ser mayor que el año "hasta".',
            form.non_field_errors(),
        )

    def test_rechaza_anio_anterior_a_1888(self):
        datos = {'anio_desde': 1500}
        form = FiltroPeliculaForm(datos)
        self.assertFalse(form.is_valid())
        self.assertIn('anio_desde', form.errors)


# ----- De integración ------------------------------------------------
# La vista junto con las rutas, la base y los permisos, usando
# el cliente de pruebas (self.client).


class CatalogoVistaTests(TestCase):
    """La vista del catálogo, que es la página de inicio."""

    def test_el_catalogo_responde_correctamente(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertEqual(respuesta.status_code, 200)

    def test_buscar_por_titulo_devuelve_solo_las_que_coinciden(self):
        el_vuelo = crear_pelicula(titulo="El vuelo")
        crear_pelicula(titulo="Titanic")

        respuesta = self.client.get(reverse("inicio"), {"q": "vuelo"})

        peliculas = list(respuesta.context["peliculas"])
        self.assertEqual(peliculas, [el_vuelo])


class ResenaPermisosVistaTests(TestCase):
    """Quién puede publicar una reseña."""

    def setUp(self):
        self.pelicula = crear_pelicula()
        self.url = reverse("peliculas:agregar", args=[self.pelicula.pk])
        self.datos = {"calificacion": "8.0", "texto": "Muy buena película"}

    def test_sin_sesion_se_redirige_al_login_y_no_se_guarda(self):
        respuesta = self.client.post(self.url, self.datos)

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/usuarios/login/", respuesta.url)
        self.assertEqual(Resena.objects.count(), 0)

    def test_con_sesion_pero_sin_permiso_responde_403(self):
        usuario = crear_usuario()
        self.client.force_login(usuario)

        respuesta = self.client.post(self.url, self.datos)

        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Resena.objects.count(), 0)


# =====================================================================
# 3. TESTS DE TEMPLATES
# Qué se muestra en la página: el template usado y los textos
# que aparecen o no aparecen según el caso.
# =====================================================================


# ----- Unitarios -----------------------------------------------------
# Un template renderizado solo, sin pasar por ninguna vista.


class TarjetaPeliculaTemplateTests(TestCase):
    """El componente tarjeta_pelicula.html, renderizado sin ninguna vista."""

    def renderizar_tarjeta(self, pelicula):
        contexto = {"pelicula": pelicula, "url_detalle": "/detalle/"}
        return render_to_string(
            "componentes/tarjeta_pelicula.html",
            contexto,
        )

    def test_sin_calificacion_muestra_el_aviso(self):
        pelicula = crear_pelicula()
        html = self.renderizar_tarjeta(pelicula)
        self.assertIn("Sin calificación", html)

    def test_con_calificacion_no_muestra_el_aviso(self):
        pelicula = crear_pelicula(calificacion_promedio=Decimal("8.5"))
        html = self.renderizar_tarjeta(pelicula)
        self.assertNotIn("Sin calificación", html)
        self.assertIn("de 10", html)


# ----- De integración ------------------------------------------------
# El template junto con la vista que lo renderiza.


class CatalogoTemplateTests(TestCase):
    """Lo que muestra la página del catálogo."""

    def test_usa_el_template_del_catalogo(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertTemplateUsed(respuesta, "peliculas/catalogo.html")

    def test_sin_peliculas_muestra_el_mensaje_de_sin_resultados(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, "No se encontraron películas")

    def test_muestra_el_titulo_de_la_pelicula_cargada(self):
        crear_pelicula(titulo="El vuelo")
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, "El vuelo")

# ----- Funcionales ---------------------------------------------------
# Una operación completa, comprobando lo que la persona ve al final.


class PublicarResenaTemplateTests(TestCase):
    """Recorrido completo: la reseña publicada aparece en el detalle."""

    def test_la_resena_publicada_se_ve_en_el_detalle(self):
        pelicula = crear_pelicula()
        usuario = crear_usuario()
        permiso = Permission.objects.get(codename="add_resena")
        usuario.user_permissions.add(permiso)
        self.client.force_login(usuario)
        url = reverse("peliculas:agregar", args=[pelicula.pk])
        datos = {"calificacion": "8.0", "texto": "Muy buena película"}

        respuesta = self.client.post(url, datos, follow=True)

        self.assertContains(respuesta, "Muy buena película")
        self.assertContains(respuesta, "Tu reseña se publicó correctamente.")
