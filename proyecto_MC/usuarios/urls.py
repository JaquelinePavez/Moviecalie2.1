from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    #login/ le muestra el formulario a alguien que ya tiene cuenta
    path("login/", auth_views.LoginView.as_view(template_name="usuarios/login.html"), name="login"),#template_name: indica que archivo html renderizar
    #logout/ cierra la sesione de quien este logueado y lo manda al catalogo
    
    path("logout/", auth_views.LogoutView.as_view(next_page='peliculas:catalogo'), name="logout"), #next_page: indica la url 
    #crea una cuenta por primera vez y automaticamente lo loguea-
    path("registro/", views.registro_usuario, name="registro"), #(login(request, nuevo_usuario) en la vista) para que no tenga que ir después a /login/ 
]
   
