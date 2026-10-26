from django.contrib.auth import views as auth_views
from django.contrib.auth import views as vistas_autenticacion
from django.urls import path, reverse_lazy
from . import views

app_name = "usuarios"

urlpatterns = [
    #login/ le muestra el formulario a alguien que ya tiene cuenta
    path("login/", auth_views.LoginView.as_view(template_name="usuarios/login.html"), name="login"),#template_name: indica que archivo html renderizar
    #logout/ cierra la sesione de quien este logueado y lo manda al catalogo
    
    path("logout/", auth_views.LogoutView.as_view(next_page='peliculas:catalogo'), name="logout"), #next_page: indica la url 
    #crea una cuenta por primera vez y automaticamente lo loguea-
    path("registro/", views.registro_usuario, name="registro"), #(login(request, nuevo_usuario) en la vista) para que no tenga que ir después a /login/ 

    #--------------------------------------nuevo------------------
    
    # Solicitar la recuperación de contraseña
    path("recuperar-contrasena/", vistas_autenticacion.PasswordResetView.as_view(
            template_name="usuarios/recuperar_contrasena.html",
            email_template_name="usuarios/correo_recuperacion_contrasena.txt",
            subject_template_name="usuarios/asunto_recuperacion_contrasena.txt",
            success_url=reverse_lazy("usuarios:recuperacion_enviada"),
        ),
        name="recuperar_contrasena",
    ),

    # Mostrar que se procesó la solicitud
    path("recuperacion-enviada/", vistas_autenticacion.PasswordResetDoneView.as_view(template_name="usuarios/recuperacion_enviada.html"), name="recuperacion_enviada",),

    # Permitir establecer una contraseña nueva
    path("nueva-contrasena/<uidb64>/<token>/", vistas_autenticacion.PasswordResetConfirmView.as_view(template_name="usuarios/nueva_contrasena.html", 
        success_url=reverse_lazy("usuarios:contrasena_cambiada"),
        ),
        name="confirmar_nueva_contrasena",
    ),

    # Confirmar que se cambió la contraseña
    path("contrasena-cambiada/", vistas_autenticacion.PasswordResetCompleteView.as_view(template_name="usuarios/contrasena_cambiada.html"),
        name="contrasena_cambiada",
    ),

    # Cambiar la contraseña conociendo la actual
    path("cambiar-contrasena/", vistas_autenticacion.PasswordChangeView.as_view(template_name="usuarios/cambiar_contrasena.html",
            success_url=reverse_lazy("usuarios:cambio_contrasena_completo")),
        name="cambiar_contrasena",
    ),

    # Confirmar que se cambió la contraseña actual
    path("cambio-contrasena-completo/", vistas_autenticacion.PasswordChangeDoneView.as_view(template_name="usuarios/cambio_contrasena_completo.html"),
        name="cambio_contrasena_completo",
    ),
]

