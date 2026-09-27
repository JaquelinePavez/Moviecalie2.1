from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views


urlpatterns = [
    path("admin/", admin.site.urls),

    #aca esta url raíz "/" seria el inicio general del proyecto.
    path("", views.inicio, name="inicio"),
    path("peliculas/", include("peliculas.urls")),
# .............. agregue rutas genericas para los logins ..............................................#
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    #login/ le muestra el formulario a alguien que ya tiene cuenta
    path('logout/', auth_views.LogoutView.as_view(next_page='peliculas:catalogo'), name='logout'),
    #logout/ cierra la sesione de quien este logueado y lo manda al catalogo 
    path('registro/', views.registro_usuario, name='registro'),
    #crea una cuenta por primera vez y automaticamente lo loguea-
    #(login(request, nuevo_usuario) en la vista) para que no tenga que ir después a /login/ 

]
# Sirve archivos media únicamente durante el desarrollo local /esto es para que las imagenes que se van subiendo en el desarrollo local se puedan visualizar bien 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)