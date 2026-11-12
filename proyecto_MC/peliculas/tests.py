from django.test import TestCase

from .forms import FiltroPeliculaForm


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
