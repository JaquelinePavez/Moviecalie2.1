import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables del archivo .env, si existe.
# No reemplaza las variables que ya estén definidas en el entorno.
load_dotenv(BASE_DIR / ".env")

# Leer la clave secreta desde una variable de entorno.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

# Si no existe la clave, mostrar un error claro.
if not SECRET_KEY:
    raise ImproperlyConfigured("Falta configurar DJANGO_SECRET_KEY")

# Activar DEBUG solo cuando la variable diga "true".
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

# Leer los hosts permitidos desde una variable de entorno.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    "https://localhost:8000",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "peliculas.apps.PeliculasConfig",
    "usuarios.apps.UsuariosConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware', # <-- Debe ir primero
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", #verifica que el token que recibe por formulario sea igual al que guardo en la cookie del usuario
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <-- Debe ir después
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],# Le indica a Django buscar en la raíz
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth", #le agrega varibles al contexto de forma automatica, como user o perms(permisos) a todos los templates
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Validacion de contraseñas
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [ #rechaza contraseñas muy cortas establece un largo minimo
#,que no sean damasiado comunes, iguales al username, que no sea solo numericas.
   
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "static/"


# Configuración de Archivos Multimedia (Subidos por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



LOGIN_URL = 'usuarios:login' #si alguien intenta entrar a una pagina protegida sin estar logueado, mandalo para acá
AUTH_USER_MODEL = "usuarios.Usuario" 
LOGIN_REDIRECT_URL = 'inicio' #si alguien se loguea desde la pantalla de login directamente (sin venir de una página protegida), mandalo para acá al terminar
LOGOUT_REDIRECT_URL = "usuarios:login" #después de cerrar sesión, MovieCali vuelve al inicio de sesión.
# esto lo saque de aca :
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

#===============================Antiguo==================================
# Solo para desarrollo local.
# Muestra los correos en la terminal en lugar de enviarlos.
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
#========================================================================
#==============================Corregido=================================
# Usamos el backend que creamos para mostrar los correos
# de recuperación en la consola de forma más clara,
# evitando que los enlaces se corten en varias líneas.
# Esto se usa durante el desarrollo, ya que para enviar
# correos reales necesitamos configurar un servidor SMTP.
EMAIL_BACKEND = "usuarios.email_backend.EmailBackend"
#========================================================================
DEFAULT_FROM_EMAIL = "nombre@moviecali.local"


#MAILERS = {
#    "default": {
#        "BACKEND": "django.core.mail.backends.console.EmailBackend",
#    },
#}
