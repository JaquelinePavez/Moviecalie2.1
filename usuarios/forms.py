from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario

#usercreationform es un modelForm ya armado para crear usuarios.

class RegistroForm(UserCreationForm):#heredda de usercreationform el registro y seguridad de hasheo y le agrega campos propios como email
    # UserCreationForm no tiene email, por eso se declara acá y se marca obligatorio
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = Usuario #indica el modelo
        fields = ("username", "email")  #fields: es la lista explicita 
        #de campos del modelo que van a aparecen en el formulario
        # password1 y password2 los agrega UserCreationForm por su cuenta

    def clean_email(self):
        # se pasa a minúsculas para que "Ana@mail.com" y "ana@mail.com" sean el mismo email
        email = self.cleaned_data.get("email").lower()

        # iexact compara sin distinguir mayúsculas de minúsculas
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ese email ya está registrado.")

        return email  # lo que devuelve clean_email es lo que se guarda en la base