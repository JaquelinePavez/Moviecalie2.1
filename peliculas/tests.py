from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .forms import FiltroPeliculaForm
from .models import Pelicula, Resena


class FiltroPeliculaFormTests(TestCase):
    def test_rechaza_anio_desde_mayor_que_anio_hasta(self):
        datos = {'anio_desde': 2020, 'anio_hasta': 2010}
        form = FiltroPeliculaForm(datos)
        es_valido = form.is_valid()
        self.assertFalse(es_valido)
        self.assertIn(
            'El año "desde" no puede ser mayor que el año "hasta".',
            form.non_field_errors(),
        )


class PeliculaYResenaTests(TestCase):

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


class CalificacionPeliculaTests(TestCase):
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


class TrailerPeliculaTests(TestCase):
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

    def test_devuelve_none_si_no_hay_enlace_de_trailer(self):
        pelicula = Pelicula(url_trailer="")
        self.assertIsNone(pelicula.trailer_embed_url)

    def test_conserva_enlace_que_ya_esta_en_formato_embed(self):
        pelicula = Pelicula(
            url_trailer="https://www.youtube.com/embed/abc123",
        )
        self.assertEqual(
            pelicula.trailer_embed_url,
            "https://www.youtube.com/embed/abc123",
        )
