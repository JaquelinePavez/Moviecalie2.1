from datetime import date

from django import forms

from .models import Actor, Director, Genero, Pelicula, Resena

#RESEÑAS:

class ResenaForm(forms.ModelForm):
    # Usamos ModelForm para que las validaciones se hagan en conjunto
    # con las del modelo.
    calificacion = forms.DecimalField(
        min_value=0.1,
        max_value=10,
        max_digits=3,
        decimal_places=1,
    )

    class Meta:
        model = Resena
        fields = ["calificacion", "texto"]


"""Busqueda de películas"""  

OPCIONES_ORDEN = [
    ('fecha_desc', 'Más recientes primero'),
    ('fecha_asc', 'Más antiguas primero'),
    ('calificacion_desc', 'Mejor calificadas'),
    ('calificacion_asc', 'Menor calificación'),
    ('titulo_asc', 'Título (A-Z)'),
]

OPCIONES_CALIFICACION = [
    ('', 'Cualquiera'),
    ('9.0', '⭐ 9.0+'),
    ('8.0', '⭐ 8.0+'),
    ('7.0', '⭐ 7.0+'),
    ('6.0', '⭐ 6.0+'),
    ('5.0', '⭐ 5.0+'),
    ('4.0', '⭐ 4.0+'),
    ('3.0', '⭐ 3.0+'),
    ('2.0', '⭐ 2.0+'),
]

# Traduce la clave de la URL al campo que necesita order_by()
CRITERIOS_ORDEN = {
    'calificacion_desc': '-calificacion_promedio',
    'calificacion_asc': 'calificacion_promedio',
    'fecha_desc': '-fecha_estreno',
    'fecha_asc': 'fecha_estreno',
    'titulo_asc': 'titulo',
}


class FiltroPeliculaForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Título de la película...'}
        ),
    )
    clasificacion = forms.ChoiceField(
        choices=[('', 'Todas')] + list(Pelicula.Clasificacion.choices),
        required=False,
    )
    anio_desde = forms.IntegerField(
        required=False,
        min_value=1888,
        widget=forms.NumberInput(attrs={'placeholder': '1990'}),
    )
    anio_hasta = forms.IntegerField(
        required=False,
        min_value=1888,
        widget=forms.NumberInput(attrs={'placeholder': '2026'}),
    )
    min_calificacion = forms.TypedChoiceField(
        choices=OPCIONES_CALIFICACION,
        coerce=float,
        empty_value=None,
        required=False,
    )
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all(),
        required=False,
        empty_label='Todos los géneros',
    )
   
    actor = forms.ModelChoiceField(
        queryset=Actor.objects.all(),
        required=False,
        empty_label='Todos los actores',
    )
    director = forms.ModelChoiceField(
        queryset=Director.objects.all(),
        required=False,
        empty_label='Todos los directores',
    )
    
    orden = forms.ChoiceField(
        choices=OPCIONES_ORDEN,
        required=False,
        initial='fecha_desc',
    )

    def clean(self):
        datos = super().clean()
        anio_desde = datos.get('anio_desde')
        anio_hasta = datos.get('anio_hasta')

        if anio_desde is not None and anio_hasta is not None:
            if anio_desde > anio_hasta:
                raise forms.ValidationError(
                    'El año "desde" no puede ser mayor que el año "hasta".'
                )
        return datos

    def filtrar(self, queryset):
        """Aplica al queryset los filtros elegidos. Usar solo si is_valid() es True."""
        datos = self.cleaned_data

        if datos['q']:
            queryset = queryset.filter(titulo__icontains=datos['q'])

        if datos['genero']:
            queryset = queryset.filter(generos=datos['genero'])

        if datos['clasificacion']:
            queryset = queryset.filter(clasificacion=datos['clasificacion'])

        if datos['actor']:
            queryset = queryset.filter(actores=datos['actor'])

        if datos['director']:
            queryset = queryset.filter(directores=datos['director'])

        # Fechas límite (no __year) para aprovechar el índice de fecha_estreno
        if datos['anio_desde'] is not None:
            queryset = queryset.filter(
                fecha_estreno__gte=date(datos['anio_desde'], 1, 1)
            )
        if datos['anio_hasta'] is not None:
            queryset = queryset.filter(
                fecha_estreno__lte=date(datos['anio_hasta'], 12, 31)
            )

        if datos['min_calificacion'] is not None:
            queryset = queryset.filter(
                calificacion_promedio__gte=datos['min_calificacion']
            )

        criterio_orden = CRITERIOS_ORDEN.get(datos['orden'], '-fecha_estreno')
        return queryset.distinct().order_by(criterio_orden)