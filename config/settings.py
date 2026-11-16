import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# load_dotenv no pisa las variables que ya estén definidas en el entorno:
# si una variable existe en el sistema, esa tiene prioridad sobre el .env.
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

# Se corta el arranque con un mensaje claro en vez de dejar que Django
# falle más adelante con un error difícil de relacionar con el .env.
if not SECRET_KEY:
    raise ImproperlyConfigured("Falta configurar DJANGO_SECRET_KEY")

# DEBUG queda apagado salvo que la variable diga exactamente "true",
# así un .env incompleto nunca lo deja activado por accidente.
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

# DJANGO_ALLOWED_HOSTS llega como texto separado por comas
# (por ejemplo "localhost,127.0.0.1") y acá se convierte en lista.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    "https://localhost:8000",
]


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

# El orden importa: SessionMiddleware tiene que ir antes que
# AuthenticationMiddleware, porque el usuario autenticado se obtiene
# a partir de la sesión.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                # Agrega "user" y "perms" al contexto de todos los
                # templates, sin tener que pasarlos desde cada vista.
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


AUTH_USER_MODEL = "usuarios.Usuario"

# A dónde se manda a quien intenta entrar a una página protegida
# sin haber iniciado sesión.
LOGIN_URL = "usuarios:login"

# A dónde se va después de iniciar sesión cuando no se venía de una
# página protegida.
LOGIN_REDIRECT_URL = "inicio"

# No se define LOGOUT_REDIRECT_URL: el destino después de cerrar sesión
# se indica con next_page en la ruta "logout" de usuarios/urls.py.


# Backend propio: muestra los correos de recuperación en la consola sin
# cortar los enlaces en varias líneas. Es solo para desarrollo; para
# enviar correos reales hay que configurar un servidor SMTP.
EMAIL_BACKEND = "usuarios.email_backend.EmailBackend"
DEFAULT_FROM_EMAIL = "nombre@moviecali.local"
