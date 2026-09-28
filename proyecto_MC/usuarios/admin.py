from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Perfil

admin.site.register(Usuario, UserAdmin) #(no ModelAdmin genérico) porque Usuario hereda de AbstractUser
admin.site.register(Perfil)