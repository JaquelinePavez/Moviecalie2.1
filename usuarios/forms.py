from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class RegistroForm(UserCreationForm):
    """
    Formulario para registrar nuevos usuarios.
    Hereda de UserCreationForm para aprovechar sus campos
    y la validación de las contraseñas.
    """
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        """
        Indicamos qué modelo y qué campos se van a utilizar
        para crear el usuario.
        """
        model = Usuario
        fields = ("username", "email")


    def clean_email(self):
        """
        Verifica que el email no esté registrado anteriormente
        y lo convierte a minúsculas antes de guardarlo.
        """
        #a minúsculas - "Ana@mail.com"="ana@mail.com" sean el mismo email
        email = self.cleaned_data.get("email").lower()

        # iexact compara sin distinguir mayúsculas de minúsculas
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ese email ya está registrado.")
        #lo que devuelve es lo que se guarda en la base

        return email
