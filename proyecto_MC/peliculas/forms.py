from django import forms
from .models import Resena
#RESEÑAS:

class ResenaForm(forms.ModelForm):#USAMOS MODEL FORMS PARA QUE LAS VALIDACIONES 
#LAS HAGA EN CONJUNTO CON EL MODELO
    calificacion = forms.DecimalField( min_value=1, max_value=10, max_digits=3, decimal_places=1,)
    
    class Meta:
        model = Resena 
        fields = ["calificacion", "texto"] #ESTO ES LO QUE SE VA A DIBUJAR 
       
